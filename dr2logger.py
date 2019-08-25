import numpy as np
import os
import sys
import keyboard
import tkinter as tk
from tkinter import filedialog

import networking
import utils
import plots


debug = False
recording = False
keys_default_stop_recording = 'Shift+F1'
keys_stop_recording = keys_default_stop_recording
version_string = '(Version 1.2, 2019-08-25)'


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
    '''.format(version_string))

    udp_socket = networking.open_port(networking.port_default)

    session_collection = np.zeros((len(networking.fields), 0))
    last_receive_results = None
    end_program = False

    if not debug:
        recording = True
        print('Press "{}" to quit the current race and start the analysis'.format(keys_stop_recording))
    else:
        recording = False
        #npz_file = np.load('C:/Users/Philipp/Desktop/dr2_logger/m1_ar_3.npz')
        npz_file = np.load('C:/Users/pherl/Desktop/dr2_logger/evo6_po.npz')

        session_collection = npz_file['arr_0']

    while not end_program:
        while recording:

            # bind failed -> don't try to receive data
            if udp_socket is None:
                recording = False
                break

            receive_results = networking.receive(udp_socket)
            if accept_new_data(receive_results, last_receive_results, session_collection.shape[1]):
                sys.stdout.write('\rSamples {}, lap time: {}, speed: {} m/s, rpm {}'.format(
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

            if keyboard.is_pressed(keys_stop_recording):
                recording = False
                # utils.cls()
                print('\nRecording of race stopped. Collected {} data points.\n'.format(session_collection.shape[1]))

        print('\n'
              'Enter: \n'
              '"e" to exit the program\n'
              '"r" to resume the race\n'
              '"n" for the next race (delete data from current run)\n'
              '"a" for analysis\n'
              '"s" to save the current run\n'
              '"l" to load a saved run\n'
              '"p" to change the port\n'
              '"k" to change the stop recording key\n')

        if debug:
            command = 'a'
        else:
            command = input()
        if command == 'e':
            print('Ending...')
            end_program = True
        elif command == 'r':
            print('Press "q" to quit the current race and start the analysis')
            recording = True
        elif command == 'n':
            print('Prepare for next race...')
            print('Press "{}" to quit the current race and start the analysis'.format(keys_stop_recording))
            session_collection = np.zeros((len(networking.fields), 0))
            last_receive_results = None
            recording = True
        elif command == 'a':
            plots.plot_main(session_data=session_collection)
        elif command == 's':
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.asksaveasfilename(filetypes=(("numpy", "*.npz"),))
            if file_path is not None:
                utils.make_dir_for_file(file_path)
                np.savez_compressed(file_path, session_collection)
                print('Saved {} data points to {}'.format(session_collection.shape[1], file_path))
        elif command == 'l':
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename(filetypes=(("numpy", "*.npz"), ("all files", "*.*")))
            if file_path is not None and os.path.isfile(file_path):
                npz_file = np.load(file_path)
                session_collection = npz_file['arr_0']
                print('Loaded {} data points from {}'.format(session_collection.shape[1], file_path))
        elif command == 'p':
            udp_socket = networking.open_port(networking.get_port())
        elif command == 'k':
            try:
                key_str = input('Enter key-string (default "{}"): '.format(keys_default_stop_recording))
                c = keyboard.key_to_scan_codes(key_str)  # trigger error if invalid and catch below
                keys_stop_recording = key_str
            except ValueError as e:
                print('Invalid key-string: "{}"'.format(key_str))
        else:
            print('Unknown command: {}'.format(command))

