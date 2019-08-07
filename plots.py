import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

import networking
import utils
import data_processing

static_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
                 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']


def plot_main(session_data):

    session_data = session_data.copy()
    if session_data.size > 0:
        plot_gear_over_3d_pos(session_data)
        plot_gear_over_2d_pos(session_data)
        plot_rpm_histogram_per_gear(session_data)
        plot_suspension_over_time(session_data)
        plot_suspension_lr_fr_over_time(session_data)
        #plot_height_over_dist(session_data)
        plot_g_over_rpm(session_data)
        plot_g_over_throttle(session_data)
        plot_v_over_rpm(session_data)
        forward_over_2d_pos(session_data)
        wheel_speed_over_time(session_data)
        wheel_speed_lr_fr_over_time(session_data)
        drift_over_speed(session_data)

        plt.show()


def plot_over_3d_pos(session_data, scale, color, title, slicing):

    x, y, z = data_processing.get_3d_coordinates(session_data)
    x_min, x_middle, x_max = data_processing.get_min_middle_max(x)
    y_min, y_middle, y_max = data_processing.get_min_middle_max(y)
    z_min, z_middle, z_max = data_processing.get_min_middle_max(z)

    diff = np.array([x_max - x_min, y_max - y_min, z_max - z_min])
    diff_max = diff.max()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x[::slicing], y[::slicing], z[::slicing], marker='o',
               s=scale[::slicing], c=color[::slicing])
    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.set_zlabel('Y')
    ax.text(x[0], y[0], z[0], 'start')
    ax.text(x[-1], y[-1], z[-1], 'finish')
    ax.set_xlim(x_middle - diff_max * 0.6, x_middle + diff_max * 0.6)
    ax.set_ylim(y_middle - diff_max * 0.6, y_middle + diff_max * 0.6)
    ax.set_zlim(z_middle - diff_max * 0.1, z_middle + diff_max * 1.1)
    plt.title(title)
    plt.set_cmap('plasma')


def plot_over_2d_pos(session_data, lines_x, lines_y, scale, alpha, title, labels):
    x, y = data_processing.get_2d_coordinates(session_data)
    x_min, x_middle, x_max = data_processing.get_min_middle_max(x)
    y_min, y_middle, y_max = data_processing.get_min_middle_max(y)

    diff = np.array([x_max - x_min, y_max - y_min])
    diff_max = diff.max()

    fig = plt.figure(title)
    ax = fig.add_subplot(111)
    for i, g in enumerate(lines_x):
        ax.scatter(x=lines_x[i], y=lines_y[i], s=scale, alpha=alpha, label=labels[i])
    ax.set_xlim(x_middle - diff_max * 0.6, x_middle + diff_max * 0.6)
    ax.set_ylim(y_middle - diff_max * 0.6, y_middle + diff_max * 0.6)
    if len(labels) > 1:
        ax.legend()
    ax.text(x[0], y[0], 'start')
    ax.text(x[-1], y[-1], 'finish')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.title(title)


def scatter_plot(x_points, y_points, title, labels, colors, scales, alphas, x_label, y_label):

    fig = plt.figure(title)
    ax = fig.add_subplot(111)
    for i, g in enumerate(x_points):
        ax.scatter(x=x_points[i], y=y_points[i], c=colors[i], s=scales[i], alpha=alphas[i], label=labels[i])
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    plt.title(title)
    if len(labels) > 1:
        ax.legend()


def line_plot(x_points, y_points, title, labels, alpha, x_label, y_label, flip_y=False):

    arg_y_max = np.unravel_index(np.argmax(y_points), y_points.shape)
    arg_y_min = np.unravel_index(np.argmin(y_points), y_points.shape)

    plt.figure(title)
    for i, g in enumerate(x_points):
        plt.plot(x_points[i], y_points[i], alpha=alpha)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if len(labels) > 1:
        plt.legend(labels)
    plt.grid(True)
    plt.title(title)
    plt.text(x_points[arg_y_max], y_points[arg_y_max], 'max: {:.2f}'.format(y_points[arg_y_max]))
    plt.text(x_points[arg_y_min], y_points[arg_y_min], 'min: {:.2f}'.format(y_points[arg_y_min]))
    if flip_y:
        y_diff = y_points[arg_y_max] - y_points[arg_y_min]
        plt.ylim(y_points[arg_y_max] + y_diff * 0.1, y_points[arg_y_min] - y_diff * 0.1)  # invert y axis and pad


def plot_gear_over_3d_pos(session_data):

    rpm = session_data[networking.fields['rpm']]
    rpm_max = rpm.max()
    scale = 50.0
    rpm_normalized_scaled = rpm / rpm_max * scale
    gear = session_data[networking.fields['gear']]
    gear_max = max(gear)
    gear_normalized_scaled = gear / gear_max

    plot_over_3d_pos(session_data=session_data, scale=rpm_normalized_scaled, color=gear_normalized_scaled,
                     title='3D positions (gear as color)', slicing=100)


def plot_gear_over_2d_pos(session_data):

    gear = session_data[networking.fields['gear']]
    range_gears = np.unique(gear)

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    lines_x = []
    lines_y = []
    for i, g in enumerate(range_gears):
        current_gear = session_data[networking.fields['gear']] == g
        pos_x = session_data[networking.fields['pos_x'], current_gear]
        pos_y = -session_data[networking.fields['pos_z'], current_gear]
        lines_x += [pos_x]
        lines_y += [pos_y]

    plot_over_2d_pos(session_data=session_data, lines_x=lines_x, lines_y=lines_y,
                     scale=10, alpha=0.5, title='Gear at 2D positions', labels=labels)


def plot_rpm_histogram_per_gear(session_data):
    rpm = session_data[networking.fields['rpm']]
    data_gear = session_data[networking.fields['gear']]
    range_gears = list(set(data_gear))
    range_gears.sort()
    range_gears = [g for g in range_gears if g > 0.0]
    rpm_min = min(rpm)
    rpm_max = max(rpm)

    num_total_samples = session_data.shape[1]
    fig, a = plt.subplots(1, len(range_gears), sharex=True, sharey=True)
    fig.canvas.set_window_title('RPM Histogram per Gear')
    a = a.ravel()
    for i, gear in enumerate(range_gears):
        current_gear = session_data[networking.fields['gear']] == gear
        rpm_per_gear = session_data[networking.fields['rpm'], current_gear]
        num_samples_gear = len(rpm_per_gear)
        samples_gear_ratio = num_samples_gear / num_total_samples

        ax = a[i]
        num_bins = 20
        n, bins, patches = ax.hist(rpm_per_gear, num_bins, facecolor='g')
        ax.set_xlabel('RPM')
        ax.set_ylabel('Samples (~time)')
        ax.set_xlim(rpm_min, rpm_max)
        ax.set_title('G{0}: {1:.1f}%'.format(int(gear), samples_gear_ratio * 100.0))


def plot_suspension_over_time(session_data):
    lap_time = session_data[networking.fields['lap_time']]
    susp_fl = session_data[networking.fields['susp_fl']]
    susp_fr = session_data[networking.fields['susp_fr']]
    susp_rl = session_data[networking.fields['susp_rl']]
    susp_rr = session_data[networking.fields['susp_rr']]
    susp_data = [susp_fl, susp_fr, susp_rl, susp_rr]

    labels = ['front left', 'front right', 'rear left', 'rear right']
    x_points = np.array([lap_time] * len(susp_data))
    y_points = np.array(susp_data)

    line_plot(x_points=x_points, y_points=y_points, title='Suspension dislocation over lap time',
              labels=labels, alpha=0.5, x_label='Lap time (s)', y_label='Suspension dislocation (mm)', flip_y=True)


def plot_suspension_lr_fr_over_time(session_data):
    lap_time = session_data[networking.fields['lap_time']]
    susp_fl = session_data[networking.fields['susp_fl']]
    susp_fr = session_data[networking.fields['susp_fr']]
    susp_rl = session_data[networking.fields['susp_rl']]
    susp_rr = session_data[networking.fields['susp_rr']]
    susp_left_right = (susp_fl + susp_rl) * 0.5 - (susp_fr + susp_rr) * 0.5
    susp_front_rear = (susp_fl + susp_fr) * 0.5 - (susp_rl + susp_rr) * 0.5
    susp_data = [susp_left_right, susp_front_rear]

    labels = ['left-right', 'front-rear']
    x_points = np.array([lap_time] * len(susp_data))
    y_points = np.array(susp_data)

    line_plot(x_points=x_points, y_points=y_points, title='Suspension dislocation difference over lap time',
              labels=labels, alpha=0.5, x_label='Lap time (s)',
              y_label='Suspension dislocation difference (mm)', flip_y=True)


def plot_height_over_dist(session_data):
    distance = session_data[networking.fields['distance']]
    height = session_data[networking.fields['pos_y']]
    fig, ax = plt.subplots()
    fig.canvas.set_window_title('Track Elevation')
    ax.plot(distance, height, label='height')
    ax.set(xlabel='distance (m)', ylabel='height (m)',
           title='Track Elevation')
    ax.grid()


def plot_g_over_rpm(session_data):

    data_gear = session_data[networking.fields['gear']]
    range_gears = list(set(data_gear))
    range_gears.sort()

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    scale = 50.0
    alphas = [0.5] * len(labels)
    colors = [static_colors[i] for i, g in enumerate(range_gears)]

    x_points = []
    y_points = []
    scales = []
    for i, g in enumerate(range_gears):
        current_gear = session_data[networking.fields['gear']] == g
        full_throttle = session_data[networking.fields['throttle']] == 1.0
        interesting = np.logical_and(current_gear, full_throttle)

        g_force_lon = session_data[networking.fields['g_force_lon'], interesting]
        rpm = session_data[networking.fields['rpm'], interesting]
        throttle = session_data[networking.fields['throttle'], interesting]
        throttle_scaled = [t * scale for t in throttle]

        x_points += [rpm]
        y_points += [g_force_lon]
        scales += [throttle_scaled]

    scatter_plot(x_points=x_points, y_points=y_points, title='G-force over RPM (full throttle)',
                 labels=labels, colors=colors, scales=scales, alphas=alphas, x_label='RPM', y_label='G-force X')


def plot_g_over_throttle(session_data):

    data_gear = session_data[networking.fields['gear']]
    range_gears = list(set(data_gear))
    range_gears.sort()

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    colors = [static_colors[i] for i, g in enumerate(range_gears)]
    scales = [25] * len(labels)
    alphas = [0.5] * len(labels)

    x_points = []
    y_points = []
    for i, g in enumerate(range_gears):
        current_gear = session_data[networking.fields['gear']] == g

        throttle = session_data[networking.fields['throttle'], current_gear]
        g_force_lon = session_data[networking.fields['g_force_lon'], current_gear]

        x_points += [throttle]
        y_points += [g_force_lon]

    scatter_plot(x_points=x_points, y_points=y_points, title='G-force X over throttle',
                 labels=labels, colors=colors, scales=scales, alphas=alphas, x_label='throttle', y_label='G-force X')


def plot_v_over_rpm(session_data):

    data_gear = session_data[networking.fields['gear']]
    range_gears = list(set(data_gear))
    range_gears.sort()

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    colors = [static_colors[i] for i, g in enumerate(range_gears)]
    scales = [25] * len(labels)
    alphas = [0.5] * len(labels)

    x_points = []
    y_points = []
    for i, g in enumerate(range_gears):
        current_gear = session_data[networking.fields['gear']] == g
        full_throttle = session_data[networking.fields['throttle']] == 1.0
        interesting = np.logical_and(current_gear, full_throttle)

        rpm = session_data[networking.fields['rpm'], interesting]
        speed_ms = session_data[networking.fields['speed_ms'], interesting]

        x_points += [rpm]
        y_points += [speed_ms]

    scatter_plot(x_points=x_points, y_points=y_points, title='Speed over RPM (full throttle)',
                   labels=labels, colors=colors, scales=scales, alphas=alphas, x_label='RPM', y_label='Speed (m/s)')


def forward_over_2d_pos(session_data):

    # if we take all data points, the plot is too crowded
    sample_rate = 10

    x, y = data_processing.get_2d_coordinates(session_data)
    x = x[::sample_rate]
    y = y[::sample_rate]
    x_min, x_middle, x_max = data_processing.get_min_middle_max(x)
    y_min, y_middle, y_max = data_processing.get_min_middle_max(y)

    diff = [x_max - x_min, y_max - y_min]
    diff_max = max(diff)

    # forward dir
    px = session_data[networking.fields['pitch_x'], ::sample_rate]
    py = -session_data[networking.fields['pitch_z'], ::sample_rate]
    pxy_normalized = utils.normalize_2d_vectors(px, py)

    # forward speed
    vx = session_data[networking.fields['vel_x'], ::sample_rate]
    vy = -session_data[networking.fields['vel_z'], ::sample_rate]
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

    lap_time = session_data[networking.fields['lap_time']]
    wsp_fl = session_data[networking.fields['wsp_fl']]
    wsp_fr = session_data[networking.fields['wsp_fr']]
    wsp_rl = session_data[networking.fields['wsp_rl']]
    wsp_rr = session_data[networking.fields['wsp_rr']]
    wsp_data = [wsp_fl, wsp_fr, wsp_rl, wsp_rr]

    labels = ['front left', 'front right', 'rear left', 'rear right']
    x_points = np.array([lap_time] * len(wsp_data))
    y_points = np.array(wsp_data)

    line_plot(x_points=x_points, y_points=y_points, title='Wheel speed over lap time',
              labels=labels, alpha=0.5, x_label='Lap time (s)', y_label='Wheel speed (m/s)')


def wheel_speed_lr_fr_over_time(session_data):

    lap_time = session_data[networking.fields['lap_time']]
    wsp_fl = session_data[networking.fields['wsp_fl']]
    wsp_fr = session_data[networking.fields['wsp_fr']]
    wsp_rl = session_data[networking.fields['wsp_rl']]
    wsp_rr = session_data[networking.fields['wsp_rr']]
    wsp_left_right = (wsp_fl + wsp_rl) * 0.5 - (wsp_fr + wsp_rr) * 0.5
    wsp_front_rear = (wsp_fl + wsp_fr) * 0.5 - (wsp_rl + wsp_rr) * 0.5
    wsp_data = [wsp_left_right, wsp_front_rear]

    labels = ['left-right', 'front-rear']
    x_points = np.array([lap_time] * len(wsp_data))
    y_points = np.array(wsp_data)

    line_plot(x_points=x_points, y_points=y_points, title='Wheel speed difference over lap time',
              labels=labels, alpha=0.5, x_label='Lap time (s)', y_label='Wheel speed difference (m/s)')


def drift_over_speed(session_data):

    steering = np.abs(session_data[networking.fields['steering']])
    speed_ms = session_data[networking.fields['speed_ms']]

    # forward dir
    px = session_data[networking.fields['pitch_x']]
    py = session_data[networking.fields['pitch_z']]
    pxy_normalized = utils.normalize_2d_vectors(px, py)

    # forward speed
    vx = session_data[networking.fields['vel_x']]
    vy = session_data[networking.fields['vel_z']]
    vxy_normalized = utils.normalize_2d_vectors(vx, vy)

    # dot(dir, speed) = drift
    drift = list((pxy_normalized * vxy_normalized).sum(axis=0))
    drift_angle = np.arccos(drift)

    colors = [steering]
    scales = [25]
    alphas = [0.5]
    labels = ['drift over steer']
    x_points = [speed_ms]
    y_points = [drift_angle]

    scatter_plot(x_points=x_points, y_points=y_points, title='Drift over speed (steering as color)',
                 labels=labels, colors=colors, scales=scales, alphas=alphas,
                 x_label='Speed (m/s)', y_label='Drift angle (rad)')
