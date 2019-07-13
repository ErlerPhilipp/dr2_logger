import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

import networking

colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
          'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']


def plot_gear_over_3d_pos(session_data):
    x = [d[networking.fields['pos_x']] for d in session_data]
    y = [d[networking.fields['pos_z']] for d in session_data]
    z = [d[networking.fields['pos_y']] for d in session_data]
    rpm = [d[networking.fields['rpm']] for d in session_data]
    rpm_max = max(rpm)
    scale = 150.0
    rpm_normalized_scaled = [r / rpm_max * scale for r in rpm]
    data_gear = [d[networking.fields['gear']] for d in session_data]
    gear_max = max(data_gear)
    gear_normalized_scaled = [g / gear_max for g in data_gear]

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
    plt.title('3D positions with gear as color, rpm')
    plt.set_cmap('plasma')
    plt.show()


def plot_gear_over_2d_pos(session_data):
    x = [d[networking.fields['pos_x']] for d in session_data]
    y = [d[networking.fields['pos_z']] for d in session_data]
    x_min = min(x)
    x_max = max(x)
    x_middle = (x_max + x_min) * 0.5
    y_min = min(y)
    y_max = max(y)
    y_middle = (y_max + y_min) * 0.5
    diff = [x_max - x_min, y_max - y_min]
    diff_max = max(diff)

    data_gear = [d[networking.fields['gear']] for d in session_data]
    range_gears = list(set(data_gear))
    range_gears.sort()

    fig = plt.figure('Gear at 2D positions')
    ax = fig.add_subplot(111)
    for i, g in enumerate(range_gears):
        pos_x = [d[networking.fields['pos_x']] for d in session_data if d[networking.fields['gear']] == g]
        pos_y = [d[networking.fields['pos_z']] for d in session_data if d[networking.fields['gear']] == g]
        ax.scatter(x=pos_x, y=pos_y, s=10, alpha=0.5, label='Gear {}'.format(str(g)))
    ax.set_xlim(x_middle - diff_max * 0.6, x_middle + diff_max * 0.6)
    ax.set_ylim(y_middle - diff_max * 0.6, y_middle + diff_max * 0.6)
    ax.legend()
    ax.text(x[0], y[0], 'start')
    ax.text(x[-1], y[-1], 'finish')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.title('Gear at 2D positions')
    plt.show()


def plot_rpm_histogram_per_gear(session_data):
    rpm = [d[networking.fields['rpm']] for d in session_data]
    data_gear = [d[networking.fields['gear']] for d in session_data]
    range_gears = list(set(data_gear))
    range_gears.sort()
    range_gears = [g for g in range_gears if g > 0.0]
    rpm_min = min(rpm)
    rpm_max = max(rpm)

    fig, a = plt.subplots(1, len(range_gears), sharex=True, sharey=True)
    fig.canvas.set_window_title('RPM Histogram per Gear')
    a = a.ravel()
    for i, gear in enumerate(range_gears):
        rpm_per_gear = [d[networking.fields['rpm']] for d in session_data if
                        d[networking.fields['gear']] == gear]

        ax = a[i]
        num_bins = 20
        n, bins, patches = ax.hist(rpm_per_gear, num_bins, density=True, facecolor='g')
        ax.set_xlabel('RPM')
        ax.set_ylabel('Prob')
        ax.set_xlim(rpm_min, rpm_max)
        ax.set_title('Gear {}'.format(gear))
    plt.show()


def plot_suspension_over_time(session_data):
    lap_time = [d[networking.fields['lap_time']] for d in session_data]
    susp_fl = [d[networking.fields['susp_fl']] for d in session_data]
    susp_fr = [d[networking.fields['susp_fr']] for d in session_data]
    susp_rl = [d[networking.fields['susp_rl']] for d in session_data]
    susp_rr = [d[networking.fields['susp_rr']] for d in session_data]
    susp_data = [susp_fl, susp_fr, susp_rl, susp_rr]
    susp_max = np.max(susp_data)
    susp_min = np.min(susp_data)
    susp_diff = susp_max - susp_min

    labels = ['susp_fl', 'susp_fr', 'susp_rl', 'susp_rr']
    plt.figure('Suspension over lap time')
    for i, susp in enumerate(susp_data):
        plt.plot(lap_time, susp, alpha=0.5)
    plt.legend(labels)
    plt.grid(True)
    plt.ylim(susp_max + susp_diff * 0.1, susp_min - susp_diff * 0.1)  # invert y axis and pad
    plt.xlabel('lap time (s)')
    plt.ylabel('RPM')
    plt.title('Suspension over lap time')
    plt.show()


def plot_height_over_dist(session_data):
    distance = [d[networking.fields['distance']] for d in session_data]
    height = [d[networking.fields['pos_y']] for d in session_data]
    fig, ax = plt.subplots()
    fig.canvas.set_window_title('Track Elevation')
    ax.plot(distance, height, label='height')
    ax.set(xlabel='distance (m)', ylabel='height (m)',
           title='Track Elevation')
    ax.grid()
    plt.show()


def plot_g_over_rpm(session_data):

    data_gear = [d[networking.fields['gear']] for d in session_data]
    range_gears = list(set(data_gear))
    range_gears.sort()

    fig = plt.figure('G-force over RPM (full throttle)')
    ax = fig.add_subplot(111)
    for i, g in enumerate(range_gears):
        g_force_lon = [d[networking.fields['g_force_lon']] for d in session_data if
                       d[networking.fields['gear']] == g and d[networking.fields['throttle']] == 1.0]
        rpm = [d[networking.fields['rpm']] for d in session_data if
               d[networking.fields['gear']] == g and d[networking.fields['throttle']] == 1.0]
        throttle = [d[networking.fields['throttle']] for d in session_data if
                    d[networking.fields['gear']] == g and d[networking.fields['throttle']] == 1.0]

        scale = 50.0
        throttle_scaled = [t * scale for t in throttle]

        ax.scatter(x=rpm, y=g_force_lon, c=colors[i], s=throttle_scaled, alpha=0.5, label='Gear {}'.format(str(g)))
    ax.set_xlabel('RPM')
    ax.set_ylabel('G-force X')
    plt.title('G-force over RPM (full throttle)')
    ax.legend()
    plt.show()


def plot_g_over_throttle(session_data):

    data_gear = [d[networking.fields['gear']] for d in session_data]
    range_gears = list(set(data_gear))
    range_gears.sort()

    fig = plt.figure('G-force X over throttle')
    ax = fig.add_subplot(111)
    for i, g in enumerate(range_gears):
        g_force_lon = [d[networking.fields['g_force_lon']] for d in session_data if d[networking.fields['gear']] == g]
        throttle = [d[networking.fields['throttle']] for d in session_data if d[networking.fields['gear']] == g]
        ax.scatter(x=throttle, y=g_force_lon, c=colors[i], s=25, alpha=0.5, label='Gear {}'.format(str(g)))
    ax.set_xlabel('throttle')
    ax.set_ylabel('G-force X')
    plt.title('G-force X over throttle')
    ax.legend()
    plt.show()


def plot_v_over_rpm(session_data):

    data_gear = [d[networking.fields['gear']] for d in session_data]
    range_gears = list(set(data_gear))
    range_gears.sort()

    fig = plt.figure('Speed over RPM (full throttle)')
    ax = fig.add_subplot(111)
    for i, g in enumerate(range_gears):
        speed_ms = [d[networking.fields['speed_ms']] for d in session_data if
                    d[networking.fields['gear']] == g and d[networking.fields['throttle']] == 1.0]
        rpm = [d[networking.fields['rpm']] for d in session_data if
               d[networking.fields['gear']] == g and d[networking.fields['throttle']] == 1.0]
        ax.scatter(x=rpm, y=speed_ms, c=colors[i], s=25, alpha=0.5, label='Gear {}'.format(str(g)))
    ax.set_xlabel('RPM')
    ax.set_ylabel('Speed (m/s)')
    ax.legend()
    plt.title('Speed over RPM (full throttle)')
    plt.show()


def plot_main(session_data):

    if session_data.size > 0:
        #plot_gear_over_3d_pos(session_data)
        plot_gear_over_2d_pos(session_data)
        plot_rpm_histogram_per_gear(session_data)
        plot_suspension_over_time(session_data)
        plot_height_over_dist(session_data)
        plot_g_over_rpm(session_data)
        plot_g_over_throttle(session_data)
        plot_v_over_rpm(session_data)

