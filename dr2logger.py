import numpy as np
import os
import sys
import threading
import queue
import time

import networking
import utils
import plots
import dr2specific


debug = False
recording = False
log_raw_data = False
version_string = '(Version 1.4, 2019-09-07)'
default_session_path = './races_auto_save/'


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


def save_run(session_collection, automatic_name=False):
    # TODO: this will block the main thread and data from the port may be lost
    import tkinter as tk
    from tkinter import filedialog
    from datetime import datetime

    if automatic_name:
        total_race_time = '{:.1f}'.format(session_collection[networking.fields.lap_time.value][-1])
        now = datetime.now()
        file_name = now.strftime('%Y-%m-%d %H_%M_%S') + ' {}s.npz'.format(total_race_time)
        os.makedirs(default_session_path, exist_ok=True)
        file_path = os.path.join(default_session_path, file_name)
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


def set_up_port(command, udp_socket):
    if command == 'p':
        print('You must specify a port number with the command. For example "p 20777".\n')

    elif command[:2] == 'p ':
        port_no = command.split(' ')[1]
        port_no_int = networking.parse_port(port_no)
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

    udp_socket = None
    session_collection = clear_session_collection()
    last_receive_results = None
    end_program = False
    new_state = dr2specific.GameState.error
    last_state = dr2specific.GameState.error

    print('''
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
'''.format(version_string))

    commands_hint = '''
Enter:
"e" to exit the program
"c" to clear the current run
"a" for analysis
"s" to save the current run
"l" to load a saved run
"p [port]" to change the port, e.g. 'p 20777'
'''
    print(commands_hint)

    udp_socket = networking.open_port(networking.port_default)
    if udp_socket is not None:
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

        # socket bind failed -> don't try to receive data
        receive_results = networking.receive(udp_socket) if udp_socket is not None else None

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
            receive_results = np.expand_dims(receive_results, 1)
            if session_collection.size == 0:
                session_collection = receive_results
            else:
                session_collection = np.append(session_collection, receive_results, axis=1)

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
                #try:
                plots.plot_main(session_data=session_collection)
                #except:
                #    print('Error during plot: {}'.format(sys.exc_info()))
            elif command == 's':
                save_run(session_collection)
            elif command == 'l':
                loaded_session_collection = load_run()
                if loaded_session_collection.size > 0:
                    session_collection = loaded_session_collection
            elif len(command) > 0 and command[0] == 'p':
                set_up_port(command, udp_socket)
            else:
                print('Unknown command: "{}"\n'.format(command))
                print(commands_hint + '\n')

        # simply ignore state changes through duplicates
        if new_state == dr2specific.GameState.duplicate_package or new_state == dr2specific.GameState.error:
            new_state = last_state

        if last_state != new_state:
            print('State changed from {} to {}'.format(last_state, new_state))

        if last_state == dr2specific.GameState.race_running and \
                new_state == dr2specific.GameState.race_finished_or_service_area:
            print('Race finished. ')
            save_run(session_collection, automatic_name=True)

            if log_raw_data:
                save_run(raw_data, automatic_name=False)
        if last_state == dr2specific.GameState.race_start and new_state == dr2specific.GameState.race_running:
            print('Race starting. Cleared {} data points\n'.format(session_collection.shape[1]))
            session_collection = clear_session_collection()

        last_state = new_state
        if has_new_data:
            last_receive_results = receive_results.copy()
        #else:
        #    time.sleep(0.005)  # 5 ms (+- 15 ms)

    input_thread.join()
    udp_socket.close()


if __name__ == "__main__":
    main()
