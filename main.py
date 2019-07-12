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

# https://docs.google.com/spreadsheets/d/1eA518KHFowYw7tSMa-NxIFYpiWe5JXgVVQ_IMs7BVW0/edit?usp=drivesdk
DATA_DICT = {
    'run_time':            0,
    'lap_time':            1,
    'distance':            2,
    'progress':            3,
    'pos_x':               4,
    'pos_y':               5,
    'pos_z':               6,
    'speed_ms':            7,
    'vel_x':               8,
    'vel_y':               9,
    'vel_z':               10,
    'roll_x':              11,
    'roll_y':              12,
    'roll_z':              13,
    'pitch_x':             14,
    'pitch_y':             15,
    'pitch_z':             16,
    'susp_rl':             17,
    'susp_rr':             18,
    'susp_fl':             19,
    'susp_fr':             20,
    'susp_vel_rl':         21,
    'susp_vel_rr':         22,
    'susp_vel_fl':         23,
    'susp_vel_fr':         24,
    'wsp_rl':              25,
    'wsp_rr':              26,
    'wsp_fl':              27,
    'wsp_fr':              28,
    'throttle':            29,
    'steering':            30,
    'brakes':              31,
    'clutch':              32,
    'gear':                33,
    'g_force_x':           34,
    'g_force_y':           35,
    'current_lap':         36,
    'rpm':                 37,
    'sli_pro_support':     38,
    'car_pos':             39,
    'kers_level':          40,
    'kers_max_level':      41,
    'drs':                 42,
    'traction_control':    43,
    'anti_lock_brakes':    44,
    'fuel_in_tank':        45,
    'fuel_capacity':       46,
    'in_pit':              47,
    'sector':              48,
    'sector_1_time':       49,
    'sector_2_time':       50,
    'brakes_temp':         51,
    'wheels_pressure_psi': 52,
    'team_info':           53,
    'total_laps':          54,
    'track_size':          55,
    'last_lap_time':       56,
    'max_rpm':             57,
    'idle_rpm':            58,
    'max_gears':           59,
    'session_type':        60,
    'drs_allowed':         61,
    'track_number':        62,
    'vehicle_fia_flags':   63,
    'unknown_0':           64,
    'unknown_1':           65,
}


def cls():
    print('\n' * 1000)  # for pycharm
    os.system('cls' if os.name == 'nt' else 'clear')


def bit_stream_to_float32(data, pos):
    try:
        value = struct.unpack('f', data[pos:pos+4])
    except ValueError as e:
        value = 0
        print('Failed to get data item at pos {}'.format(pos))
    return value[0]


def receive(data):

    run_time = bit_stream_to_float32(data, 0)
    lap_time = bit_stream_to_float32(data, 4)
    distance = max(bit_stream_to_float32(data, 8), 0)
    progress = bit_stream_to_float32(data, 12)  # 0-1
    pos_x = bit_stream_to_float32(data, 16)
    pos_y = bit_stream_to_float32(data, 20)
    pos_z = bit_stream_to_float32(data, 24)
    speed_ms = bit_stream_to_float32(data, 28)  # * 3.6  # * 3.6 for Km/h
    vel_x = bit_stream_to_float32(data, 32)  # velocity in world space
    vel_y = bit_stream_to_float32(data, 36)  # velocity in world space
    vel_z = bit_stream_to_float32(data, 40)  # velocity in world space
    roll_x = bit_stream_to_float32(data, 44)
    roll_y = bit_stream_to_float32(data, 48)
    roll_z = bit_stream_to_float32(data, 52)
    pitch_x = bit_stream_to_float32(data, 56)
    pitch_y = bit_stream_to_float32(data, 60)
    pitch_z = bit_stream_to_float32(data, 64)
    susp_rl = bit_stream_to_float32(data, 68)  # Suspension travel aft left
    susp_rr = bit_stream_to_float32(data, 72)  # Suspension travel aft right
    susp_fl = bit_stream_to_float32(data, 76)  # Suspension travel fwd left
    susp_fr = bit_stream_to_float32(data, 80)  # Suspension travel fwd right
    susp_vel_rl = bit_stream_to_float32(data, 84)
    susp_vel_rr = bit_stream_to_float32(data, 88)
    susp_vel_fl = bit_stream_to_float32(data, 92)
    susp_vel_fr = bit_stream_to_float32(data, 96)
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
    sli_pro_support = bit_stream_to_float32(data, 152)
    car_pos = bit_stream_to_float32(data, 156)
    kers_level = bit_stream_to_float32(data, 160)
    kers_max_level = bit_stream_to_float32(data, 164)
    drs = bit_stream_to_float32(data, 168)
    traction_control = bit_stream_to_float32(data, 172)
    anti_lock_brakes = bit_stream_to_float32(data, 176)
    fuel_in_tank = bit_stream_to_float32(data, 180)
    fuel_capacity = bit_stream_to_float32(data, 184)
    in_pit = bit_stream_to_float32(data, 188)
    sector = bit_stream_to_float32(data, 192)
    sector_1_time = bit_stream_to_float32(data, 196)
    sector_2_time = bit_stream_to_float32(data, 200)
    brakes_temp = bit_stream_to_float32(data, 204)
    wheels_pressure_psi = bit_stream_to_float32(data, 208)
    team_info = bit_stream_to_float32(data, 212)
    total_laps = bit_stream_to_float32(data, 216)
    track_size = bit_stream_to_float32(data, 220)
    last_lap_time = bit_stream_to_float32(data, 224)
    max_rpm = bit_stream_to_float32(data, 228)
    idle_rpm = bit_stream_to_float32(data, 232)
    max_gears = bit_stream_to_float32(data, 236)
    session_type = bit_stream_to_float32(data, 240)
    drs_allowed = bit_stream_to_float32(data, 244)
    track_number = bit_stream_to_float32(data, 248)
    vehicle_fia_flags = bit_stream_to_float32(data, 252)
    unknown_0 = bit_stream_to_float32(data, 256)
    unknown_1 = bit_stream_to_float32(data, 260)

    return np.array([
        run_time, lap_time, distance, progress, pos_x, pos_y, pos_z, speed_ms, vel_x, vel_y, vel_z,
        roll_x, roll_y, roll_z, pitch_x, pitch_y, pitch_z, susp_rl, susp_rr, susp_fl, susp_fr,
        susp_vel_rl, susp_vel_rr, susp_vel_fl, susp_vel_fr, wsp_rl, wsp_rr, wsp_fl, wsp_fr,
        throttle, steering, brakes, clutch, gear, g_force_x, g_force_y, current_lap, rpm, sli_pro_support, car_pos,
        kers_level, kers_max_level, drs, traction_control, anti_lock_brakes, fuel_in_tank, fuel_capacity, in_pit,
        sector, sector_1_time, sector_2_time, brakes_temp, wheels_pressure_psi, team_info, total_laps, track_size,
        last_lap_time, max_rpm, idle_rpm, max_gears, session_type, drs_allowed, track_number, vehicle_fia_flags,
        unknown_0, unknown_1
    ])


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
                gear_scatter_plot_3d = False
                gear_scatter_plot_2d = False
                rpm_gear_histogram_plot = True
                suspension_over_time = True
                height_over_dist = False

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

                if suspension_over_time:
                    lap_time = [d[DATA_DICT['lap_time']] for d in session_collection_t]
                    susp_fl = [d[DATA_DICT['susp_fl']] for d in session_collection_t]
                    susp_fr = [d[DATA_DICT['susp_fr']] for d in session_collection_t]
                    susp_rl = [d[DATA_DICT['susp_rl']] for d in session_collection_t]
                    susp_rr = [d[DATA_DICT['susp_rr']] for d in session_collection_t]
                    susp_data = [susp_fl, susp_fr, susp_rl, susp_rr]
                    susp_max = np.max(susp_data)
                    susp_min = np.min(susp_data)
                    susp_diff = susp_max - susp_min

                    #fig, ax = plt.subplots()
                    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
                              'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
                    labels = ['susp_fl', 'susp_fr', 'susp_rl', 'susp_rr']
                    for i, susp in enumerate(susp_data):
                        plt.plot(lap_time, susp, alpha=0.5)
                    plt.legend(labels)
                    plt.grid(True)
                    plt.ylim(susp_max + susp_diff * 0.1, susp_min - susp_diff * 0.1)  # invert y axis and pad
                    plt.title('Suspension over lap time')
                    plt.show()

                if height_over_dist:
                    distance = [d[DATA_DICT['distance']] for d in session_collection_t]
                    height = [d[DATA_DICT['pos_y']] for d in session_collection_t]
                    fig, ax = plt.subplots()
                    ax.plot(distance, height, label='height')
                    ax.set(xlabel='distance (m)', ylabel='height (m)',
                           title='Height over time')
                    ax.grid()
                    # ax.legend()
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

