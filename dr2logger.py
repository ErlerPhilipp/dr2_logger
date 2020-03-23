import numpy as np
import os
import sys
import threading
import queue
# import time
import configparser

import networking
import utils
import plots
import dr2specific


debug = False
log_raw_data = False
version_string = '(Version 1.6, 2019-10-14)'

intro_text = '''
Dirt Rally 2.0 Race Logger {} by Philipp Erler
https://github.com/ErlerPhilipp/dr2_logger

Make sure, UDP data is enabled in the hardware_settings_config.xml 
Default: C:\\Users\\ [username] \\Documents\\My Games\\DiRT Rally 2.0\\hardwaresettings\\hardware_settings_config.xml
<motion_platform>
    <dbox enabled="false" />
    <udp enabled="true" extradata="3" ip="127.0.0.1" port="20777" delay="1" />
    <udp enabled="true" extradata="3" ip="127.0.0.1" port="10001" delay="1" />
    <custom_udp enabled="False" filename="packet_data.xml" ip="127.0.0.1" port="20777" delay="1" />
    <fanatec enabled="false" pedalVibrationScale="1.0" wheelVibrationScale="1.0" ledTrueForGearsFalseForSpeed="true" />
</motion_platform>
'''.format(version_string)

commands_hint = '''
Enter:
"e" to exit the program
"c" to clear the current run
"a" for analysis
"s" to save the current run
"l" to load a saved run
'''


def init_config(config):
    init_config_input_socket(config)
#    init_config_output_socket(config)
    init_config_session_path(config)


def init_config_input_socket(config):
    config['general']['ip_in'] = '127.0.0.1'
    config['general']['port_in'] = '20777'


# def init_config_output_socket(config):
#     # mirror the received datagrams to this port in order to enable other telemetry tools
#     config['general']['ip_out'] = '127.0.0.1'
#     config['general']['port_out'] = '10001'


def init_config_session_path(config):
    config['general']['session_path'] = './races_auto_save/'


# def forward_datagram(udp_socket, datagram, config):
#     # forward datagram to another socket
#     # not necessary atm because you can simply duplicate the entry in the DR2 settings file
#     try:
#         networking.send_datagram(udp_socket, datagram,
#                                  config['general']['ip_out'], int(config['general']['port_out']))
#     except ValueError:
#         print('Invalid output socket. Resetting...')
#         init_config_output_socket(config)
#         write_config(config)
#         networking.send_datagram(udp_socket, datagram,
#                                  config['general']['ip_out'], int(config['general']['port_out']))


def write_config(config):
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)


def read_config(config):
    settings_file_path = 'settings.ini'
    if os.path.isfile(settings_file_path):
        config.read(settings_file_path)
    else:
        config['general'] = {}
        init_config(config)
        write_config(config)


def add_input(message_queue):
    running = True
    while running:
        read_res = input()
        message_queue.put(read_res)
        if read_res == 'e':
            running = False


def print_current_state(state_str):
    import ctypes
    if state_str is not None:
        ctypes.windll.kernel32.SetConsoleTitleW(state_str)


def save_run(session_collection, config, automatic_name=False):
    # TODO: this will block the main thread and data from the port may be lost
    import tkinter as tk
    from tkinter import filedialog
    from datetime import datetime

    try:
        os.makedirs(config['general']['session_path'], exist_ok=True)
    except ValueError:
        print('Invalid session path. Resetting...')
        init_config_session_path(config)
        write_config(config)
        os.makedirs(config['general']['session_path'], exist_ok=True)

    # assemble default name
    last_sample = session_collection[:, -1]
    car_name = dr2specific.get_car_name_from_sample(last_sample)
    track_name = dr2specific.get_track_name_from_sample(last_sample)
    race_time = session_collection[networking.Fields.run_time.value, -1] - \
                session_collection[networking.Fields.run_time.value, 0]
    total_race_time = '{:.1f}'.format(race_time)
    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d %H_%M_%S')
    file_name = '{} - {} - {} - {}s.npz'.format(now_str, car_name, track_name, total_race_time)
    file_path = os.path.join(config['general']['session_path'], file_name)

    if not automatic_name:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            initialdir=config['general']['session_path'],
            initialfile=file_name,
            title='Save race log',
            filetypes=(("numpy", "*.npz"),))

    if file_path is not None and file_path != '' and file_path != '.npz':
        utils.make_dir_for_file(file_path)
        np.savez_compressed(file_path, session_collection)
        print('Saved {} data points to {}\n'.format(session_collection.shape[1], os.path.abspath(file_path)))


def load_run(config):
    # TODO: this will block the main thread and data from the port may be lost
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        initialdir=config['general']['session_path'],
        title='Load race log',
        filetypes=(("numpy", "*.npz"), ("all files", "*.*")))
    if file_path is not None and file_path != '':
        if os.path.isfile(file_path):
            npz_file = np.load(file_path)
            session_collection = npz_file['arr_0']
            print('Loaded {} data points from {}\n'.format(session_collection.shape[1], file_path))
            return session_collection
        else:
            print('"{}" is no valid file!\n'.format(file_path))
            return clear_session_collection()


def clear_session_collection():
    return np.zeros((len(networking.Fields), 0)), np.zeros((len(networking.Fields)))


def main():

    session_collection, first_sample = clear_session_collection()
    last_receive_results = None
    end_program = False
    new_state = dr2specific.GameState.race_not_running
    last_state = dr2specific.GameState.race_not_running
    config = configparser.ConfigParser()
    read_config(config)

    print(intro_text)
    print(commands_hint)

    udp_socket = networking.open_port(config['general']['ip_in'], int(config['general']['port_in']))
    if udp_socket is not None:
        print('Listening on socket {}\n'.format(udp_socket.getsockname()))
    else:
        print('Invalid input socket. Resetting...')
        init_config_input_socket(config)
        write_config(config)
        udp_socket = networking.open_port(config['general']['ip_in'], int(config['general']['port_in']))
        print('Listening on socket {}\n'.format(udp_socket.getsockname()))

    message_queue = queue.Queue()
    input_thread = threading.Thread(target=add_input, args=(message_queue,))
    input_thread.daemon = True
    input_thread.start()
    raw_data, _ = clear_session_collection() if log_raw_data else (None, None)

    if debug:  # start with plots
        # npz_file = np.load('C:/Users/Philipp/Desktop/dr2_logger/m1_ar_3.npz')
        # npz_file = np.load('C:/Users/pherl/Desktop/dr2logger_1_6/races_auto_save/2019-12-26 16_11_35 - Unknown car (0.0, 0.0, 0.0) - Verbundsring - 216.9s.npz')
        npz_file = np.load('C:/Users/pherl/Desktop/2020-03-18 21_22_14 - Peugeot 208 R2 - Kakaristo - 451.7s.npz')
        session_collection = npz_file['arr_0']
        message_queue.put('a')
    else:  # start with recording
        pass

    while not end_program:

        receive_results, datagram = networking.receive(udp_socket)
        # forward_datagram(udp_socket=udp_socket, datagram=datagram, config=config)

        if receive_results is not None:
            if log_raw_data:
                receive_results_raw = np.expand_dims(receive_results, 1)
                if raw_data.size == 0:
                    raw_data = receive_results_raw
                else:
                    raw_data = np.append(session_collection, receive_results_raw, axis=1)

            new_state = dr2specific.get_game_state(receive_results, last_receive_results)
            last_sample = receive_results
            print_current_state(dr2specific.get_game_state_str(
                new_state, last_sample, session_collection.shape[1]))
            has_new_data = dr2specific.accept_new_data(new_state)
            if has_new_data:
                if session_collection.size == 0:
                    session_collection = np.expand_dims(receive_results, 1)
                else:
                    session_collection = np.append(session_collection, np.expand_dims(receive_results, 1), axis=1)
        else:
            new_state = last_state
            has_new_data = False

        while not message_queue.empty():
            command = message_queue.get()

            if command == 'e':
                print('Exit...\n')
                end_program = True
            elif command == 'c':
                print('Cleared {} data points\n'.format(session_collection.shape[1]))
                session_collection, first_sample = clear_session_collection()
                last_receive_results = None
            elif command == 'a':
                print('Plotting {} data points\n'.format(session_collection.shape[1]))
                if debug:
                    plots.plot_main(session_data=session_collection)
                else:
                    try:
                        plots.plot_main(session_data=session_collection)
                    except Exception:
                        print('Error during plot: {}'.format(sys.exc_info()))
            elif command == 's':
                save_run(session_collection, config)
            elif command == 'l':
                loaded_session_collection = load_run(config)
                if loaded_session_collection is not None and loaded_session_collection.size > 0:
                    session_collection = loaded_session_collection
                    last_sample = session_collection[:, -1]
                    print_current_state(dr2specific.get_game_state_str(
                        new_state, last_sample, session_collection.shape[1]))
            elif command == '':
                pass  # just ignore empty inputs
            else:
                print('Unknown command: "{}"'.format(command))
                print(commands_hint + '\n')

        # simply ignore state changes through duplicates
        if new_state == dr2specific.GameState.ignore_package:
            new_state = last_state

        if debug and last_state != new_state:
            print('State changed from {} to {}'.format(last_state, new_state))

        if last_state == dr2specific.GameState.race_running and \
                new_state == dr2specific.GameState.race_not_running:
            print('Race finished. ')
            save_run(session_collection, config, automatic_name=True)

            if log_raw_data:
                save_run(raw_data, config, automatic_name=False)
        elif last_state == dr2specific.GameState.race_not_running and \
                new_state == dr2specific.GameState.race_running:
            print('Race starting')
            if session_collection.shape[1] > 10:  # should only be less than 100 at the first race after startup
                print('Cleared {} data points'.format(session_collection.shape[1]))
            session_collection, first_sample = clear_session_collection()

            # debug, data mining
            max_rpm = receive_results[networking.Fields.max_rpm.value]
            idle_rpm = receive_results[networking.Fields.idle_rpm.value]
            max_gears = receive_results[networking.Fields.max_gears.value]
            car_name = dr2specific.get_car_name(max_rpm, idle_rpm, max_gears)
            if car_name.startswith('Unknown'):
                with open('unknown cars.txt', 'a+') as f:
                    f.write('[{}, {}, {}, \'Unknown car\'],\n'.format(max_rpm, idle_rpm, max_gears))

            track_length = receive_results[networking.Fields.track_length.value]
            pos_z = receive_results[networking.Fields.pos_z.value]
            track_name = dr2specific.get_track_name(track_length, pos_z)
            if track_name.startswith('Unknown'):
                with open('unknown tracks.txt', 'a+') as f:
                    f.write('[{}, {}, \'Unknown track\'],\n'.format(track_length, pos_z))

        last_state = new_state
        if has_new_data:
            last_receive_results = receive_results.copy()

    input_thread.join()
    udp_socket.close()


if __name__ == "__main__":
    main()
