import numpy as np
import os
import sys
import threading
import queue
#import time
import configparser

import networking
import utils
import plots
import dr2specific


debug = False
recording = False
log_raw_data = False
version_string = '(Version 1.5, 2019-10-1)'

intro_text = '''
Dirt Rally 2.0 Race Logger {} by Philipp Erler
https://github.com/ErlerPhilipp/dr2_logger

Make sure, UDP data is enabled in the hardware_settings_config.xml 
Default: C:\\Users\\ [username] \\Documents\\My Games\\DiRT Rally 2.0\\hardwaresettings\\hardware_settings_config.xml
<motion_platform>
    <dbox enabled="false" />
    <udp enabled="True" extradata="2" ip="127.0.0.1" port="20777" delay="1" />
    <custom_udp enabled="false" filename="packet_data.xml" ip="127.0.0.1" port="20777" delay="1" />
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
    init_config_output_socket(config)
    init_config_session_path(config)


def init_config_input_socket(config):
    config['general']['ip_in'] = '127.0.0.1'
    config['general']['port_in'] = '20777'


def init_config_output_socket(config):
    # mirror the received datagrams to this port in order to enable other telemetry tools
    config['general']['ip_out'] = '127.0.0.1'
    config['general']['port_out'] = '10001'


def init_config_session_path(config):
    config['general']['session_path'] = './races_auto_save/'


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

    if automatic_name:
        total_race_time = '{:.1f}'.format(np.max(session_collection[networking.fields.lap_time.value]))
        now = datetime.now()
        file_name = now.strftime('%Y-%m-%d %H_%M_%S') + ' {}s.npz'.format(total_race_time)
        try:
            os.makedirs(config['general']['session_path'], exist_ok=True)
        except ValueError:
            print('Invalid session path. Resetting...')
            init_config_session_path(config)
            write_config(config)
            os.makedirs(config['general']['session_path'], exist_ok=True)
        file_path = os.path.join(config['general']['session_path'], file_name)
    else:
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(filetypes=(("numpy", "*.npz"),))
    if file_path is not None and file_path != '' and file_path != '.npz':
        utils.make_dir_for_file(file_path)
        np.savez_compressed(file_path, session_collection)
        print('Saved {} data points to {}\n'.format(session_collection.shape[1], os.path.abspath(file_path)))


def load_run():
    # TODO: this will block the main thread and data from the port may be lost
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=(("numpy", "*.npz"), ("all files", "*.*")))
    if file_path is not None and file_path != '':
        if os.path.isfile(file_path):
            npz_file = np.load(file_path)
            session_collection = npz_file['arr_0']
            print('Loaded {} data points from {}\n'.format(session_collection.shape[1], file_path))
            return session_collection
        else:
            print('"{}" is no valid file!\n'.format(file_path))
            return clear_session_collection()


def set_up_port(command, udp_socket, port_default):
    if command == 'p':
        print('You must specify a port number with the command. For example "p 20777".\n')

    elif command[:2] == 'p ':
        port_no = command.split(' ')[1]
        port_no_int = networking.parse_port(port_no, port_default)
        if udp_socket.getsockname()[1] == port_no_int:
            print('Already listening on socket {}\n'.format(udp_socket.getsockname()))
        else:
            udp_socket = networking.open_port(port_no_int)
            if udp_socket is not None:
                print('Listening on socket {}\n'.format(udp_socket.getsockname()))
    else:
        print('Unknown port parameter: "{}"'.format(command))


def clear_session_collection():
    return np.zeros((len(networking.fields), 0))


def main():

    session_collection = clear_session_collection()
    last_receive_results = None
    end_program = False
    new_state = dr2specific.GameState.error
    last_state = dr2specific.GameState.error
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
    raw_data = clear_session_collection() if log_raw_data else None

    if debug:  # start with plots
        # npz_file = np.load('C:/Users/Philipp/Desktop/dr2_logger/m1_ar_3.npz')
        npz_file = np.load('C:/Users/pherl/Desktop/dr2_logger/evo6_po.npz')
        session_collection = npz_file['arr_0']
        message_queue.put('a')
    else:  # start with recording
        pass

    while not end_program:

        receive_results, datagram = networking.receive(udp_socket)
        try:
            networking.send_datagram(udp_socket, datagram,
                                     config['general']['ip_out'], int(config['general']['port_out']))
        except ValueError:
            print('Invalid output socket. Resetting...')
            init_config_output_socket(config)
            write_config(config)
            networking.send_datagram(udp_socket, datagram,
                                     config['general']['ip_out'], int(config['general']['port_out']))

        if log_raw_data:
            receive_results_raw = np.expand_dims(receive_results, 1)
            if raw_data.size == 0:
                raw_data = receive_results_raw
            else:
                raw_data = np.append(session_collection, receive_results_raw, axis=1)

        new_state = dr2specific.get_game_state(receive_results, last_receive_results)
        print_current_state(dr2specific.get_game_state_str(new_state, receive_results, session_collection.shape[1]))
        has_new_data = dr2specific.accept_new_data(new_state)
        if has_new_data:
            if session_collection.size == 0:
                session_collection = np.expand_dims(receive_results, 1)
            else:
                session_collection = np.append(session_collection, np.expand_dims(receive_results, 1), axis=1)

        while not message_queue.empty():
            command = message_queue.get()

            if command == 'e':
                print('Exit...\n')
                end_program = True
            elif command == 'c':
                print('Cleared {} data points\n'.format(session_collection.shape[1]))
                session_collection = clear_session_collection()
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
                loaded_session_collection = load_run()
                if loaded_session_collection.size > 0:
                    session_collection = loaded_session_collection
            elif command == '':
                pass  # just ignore empty inputs
            else:
                print('Unknown command: "{}"'.format(command))
                print(commands_hint + '\n')

        # simply ignore state changes through duplicates
        if new_state == dr2specific.GameState.duplicate_package or new_state == dr2specific.GameState.error:
            new_state = last_state

        if debug and last_state != new_state:
            print('State changed from {} to {}'.format(last_state, new_state))

        if last_state == dr2specific.GameState.race_running and \
                new_state == dr2specific.GameState.race_finished_or_service_area:
            print('Race finished. ')
            save_run(session_collection, config, automatic_name=True)

            if log_raw_data:
                save_run(raw_data, config, automatic_name=False)
        elif last_state == dr2specific.GameState.race_start and \
                new_state == dr2specific.GameState.race_running:
            print('Race starting. \nCleared {} data points\n'.format(session_collection.shape[1]))
            session_collection = clear_session_collection()
        elif last_state == dr2specific.GameState.race_finished_or_service_area and \
                new_state == dr2specific.GameState.race_running:
            save_run(session_collection, config, automatic_name=True)
            session_collection = clear_session_collection()
            print('Race finished. Race starting. \nCleared {} data points\n'.format(session_collection.shape[1]))

        last_state = new_state
        if has_new_data:
            last_receive_results = receive_results.copy()
        #else:
        #    time.sleep(0.005)  # 5 ms (+- 15 ms)

    input_thread.join()
    udp_socket.close()


if __name__ == "__main__":
    main()
