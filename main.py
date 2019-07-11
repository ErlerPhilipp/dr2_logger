import socket
import numpy as np
import struct
import os
import sys
import keyboard
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import tkinter as tk
from tkinter import filedialog
import math

DATA_DICT = {
    'run_time': 0,
    'lap_time': 1,
    'distance': 2,
    'unknown_0': 3,
    'pos_x': 4,
    'pos_y': 5,
    'pos_z': 6,
    'speed_ms': 7,
    'unknown_2': 8,
    'unknown_3': 9,
    'unknown_4': 10,
    'unknown_5': 11,
    'unknown_6': 12,
    'unknown_7': 13,
    'unknown_8': 14,
    'unknown_9': 15,
    'unknown_10': 16,
    'susp_rl': 17,
    'susp_rr': 18,
    'susp_fl': 19,
    'susp_fr': 20,
    'unknown_11': 21,
    'unknown_12': 22,
    'unknown_13': 23,
    'unknown_14': 24,
    'wsp_rl': 25,
    'wsp_rr': 26,
    'wsp_fl': 27,
    'wsp_fr': 28,
    'throttle': 29,
    'steering': 30,
    'brakes': 31,
    'clutch': 32,
    'gear': 33,
    'g_force_x': 34,
    'g_force_y': 35,
    'current_lap': 36,
    'rpm': 37,
}


def cls():
    print('\n' * 1000)  # for pycharm
    os.system('cls' if os.name == 'nt' else 'clear')


def bit_stream_to_float32(data, pos):

    value = struct.unpack('f', data[pos:pos+4])
    return value[0]


def receive(data):

    run_time = bit_stream_to_float32(data, 0)
    lap_time = bit_stream_to_float32(data, 4)
    distance = max(bit_stream_to_float32(data, 8), 0)
    unknown_0 = bit_stream_to_float32(data, 12)
    pos_x = bit_stream_to_float32(data, 16)
    pos_y = bit_stream_to_float32(data, 20)
    pos_z = bit_stream_to_float32(data, 24)
    speed_ms = bit_stream_to_float32(data, 28)  # * 3.6  # * 3.6 for Km/h
    unknown_2 = bit_stream_to_float32(data, 32)
    unknown_3 = bit_stream_to_float32(data, 36)
    unknown_4 = bit_stream_to_float32(data, 40)
    unknown_5 = bit_stream_to_float32(data, 44)
    unknown_6 = bit_stream_to_float32(data, 48)
    unknown_7 = bit_stream_to_float32(data, 52)
    unknown_8 = bit_stream_to_float32(data, 56)
    unknown_9 = bit_stream_to_float32(data, 60)
    unknown_10 = bit_stream_to_float32(data, 64)
    susp_rl = bit_stream_to_float32(data, 68)  # Suspension travel aft left
    susp_rr = bit_stream_to_float32(data, 72)  # Suspension travel aft right
    susp_fl = bit_stream_to_float32(data, 76)  # Suspension travel fwd left
    susp_fr = bit_stream_to_float32(data, 80)  # Suspension travel fwd right
    unknown_11 = bit_stream_to_float32(data, 84)
    unknown_12 = bit_stream_to_float32(data, 88)
    unknown_13 = bit_stream_to_float32(data, 92)
    unknown_14 = bit_stream_to_float32(data, 96)
    wsp_rl = bit_stream_to_float32(data, 100)  # Wheel speed aft left
    wsp_rr = bit_stream_to_float32(data, 104)  # Wheel speed aft right
    wsp_fl = bit_stream_to_float32(data, 108)  # Wheel speed fwd left
    wsp_fr = bit_stream_to_float32(data, 112)  # Wheel speed fwd right
    throttle = bit_stream_to_float32(data, 116)  # Throttle 0-1
    steering = bit_stream_to_float32(data, 120)
    brakes = bit_stream_to_float32(data, 124)  # Brakes 0-1
    clutch = bit_stream_to_float32(data, 128)  # Clutch 0-1
    gear = bit_stream_to_float32(data, 132)  # Gear, neutral = 0
    g_force_x = bit_stream_to_float32(data, 136)
    g_force_y = bit_stream_to_float32(data, 140)
    current_lap = bit_stream_to_float32(data, 144)  # Current lap, starts at 0
    rpm = bit_stream_to_float32(data, 148) * 10  # RPM, requires * 10 for realistic values

    return np.array([
        run_time, lap_time, distance, unknown_0, pos_x, pos_y, pos_z, speed_ms, unknown_2, unknown_3, unknown_4,
        unknown_5, unknown_6, unknown_7, unknown_8, unknown_9, unknown_10, susp_rl, susp_rr, susp_fl, susp_fr,
        unknown_11, unknown_12, unknown_13, unknown_14, wsp_rl, wsp_rr, wsp_fl, wsp_fr,
        throttle, steering, brakes, clutch, gear, g_force_x, g_force_y, current_lap, rpm])


def get_port():

    try:
        port_str = input('Enter port (default 10001): ')
        if port_str is None or port_str == '':
            return 10001
        else:
            port_int = int(port_str)
            return port_int
    except ValueError as e:
        return 10001


def make_dir_for_file(file):
    file_dir = os.path.dirname(file)
    if file_dir != '':
        if not os.path.exists(file_dir):
            try:
                os.makedirs(os.path.dirname(file))
            except OSError as exc: # Guard against race condition
                raise


def open_port(port):

    UDP_IP = "127.0.0.1"
    UDP_PORT = port
    udp_socket = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    udp_socket.bind((UDP_IP, UDP_PORT))
    udp_socket.settimeout(0.01)
    return udp_socket


if __name__== "__main__":

    print('Dirt Rally 2.0 Race Logger by Philipp Erler')

    udp_socket = open_port(10001)

    session_collection = np.zeros((len(DATA_DICT), 0))
    last_receive_results = None
    recording = True
    end_program = False

    print('Press "q" to quit the current race and start the analysis')

    while not end_program:
        while recording:
            try:
                data, addr = udp_socket.recvfrom(1024)  # buffer size is 1024 bytes
                new_data = True
            except socket.timeout as e:
                new_data = False

            if new_data:
                receive_results = receive(data)
                if (receive_results != last_receive_results).any():
                    if (receive_results[DATA_DICT['pos_x']] != 0.0 or
                            receive_results[DATA_DICT['pos_y']] != 0.0 or
                            receive_results[DATA_DICT['pos_z']] != 0.0) and \
                            receive_results[DATA_DICT['lap_time']] != 0.0:

                        sys.stdout.write('\rLap time: {}, speed: {} m/s, rpm {}'.format(
                            receive_results[DATA_DICT['lap_time']],
                            receive_results[DATA_DICT['speed_ms']],
                            receive_results[DATA_DICT['rpm']]) + ' '*20)
                        sys.stdout.flush()

                        receive_results = np.expand_dims(receive_results, 1)
                        if session_collection.size == 0:
                            session_collection = receive_results
                        else:
                            session_collection = np.append(session_collection, receive_results, axis=1)

            if keyboard.is_pressed('q'):
                recording = False
                cls()
                print('Recording of race stopped. Collected {} data points.'.format(session_collection.shape[1]))

        print('Press: \n'
              '"e" to exit the program\n'
              '"r" to resume the race\n'
              '"n" for the next race\n'
              '"a" for analysis\n'
              '"s" to save the current run\n'
              '"l" to load a saved run\n'
              '"p" to change the port\n')

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
            session_collection = np.zeros((len(DATA_DICT), 0))
            recording = True
        elif command == 'a':
            if session_collection.size > 0:
                gear_scatter_plot_3d = True
                gear_scatter_plot_2d = True
                rpm_gear_histogram_plot = True
                suspension_speed_scatter_plot = True

                # gather data from the collection
                session_collection_t = session_collection.transpose()
                x = [d[DATA_DICT['pos_x']] for d in session_collection_t]
                y = [d[DATA_DICT['pos_z']] for d in session_collection_t]
                z = [d[DATA_DICT['pos_y']] for d in session_collection_t]
                rpm = [d[DATA_DICT['rpm']] for d in session_collection_t]
                rpm_max = max(rpm)
                scale = 150.0
                rpm_normalized_scaled = [r / rpm_max * scale for r in rpm]
                data_gear = [d[DATA_DICT['gear']] for d in session_collection_t]
                gear_max = max(data_gear)
                gear_normalized_scaled = [g / rpm_max for g in data_gear]

                if gear_scatter_plot_3d:
                    x_min = min(x)
                    x_max = max(x)
                    x_middle = (x_max + x_min) * 0.5
                    y_min = min(y)
                    y_max = max(y)
                    y_middle = (y_max + y_min) * 0.5
                    z_min = min(z)
                    z_max = max(z)
                    z_middle = (z_max + z_min) * 0.5
                    diff = [x_max - x_min, y_max - y_min, z_max - z_min]
                    diff_max = max(diff)
                    fig = plt.figure()
                    ax = fig.add_subplot(111, projection='3d')
                    ax.scatter(x, y, z, marker='o', s=rpm_normalized_scaled, c=gear_normalized_scaled)
                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    ax.set_zlabel('Z')
                    ax.text(x[0], y[0], z[0], 'start')
                    ax.text(x[-1], y[-1], z[-1], 'finish')
                    ax.set_xlim(x_middle - diff_max * 0.6, x_middle + diff_max * 0.6)
                    ax.set_ylim(y_middle - diff_max * 0.6, y_middle + diff_max * 0.6)
                    ax.set_zlim(z_middle - diff_max * 0.6, z_middle + diff_max * 0.6)
                    plt.title('3D positions with gear as color')
                    plt.show()

                if gear_scatter_plot_2d:
                    x_min = min(x)
                    x_max = max(x)
                    x_middle = (x_max + x_min) * 0.5
                    y_min = min(y)
                    y_max = max(y)
                    y_middle = (y_max + y_min) * 0.5
                    diff = [x_max - x_min, y_max - y_min]
                    diff_max = max(diff)
                    fig = plt.figure()
                    ax = fig.add_subplot(111)
                    ax.scatter(x=x, y=y, c=gear_normalized_scaled)
                    ax.set_xlabel('X')
                    ax.set_ylabel('Y')
                    ax.set_xlim(x_middle - diff_max * 0.6, x_middle + diff_max * 0.6)
                    ax.set_ylim(y_middle - diff_max * 0.6, y_middle + diff_max * 0.6)
                    ax.text(x[0], y[0], 'start')
                    ax.text(x[-1], y[-1], 'finish')
                    plt.title('2D positions with gear as color')
                    plt.show()

                # rpm as histogram over gears
                if rpm_gear_histogram_plot:
                    range_gears = list(set(data_gear))
                    range_gears.sort()
                    range_gears = [g for g in range_gears if g > 0.0]
                    rpm_min = min(rpm)
                    rpm_max = max(rpm)

                    fig, a = plt.subplots(1, len(range_gears), sharex=True, sharey=True)
                    a = a.ravel()
                    for i, gear in enumerate(range_gears):
                        rpm_per_gear = [d[DATA_DICT['rpm']] for d in session_collection_t if
                                        d[DATA_DICT['gear']] == gear]

                        ax = a[i]
                        num_bins = 20
                        n, bins, patches = ax.hist(rpm_per_gear, num_bins, density=True,
                                                   facecolor='g')
                        ax.set_xlabel('RPM')
                        ax.set_ylabel('Prob')
                        ax.set_xlim(rpm_min, rpm_max)
                        ax.set_title('Gear {}'.format(gear))
                    plt.show()

                if suspension_speed_scatter_plot:
                    fig, ax = plt.subplots()
                    lap_time = [d[DATA_DICT['lap_time']] for d in session_collection_t]
                    susp_fl = [d[DATA_DICT['susp_fl']] for d in session_collection_t]
                    susp_fr = [d[DATA_DICT['susp_fr']] for d in session_collection_t]
                    susp_rl = [d[DATA_DICT['susp_rl']] for d in session_collection_t]
                    susp_rr = [d[DATA_DICT['susp_rr']] for d in session_collection_t]
                    susp_data = [susp_fl, susp_fr, susp_rl, susp_rr]
                    susp_max = np.max(susp_data)
                    susp_min = np.min(susp_data)
                    susp_diff = susp_max - susp_min

                    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
                              'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
                    labels = ['susp_fl', 'susp_fr', 'susp_rl', 'susp_rr']
                    for i, susp in enumerate(susp_data):
                        ax.scatter(x=lap_time, y=susp, c=colors[i], label=labels[i],
                                   alpha=0.25, edgecolors='none')
                    ax.legend()
                    ax.grid(True)
                    plt.ylim(susp_max + susp_diff * 0.1, susp_min - susp_diff * 0.1)  # invert y axis and pad
                    plt.title('Suspension over lap time scatter plot')
                    plt.show()
        elif command == 's':
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.asksaveasfilename(filetypes=(("numpy", "*.npz"),))
            if file_path is not None:
                make_dir_for_file(file_path)
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
            udp_socket = open_port(get_port())

