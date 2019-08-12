import numpy as np
import os
import sys
import keyboard
import time
import tkinter as tk
from tkinter import filedialog
import math

import networking
import utils
import plots


debug = False


def accept_new_data(receive_results, last_receive_results):
    # no data, error in receive?
    if receive_results is None:
        return False

    # same data again -> game is probably paused
    if np.any(receive_results == last_receive_results):
        return False

    # car is at origin -> probably in service area
    if receive_results[networking.fields['pos_x']] == 0.0 and \
        receive_results[networking.fields['pos_y']] == 0.0 and \
        receive_results[networking.fields['pos_z']] == 0.0:
        return False

    # race has not yet started
    if receive_results[networking.fields['lap_time']] == 0.0:
        return False

    # new race time is less than the previous -> race has ended and car is in service area or next race
    if last_receive_results is not None and \
            receive_results[networking.fields['lap_time']] < last_receive_results[networking.fields['lap_time']]:
        return False

    return True


if __name__ == "__main__":

    print('Dirt Rally 2.0 Race Logger by Philipp Erler')

    udp_socket = networking.open_port(10001)

    session_collection = np.zeros((len(networking.fields), 0))
    last_receive_results = None
    end_program = False

    if not debug:
        recording = True
        print('Press "q" to quit the current race and start the analysis')
    else:
        recording = False
        npz_file = np.load('C:/Users/Philipp/Desktop/dr2_logger/m1_ar_3.npz')
        #npz_file = np.load('C:/Users/pherl/Desktop/dr2_logger/camaro_nz.npz')

        session_collection = npz_file['arr_0']

    while not end_program:
        while recording:
            receive_results = networking.receive(udp_socket)
            if accept_new_data(receive_results, last_receive_results):
                sys.stdout.write('\rLap time: {}, speed: {} m/s, rpm {}'.format(
                    receive_results[networking.fields['lap_time']],
                    receive_results[networking.fields['speed_ms']],
                    receive_results[networking.fields['rpm']]) + ' '*20)
                sys.stdout.flush()

                receive_results = np.expand_dims(receive_results, 1)
                if session_collection.size == 0:
                    session_collection = receive_results
                else:
                    session_collection = np.append(session_collection, receive_results, axis=1)

                last_receive_results = receive_results

            if keyboard.is_pressed('q'):
                recording = False
                utils.cls()
                print('\nRecording of race stopped. Collected {} data points.'.format(session_collection.shape[1]))

        print('Press: \n'
              '"e" to exit the program\n'
              '"r" to resume the race\n'
              '"n" for the next race\n'
              '"a" for analysis\n'
              '"s" to save the current run\n'
              '"l" to load a saved run\n'
              '"p" to change the port\n')

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
            print('Press "q" to quit the current race and start the analysis')
            session_collection = np.zeros((len(networking.fields), 0))
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

