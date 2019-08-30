import numpy as np
import os
import sys
import tkinter as tk
from tkinter import filedialog
import threading
import queue
import time

import networking
import utils
import plots


debug = False
recording = False
version_string = '(Version 1.3, 2019-08-25)'


def add_input(message_queue):
    running = True
    while running:
        read_res = input()
        message_queue.put(read_res)
        if read_res == 'e':
            running = False


def accept_new_data(receive_results, last_receive_results, num_samples):
    # no data, error in receive?
    if receive_results is None:
        return False
    elif last_receive_results is None:
        return True

    # car is at origin -> probably in service area
    if receive_results[networking.fields['pos_x']] == 0.0 and \
        receive_results[networking.fields['pos_y']] == 0.0 and \
        receive_results[networking.fields['pos_z']] == 0.0:
        sys.stdout.write('\rSamples {}, lap time: {}, ignore bad data (in finish?)'.format(
            num_samples,
            receive_results[networking.fields['lap_time']]) + ' '*20)
        sys.stdout.flush()
        return False

    # race has not yet started
    if receive_results[networking.fields['lap_time']] == 0.0:
        sys.stdout.write('\rSamples {}, lap time: {}, ignore pre-race'.format(
            num_samples,
            receive_results[networking.fields['lap_time']]) + ' '*20)
        sys.stdout.flush()
        return False

    # new race time is less than the previous -> race has ended and car is in service area or next race
    if last_receive_results is not None and \
            receive_results[networking.fields['lap_time']] < last_receive_results[networking.fields['lap_time']]:
        sys.stdout.write('\rSamples {}, lap time: {}, ignore bad data (service area?)'.format(
            num_samples,
            receive_results[networking.fields['lap_time']]) + ' '*20)
        sys.stdout.flush()
        return False

    # same time again -> game is probably paused
    if last_receive_results is not None and \
            receive_results[networking.fields['lap_time']] == last_receive_results[networking.fields['lap_time']]:
        sys.stdout.write('\rSamples {}, lap time: {}, ignore old data'.format(
            num_samples,
            receive_results[networking.fields['lap_time']]) + ' '*20)
        sys.stdout.flush()
        return False

    return True


if __name__ == "__main__":

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

Enter:
"e" to exit the program
"c" to clear the current run
"a" for analysis
"s" to save the current run
"l" to load a saved run
"p" to change the port
    '''.format(version_string))

    udp_socket = networking.open_port(networking.port_default)

    session_collection = np.zeros((len(networking.fields), 0))
    last_receive_results = None
    end_program = False

    message_queue = queue.Queue()
    input_thread = threading.Thread(target=add_input, args=(message_queue,))
    input_thread.daemon = True
    input_thread.start()

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

        has_new_data = accept_new_data(receive_results, last_receive_results, session_collection.shape[1])
        if has_new_data:
            sys.stdout.write('\rSamples {:05d}, lap time: {:.1f}, speed: {:.1f} m/s, rpm {:5.1f}'.format(
                session_collection.shape[1],
                receive_results[networking.fields['lap_time']],
                receive_results[networking.fields['speed_ms']],
                receive_results[networking.fields['rpm']],) + ' '*20)
            sys.stdout.flush()

            receive_results = np.expand_dims(receive_results, 1)
            if session_collection.size == 0:
                session_collection = receive_results
            else:
                session_collection = np.append(session_collection, receive_results, axis=1)

            last_receive_results = receive_results.copy()

        while not message_queue.empty():
            command = message_queue.get()

            if command == 'e':
                print('Exit...\n')
                end_program = True
            elif command == 'c':
                print('Cleared {} data points\n'.format(session_collection.shape[1]))
                session_collection = np.zeros((len(networking.fields), 0))
                last_receive_results = None
            elif command == 'a':
                print('Plotting {} data points\n'.format(session_collection.shape[1]))
                plots.plot_main(session_data=session_collection)
            elif command == 's':  # TODO: this will block the main thread and data from the port may be lost
                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.asksaveasfilename(filetypes=(("numpy", "*.npz"),))
                if file_path is not None and file_path != '' and file_path != '.npz':
                    utils.make_dir_for_file(file_path)
                    np.savez_compressed(file_path, session_collection)
                    print('Saved {} data points to {}\n'.format(session_collection.shape[1], file_path))
            elif command == 'l':  # TODO: this will block the main thread and data from the port may be lost
                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.askopenfilename(filetypes=(("numpy", "*.npz"), ("all files", "*.*")))
                if file_path is not None and file_path != '':
                    if os.path.isfile(file_path):
                        npz_file = np.load(file_path)
                        session_collection = npz_file['arr_0']
                        print('Loaded {} data points from {}\n'.format(session_collection.shape[1], file_path))
                    else:
                        print('"{}" is no valid file!\n'.format(file_path))
            elif command == 'p':
                udp_socket = networking.open_port(networking.get_port())
            else:
                print('Unknown command: {}\n'.format(command))

        if not has_new_data:
            time.sleep(0.05)  # 5 ms (+- 15 ms)

    input_thread.join()
