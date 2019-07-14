import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

import networking
import utils

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


def plot_suspension_over_time(session_data):
    lap_time = [d[networking.fields['lap_time']] for d in session_data]
    susp_fl = [d[networking.fields['susp_fl']] for d in session_data]
    susp_fr = [d[networking.fields['susp_fr']] for d in session_data]
    susp_rl = [d[networking.fields['susp_rl']] for d in session_data]
    susp_rr = [d[networking.fields['susp_rr']] for d in session_data]
    susp_data = [susp_fl, susp_fr, susp_rl, susp_rr]

    susp_arg_max_wheels = [np.argmax(l) for l in susp_data]
    susp_max_wheels = [susp_data[i][a] for i, a in enumerate(susp_arg_max_wheels)]
    susp_data_arg_max = np.argmax(susp_max_wheels)
    susp_max = susp_max_wheels[susp_data_arg_max]

    susp_arg_min_wheels = [np.argmin(l) for l in susp_data]
    susp_min_wheels = [susp_data[i][a] for i, a in enumerate(susp_arg_min_wheels)]
    susp_data_arg_min = np.argmin(susp_min_wheels)
    susp_min = susp_min_wheels[susp_data_arg_min]

    susp_diff = susp_max - susp_min
    time_susp_max = lap_time[susp_arg_max_wheels[susp_data_arg_max]]
    time_susp_min = lap_time[susp_arg_min_wheels[susp_data_arg_min]]

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
    plt.text(time_susp_max, susp_max, 'max: {}'.format(susp_max))
    plt.text(time_susp_min, susp_min, 'min: {}'.format(susp_min))


def plot_height_over_dist(session_data):
    distance = [d[networking.fields['distance']] for d in session_data]
    height = [d[networking.fields['pos_y']] for d in session_data]
    fig, ax = plt.subplots()
    fig.canvas.set_window_title('Track Elevation')
    ax.plot(distance, height, label='height')
    ax.set(xlabel='distance (m)', ylabel='height (m)',
           title='Track Elevation')
    ax.grid()


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


def forward_over_2d_pos(session_data):

    # if we take all data points, the plot is too crowded
    sample_rate = 10

    x = [d[networking.fields['pos_x']] for i, d in enumerate(session_data) if i % sample_rate == 0]
    y = [d[networking.fields['pos_z']] for i, d in enumerate(session_data) if i % sample_rate == 0]
    x_min = min(x)
    x_max = max(x)
    x_middle = (x_max + x_min) * 0.5
    y_min = min(y)
    y_max = max(y)
    y_middle = (y_max + y_min) * 0.5
    diff = [x_max - x_min, y_max - y_min]
    diff_max = max(diff)

    # forward dir
    px = [d[networking.fields['pitch_x']] for i, d in enumerate(session_data) if i % sample_rate == 0]
    py = [d[networking.fields['pitch_z']] for i, d in enumerate(session_data) if i % sample_rate == 0]
    pxy_normalized = utils.normalize_2d_vectors(px, py)

    # forward speed
    vx = [d[networking.fields['vel_x']] for i, d in enumerate(session_data) if i % sample_rate == 0]
    vy = [d[networking.fields['vel_z']] for i, d in enumerate(session_data) if i % sample_rate == 0]
    vxy_normalized = utils.normalize_2d_vectors(vx, vy)

    # dot(dir, speed) = drift
    drift = list((pxy_normalized * vxy_normalized).sum(axis=0))
    drift_angle = np.arccos(drift)

    fig, ax = plt.subplots()
    plt.plot(x, y, c='k')
    q = ax.quiver(x, y, pxy_normalized[0], pxy_normalized[1], drift_angle,
                  angles='xy', scale_units='dots', scale=0.03, label='Forward dir', color='tab:purple')
    p = ax.quiver(x, y, vx, vy,
                  angles='xy', scale_units='xy', scale=5, label='Forward vel', color='tab:red')
    ax.set_xlim(x_middle - diff_max * 0.6, x_middle + diff_max * 0.6)
    ax.set_ylim(y_middle - diff_max * 0.6, y_middle + diff_max * 0.6)
    ax.text(x[0], y[0], 'start')
    ax.text(x[-1], y[-1], 'finish')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend()
    plt.title('Drift at 2D positions (drift angle as color)')
    fig.canvas.set_window_title('Drift at 2D positions')


def wheel_speed_over_time(session_data):

    lap_time = [d[networking.fields['lap_time']] for d in session_data]
    wsp_fl = [d[networking.fields['wsp_fl']] for d in session_data]
    wsp_fr = [d[networking.fields['wsp_fr']] for d in session_data]
    wsp_rl = [d[networking.fields['wsp_rl']] for d in session_data]
    wsp_rr = [d[networking.fields['wsp_rr']] for d in session_data]
    wsp_data = [wsp_fl, wsp_fr, wsp_rl, wsp_rr]

    wsp_arg_max_wheels = [np.argmax(l) for l in wsp_data]
    wsp_max_wheels = [wsp_data[i][a] for i, a in enumerate(wsp_arg_max_wheels)]
    wsp_data_arg_max = np.argmax(wsp_max_wheels)
    wsp_max = wsp_max_wheels[wsp_data_arg_max]

    wsp_arg_min_wheels = [np.argmin(l) for l in wsp_data]
    wsp_min_wheels = [wsp_data[i][a] for i, a in enumerate(wsp_arg_min_wheels)]
    wsp_data_arg_min = np.argmin(wsp_min_wheels)
    wsp_min = wsp_min_wheels[wsp_data_arg_min]

    wsp_diff = wsp_max - wsp_min
    time_wsp_max = lap_time[wsp_arg_max_wheels[wsp_data_arg_max]]
    time_wsp_min = lap_time[wsp_arg_min_wheels[wsp_data_arg_min]]

    labels = ['wsp_fl', 'wsp_fr', 'wsp_rl', 'wsp_rr']
    plt.figure('Wheel speed over lap time')
    plt.title('Wheel speed over lap time')
    for i, wsp in enumerate(wsp_data):
        plt.plot(lap_time, wsp, alpha=0.5)
    plt.legend(labels)
    plt.grid(True)
    plt.ylim(wsp_max + wsp_diff * 0.1, wsp_min - wsp_diff * 0.1)  # invert y axis and pad
    plt.xlabel('lap time (s)')
    plt.ylabel('wheel speed')
    plt.text(time_wsp_max, wsp_max, 'max: {}'.format(wsp_max))
    plt.text(time_wsp_min, wsp_min, 'min: {}'.format(wsp_min))


def drift_over_speed(session_data):

    steering = [d[networking.fields['steering']] for i, d in enumerate(session_data)]
    speed_ms = [d[networking.fields['speed_ms']] for i, d in enumerate(session_data)]

    # forward dir
    px = [d[networking.fields['pitch_x']] for i, d in enumerate(session_data)]
    py = [d[networking.fields['pitch_z']] for i, d in enumerate(session_data)]
    pxy_normalized = utils.normalize_2d_vectors(px, py)

    # forward speed
    vx = [d[networking.fields['vel_x']] for i, d in enumerate(session_data)]
    vy = [d[networking.fields['vel_z']] for i, d in enumerate(session_data)]
    vxy_normalized = utils.normalize_2d_vectors(vx, vy)

    # dot(dir, speed) = drift
    drift = list((pxy_normalized * vxy_normalized).sum(axis=0))
    drift_angle = np.arccos(drift)

    fig = plt.figure('Drift over speed (steering as color)')
    plt.title('Drift over speed (steering as color)')
    plt.scatter(x=speed_ms, y=drift_angle, c=steering, s=25, alpha=0.5, label='drift over steer')
    plt.xlabel('speed (m/s)')
    plt.ylabel('drift angle')


def plot_main(session_data):

    if session_data.size > 0:
        #plot_gear_over_3d_pos(session_data)
        plot_gear_over_2d_pos(session_data)
        plot_rpm_histogram_per_gear(session_data)
        plot_suspension_over_time(session_data)
        #plot_height_over_dist(session_data)
        #plot_g_over_rpm(session_data)
        #plot_g_over_throttle(session_data)
        plot_v_over_rpm(session_data)
        forward_over_2d_pos(session_data)
        wheel_speed_over_time(session_data)
        drift_over_speed(session_data)

        plt.show()

