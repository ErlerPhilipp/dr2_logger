import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from scipy.stats import binned_statistic

import networking
import data_processing

static_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
                 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']


def plot_main(session_data):

    session_data = session_data.copy()
    if session_data.size > 0:
        #fig = plt.figure()
        #ax = fig.add_subplot(111, projection='3d')
        #fig.canvas.set_window_title('3D positions (gear as color)')
        #plot_gear_over_3d_pos(ax, session_data)

        fig, ax = plt.subplots(1, 2)
        fig.canvas.set_window_title('Map Basics')
        plot_height_over_dist(ax[0], session_data)
        plot_energy_over_2d_pos(ax[1], session_data)
        # plot_gear_over_2d_pos(ax[1], session_data)

        fig, ax = plt.subplots(2, 1, sharex=True)
        fig.canvas.set_window_title('Energy and Power')
        energy_over_time(ax[0], session_data)
        power_over_time(ax[1], session_data)

        # fig, ax = plt.subplots(1, 1)
        # fig.canvas.set_window_title('Energy')
        # plot_energy_over_2d_pos(ax, session_data)

        fig, ax = plt.subplots(1, 1)
        fig.canvas.set_window_title('RPM Histogram per Gear')
        gear_rpm_bars(ax, session_data)

        fig, ax = plt.subplots(1, 1)
        fig.canvas.set_window_title('Speed over RPM')
        plot_v_over_rpm(ax, session_data)

        fig, ax = plt.subplots(1, 2, sharey=True)
        fig.canvas.set_window_title('Power')
        plot_p_over_rpm(ax[0], session_data)
        plot_p_over_vel(ax[1], session_data)

        #fig, ax = plt.subplots(2, 1)
        #fig.canvas.set_window_title('G-Force')
        #plot_g_over_rpm(ax[0], session_data)
        #plot_g_over_throttle(ax[1], session_data)

        fig, ax = plt.subplots(1, 3)
        fig.canvas.set_window_title('Drift at 2D positions (drift angle as color)')
        forward_over_2d_pos(ax[0], session_data)
        drift_angle_bars(ax[1], session_data)
        drift_angle_change_bars(ax[2], session_data)
        #drift_over_speed(ax[1][1], session_data)

        fig, ax = plt.subplots(2, 1, sharex=True)
        fig.canvas.set_window_title('Suspension')
        suspension_bars(ax[0], session_data)
        suspension_l_r_f_r_bars(ax[1], session_data)

        fig, ax = plt.subplots(3, 1, sharex=True)
        fig.canvas.set_window_title('Wheel Speed')
        wheel_speed_over_time(ax[0], session_data)
        wheel_speed_lr_fr_over_time(ax[1], session_data)
        inputs_over_time(ax[2], session_data)

        fig, ax = plt.subplots(3, 1, sharex=True)
        fig.canvas.set_window_title('Rotation vs Suspension')
        rotation_over_time(ax[0], session_data)
        suspension_lr_fr_angles_over_time(ax[1], session_data)
        suspension_l_r_f_r_over_time(ax[2], session_data)

        plt.show()


def plot_over_3d_pos(ax, session_data, scale, color, slicing):

    x, y, z = data_processing.get_3d_coordinates(session_data)
    x_min, x_middle, x_max = data_processing.get_min_middle_max(x)
    y_min, y_middle, y_max = data_processing.get_min_middle_max(y)
    z_min, z_middle, z_max = data_processing.get_min_middle_max(z)

    diff = np.array([x_max - x_min, y_max - y_min, z_max - z_min])
    diff_max = diff.max()
    #ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x[::slicing], y[::slicing], z[::slicing], marker='o',
               s=scale[::slicing], c=color[::slicing], cmap='plasma')
    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.set_zlabel('Y')
    ax.text(x[0], y[0], z[0], 'start')
    ax.text(x[-1], y[-1], z[-1], 'finish')
    ax.set_xlim(x_middle - diff_max * 0.6, x_middle + diff_max * 0.6)
    ax.set_ylim(y_middle - diff_max * 0.6, y_middle + diff_max * 0.6)
    ax.set_zlim(z_middle - diff_max * 0.1, z_middle + diff_max * 1.1)
    return ax


def plot_over_2d_pos(ax, session_data, lines_x, lines_y, scale, alpha, title, labels):
    x, y = data_processing.get_2d_coordinates(session_data)
    x_min, x_middle, x_max = data_processing.get_min_middle_max(x)
    y_min, y_middle, y_max = data_processing.get_min_middle_max(y)

    diff = np.array([x_max - x_min, y_max - y_min])
    diff_max = diff.max()

    for i, g in enumerate(lines_x):
        if type(scale) == list:
            ax.scatter(x=lines_x[i], y=lines_y[i], s=scale[i], alpha=alpha, label=labels[i])
        else:
            ax.scatter(x=lines_x[i], y=lines_y[i], s=scale, alpha=alpha, label=labels[i])
    lim_left = x_middle - diff_max * 0.6
    lim_right = x_middle + diff_max * 0.6
    if lim_left != lim_right:
        ax.set_xlim(lim_left, lim_right)
    lim_bottom = y_middle - diff_max * 0.6
    lim_top = y_middle + diff_max * 0.6
    if lim_bottom != lim_top:
        ax.set_ylim(lim_bottom, lim_top)
    if labels is not None and len(labels) > 1:
        ax.legend()
    ax.text(x[0], y[0], 'start')
    ax.text(x[-1], y[-1], 'finish')
    ax.set_title(title)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')


def scatter_plot(ax, x_points, y_points, title, labels, colors, scales, alphas, x_label, y_label):

    for i, g in enumerate(x_points):
        ax.scatter(x=x_points[i], y=y_points[i], c=colors[i], s=scales[i], alpha=alphas[i], label=labels[i])
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if labels is not None and len(labels) > 1:
        ax.legend()


def line_plot(ax, x_points, y_points, title, labels, alpha, x_label, y_label,
              flip_y=False, min_max_annotations=True):

    arg_y_max = np.unravel_index(np.argmax(y_points), y_points.shape)
    arg_y_min = np.unravel_index(np.argmin(y_points), y_points.shape)

    for i, g in enumerate(x_points):
        ax.plot(x_points[i], y_points[i], alpha=alpha)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if labels is not None:
        ax.legend(labels)
    ax.grid(True)
    ax.set_title(title)

    if min_max_annotations:
        x_offset = 32
        y_offset = 20
        if flip_y:
            y_offset = -y_offset
        bbox = dict(boxstyle="round", fc="0.8")
        arrow_props = dict(arrowstyle="->", connectionstyle="angle,angleA=0,angleB=90,rad=10")
        ax.annotate('max: {:.2f}'.format(y_points[arg_y_max]), (x_points[arg_y_max], y_points[arg_y_max]),
                    xytext=(x_offset, y_offset), textcoords='offset points', bbox=bbox, arrowprops=arrow_props)
        ax.annotate('min: {:.2f}'.format(y_points[arg_y_min]), (x_points[arg_y_min], y_points[arg_y_min]),
                    xytext=(x_offset, -y_offset), textcoords='offset points', bbox=bbox, arrowprops=arrow_props)

    # invert y axis and pad
    y_diff = y_points[arg_y_max] - y_points[arg_y_min]
    if not flip_y:
        ax.set_ylim(y_points[arg_y_min] - y_diff * 0.1, y_points[arg_y_max] + y_diff * 0.1)
    else:
        ax.set_ylim(y_points[arg_y_max] + y_diff * 0.1, y_points[arg_y_min] - y_diff * 0.1)


def histogram_plot(ax, samples, title, x_label, y_label, labels=None, min=None, max=None, num_bins=20, color=None):

        if min is None:
            min = samples.min()
        if max is None:
            max = samples.max()
        n, bins, patches = ax.hist(list(samples), num_bins, color=color, label=labels)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_xlim(min, max)
        if labels is not None and len(labels) > 1:
            ax.legend(labels)
        ax.set_title(title)


def bar_plot(ax, data, weights, num_bins=20,
             title=None, x_label=None, y_label=None, series_labels=None, tick_labels=None):

    if len(data) == 0 or data[0].size == 0:
        return

    data_min = min([d.min() for d in data])
    data_max = max([d.max() for d in data])

    x = np.arange(num_bins)

    default_width = 0.8
    width = default_width / (float(len(series_labels)) + 1)
    for i in range(len(series_labels)):
        data_bin_sum, bin_edges, _ = \
            binned_statistic(data[i], weights[i], statistic='sum', bins=num_bins, range=(data_min, data_max))
        tick_labels = ['{:.0f} to\n {:.0f}'.format(bin_edges[0 + i], bin_edges[1 + i])
                       for i in range(bin_edges.shape[0] - 1)]

        ax.bar(x + (0.5 + i - float(len(series_labels)) * 0.5) * width, data_bin_sum, width, label=series_labels[i])

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if series_labels is not None and len(series_labels) > 1:
        ax.legend(series_labels)
    ax.set_xticks(x)
    ax.set_xticklabels(tick_labels)
    ax.set_title(title)


def plot_gear_over_3d_pos(ax, session_data):

    slicing = 100
    x, y, z = data_processing.get_3d_coordinates(session_data)
    dx, dy, dz = data_processing.get_forward_dir_3d(session_data)

    rpm = session_data[networking.Fields.rpm.value]
    rpm_max = rpm.max()
    scale = 50.0
    rpm_normalized_scaled = rpm / rpm_max * scale
    gear = session_data[networking.Fields.gear.value]
    gear_max = max(gear)
    gear_normalized_scaled = gear / gear_max

    ax = plot_over_3d_pos(ax, session_data=session_data, scale=rpm_normalized_scaled,
                          color=gear_normalized_scaled, slicing=slicing)
    ax.quiver(x[::slicing], y[::slicing], z[::slicing],
              dx[::slicing], dy[::slicing], dz[::slicing], length=100.0, normalize=True)


def plot_gear_over_2d_pos(ax, session_data):

    gear = session_data[networking.Fields.gear.value]
    pos_x, pos_y = data_processing.get_2d_coordinates(session_data)
    range_gears = np.unique(gear)

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    lines_x = []
    lines_y = []
    for i, g in enumerate(range_gears):
        current_gear = session_data[networking.Fields.gear.value] == g
        lines_x += [pos_x[current_gear]]
        lines_y += [pos_y[current_gear]]

    plot_over_2d_pos(ax, session_data=session_data, lines_x=lines_x, lines_y=lines_y,
                     scale=10, alpha=0.5, title='Gear at 2D positions', labels=labels)


def plot_energy_over_2d_pos(ax, session_data):

    scale_factor = 100.0
    gear = session_data[networking.Fields.gear.value]
    pos_x, pos_y = data_processing.get_2d_coordinates(session_data)
    range_gears = np.unique(gear)

    energy, kinetic_energy, potential_energy = data_processing.get_energy(session_data=session_data)
    energy_truncated = energy - np.min(energy)
    energy_normalized = energy_truncated / np.max(energy_truncated)

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    lines_x = []
    lines_y = []
    scales = []
    for i, g in enumerate(range_gears):
        current_gear = session_data[networking.Fields.gear.value] == g
        lines_x += [pos_x[current_gear]]
        lines_y += [pos_y[current_gear]]
        scales += [energy_normalized[current_gear] * scale_factor]

    plot_over_2d_pos(ax, session_data=session_data, lines_x=lines_x, lines_y=lines_y,
                     scale=scales, alpha=0.5, title='Gear at 2D positions, scaled by energy', labels=labels)


def gear_rpm_bars(ax, session_data):

    time_differences = data_processing.differences(session_data[networking.Fields.lap_time.value])
    # prevent negative times due to next lap
    time_differences[time_differences < 0.0] = np.finfo(time_differences.dtype).eps
    rpm = session_data[networking.Fields.rpm.value]
    data_gear = session_data[networking.Fields.gear.value]
    range_gears = list(set(data_gear))
    range_gears.sort()

    total_time = time_differences.sum()
    gear_ids = [data_gear == gear for gear in range_gears]
    gear_times = [time_differences[g] for g in gear_ids]
    gear_rpms = [rpm[g] for g in gear_ids]
    gear_time_sums = [gt.sum() for gt in gear_times]
    if total_time == 0.0:
        gear_ratio = [0.0] * len(gear_time_sums)
    else:
        gear_ratio = [gts / total_time for gts in gear_time_sums]
    series_labels = ['Gear {0}: {1:.1f}%'.format(
        int(g), gear_ratio[gi] * 100.0) for gi, g in enumerate(range_gears)]

    bar_plot(ax, data=gear_rpms, weights=gear_times, num_bins=20,
             title='Gear RPM', x_label='RPM', y_label='Accumulated Time (s)', series_labels=series_labels)


def energy_over_time(ax, session_data):
    lap_time = session_data[networking.Fields.lap_time.value]
    energy, kinetic_energy, potential_energy = data_processing.get_energy(session_data=session_data)
    energy_data = np.array([energy, kinetic_energy, potential_energy])

    labels = ['Energy [kJ]', 'Kinetic Energy [kJ]', 'Potential Energy [kJ]']
    y_points = energy_data
    x_points = np.array([lap_time] * y_points.shape[0])

    line_plot(ax, x_points=x_points, y_points=y_points, title='Energy over lap time',
              labels=labels, alpha=0.5, x_label='Lap time (s)', y_label='Energy', min_max_annotations=False)


def power_over_time(ax, session_data):
    lap_time = session_data[networking.Fields.lap_time.value]
    energy, kinetic_energy, potential_energy = data_processing.get_energy(session_data=session_data)
    power = data_processing.derive_no_nan(energy, lap_time)
    full_acceleration = data_processing.get_full_acceleration_mask(session_data=session_data)
    not_full_acceleration = np.logical_not(full_acceleration)
    power_full_acceleration = power.copy()
    power_full_acceleration[not_full_acceleration] = 0.0
    power_not_full_acceleration = power.copy()
    power_not_full_acceleration[full_acceleration] = 0.0
    power_data = np.array([power_full_acceleration, power_not_full_acceleration])

    labels = ['Power at full throttle [kW]', 'Power otherwise [kW]']
    y_points = power_data
    x_points = np.array([lap_time] * y_points.shape[0])

    line_plot(ax, x_points=x_points, y_points=y_points, title='Power over lap time',
              labels=labels, alpha=0.5, x_label='Lap time (s)', y_label='Power', min_max_annotations=False)


def inputs_over_time(ax, session_data):
    lap_time = session_data[networking.Fields.lap_time.value]
    throttle = session_data[networking.Fields.throttle.value]
    brakes = session_data[networking.Fields.brakes.value]
    steering = session_data[networking.Fields.steering.value]
    input_data = np.array([throttle, brakes, steering])

    labels = ['throttle', 'brakes', 'steering']
    y_points = input_data
    x_points = np.array([lap_time] * y_points.shape[0])

    line_plot(ax, x_points=x_points, y_points=y_points, title='Inputs over lap time',
              labels=labels, alpha=0.5, x_label='Lap time (s)', y_label='Inputs', min_max_annotations=False)


def suspension_over_time(ax, session_data):
    lap_time = session_data[networking.Fields.lap_time.value]
    susp_fl = session_data[networking.Fields.susp_fl.value]
    susp_fr = session_data[networking.Fields.susp_fr.value]
    susp_rl = session_data[networking.Fields.susp_rl.value]
    susp_rr = session_data[networking.Fields.susp_rr.value]
    susp_data = np.array([susp_fl, susp_fr, susp_rl, susp_rr])

    labels = ['front left', 'front right', 'rear left', 'rear right']
    y_points = susp_data
    x_points = np.array([lap_time] * y_points.shape[0])

    line_plot(ax, x_points=x_points, y_points=y_points, title='Suspension dislocation over lap time',
              labels=labels, alpha=0.5, x_label='Lap time (s)', y_label='Suspension dislocation (mm)',
              flip_y=True, min_max_annotations=True)


def suspension_lr_fr_over_time(ax, session_data):
    lap_time = session_data[networking.Fields.lap_time.value]
    susp_fl = session_data[networking.Fields.susp_fl.value]
    susp_fr = session_data[networking.Fields.susp_fr.value]
    susp_rl = session_data[networking.Fields.susp_rl.value]
    susp_rr = session_data[networking.Fields.susp_rr.value]
    susp_left_right = (susp_fl + susp_rl) * 0.5 - (susp_fr + susp_rr) * 0.5
    susp_front_rear = (susp_fl + susp_fr) * 0.5 - (susp_rl + susp_rr) * 0.5
    susp_data = np.array([susp_left_right, susp_front_rear])

    labels = ['left-right', 'front-rear']
    x_points = np.array([lap_time] * len(susp_data))
    y_points = np.array(susp_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Suspension dislocation difference over lap time',
              labels=labels, alpha=0.5, x_label='Lap time (s)',
              y_label='Suspension dislocation difference (mm)', flip_y=True, min_max_annotations=True)


def suspension_l_r_f_r_over_time(ax, session_data):

    lap_time = session_data[networking.Fields.lap_time.value]
    susp_fl = session_data[networking.Fields.susp_fl.value]
    susp_fr = session_data[networking.Fields.susp_fr.value]
    susp_rl = session_data[networking.Fields.susp_rl.value]
    susp_rr = session_data[networking.Fields.susp_rr.value]
    susp_left = (susp_fl + susp_rl) * 0.5
    susp_right = (susp_fr + susp_rr) * 0.5
    susp_front = (susp_fl + susp_fr) * 0.5
    susp_rear = (susp_rl + susp_rr) * 0.5
    susp_data = np.array([susp_left, susp_right, susp_front, susp_rear])

    labels = ['left', 'right', 'front', 'rear']
    x_points = np.array([lap_time] * len(susp_data))
    y_points = np.array(susp_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Average suspension dislocation over lap time',
              labels=labels, alpha=0.5, x_label='Lap time (s)',
              y_label='Suspension dislocation (mm)', flip_y=True, min_max_annotations=True)


def suspension_bars(ax, session_data):

    time_differences = data_processing.differences(session_data[networking.Fields.lap_time.value])
    # prevent negative times due to next lap
    time_differences[time_differences < 0.0] = np.finfo(time_differences.dtype).eps
    susp_fl = session_data[networking.Fields.susp_fl.value]
    susp_fr = session_data[networking.Fields.susp_fr.value]
    susp_rl = session_data[networking.Fields.susp_rl.value]
    susp_rr = session_data[networking.Fields.susp_rr.value]
    susp_data = np.array([susp_fl, susp_fr, susp_rl, susp_rr])
    time_data = np.repeat(np.expand_dims(time_differences, axis=0), 4, axis=0)
    susp_min = susp_data.min()
    susp_max = susp_data.max()
    susp_min_ids = (susp_min == susp_data)
    susp_max_ids = (susp_max == susp_data)
    series_labels = ['front left', 'front right', 'rear left', 'rear right']
    series_labels = [l + ', bump min: {:.1f} s, bump max: {:.1f} s'.format(
        time_differences[susp_min_ids[li]].sum(), time_differences[susp_max_ids[li]].sum())
              for li, l in enumerate(series_labels)]

    bar_plot(ax, data=susp_data, weights=time_data, num_bins=20,
             title='Suspension dislocation, min: {:.1f} mm, max: {:.1f} mm'.format(susp_min, susp_max),
             x_label='Suspension dislocation (mm)', y_label='Accumulated Time (s)', series_labels=series_labels)


def suspension_l_r_f_r_bars(ax, session_data):

    time_differences = data_processing.differences(session_data[networking.Fields.lap_time.value])
    # prevent negative times due to next lap
    time_differences[time_differences < 0.0] = np.finfo(time_differences.dtype).eps
    susp_fl = session_data[networking.Fields.susp_fl.value]
    susp_fr = session_data[networking.Fields.susp_fr.value]
    susp_rl = session_data[networking.Fields.susp_rl.value]
    susp_rr = session_data[networking.Fields.susp_rr.value]
    susp_left = (susp_fl + susp_rl) * 0.5
    susp_right = (susp_fr + susp_rr) * 0.5
    susp_front = (susp_fl + susp_fr) * 0.5
    susp_rear = (susp_rl + susp_rr) * 0.5
    susp_data = np.array([susp_left, susp_right, susp_front, susp_rear])
    time_data = np.repeat(np.expand_dims(time_differences, axis=0), 4, axis=0)
    susp_min = susp_data.min()
    susp_max = susp_data.max()
    series_labels = ['left', 'right', 'front', 'rear']

    bar_plot(ax, data=susp_data, weights=time_data, num_bins=20,
             title='Average Suspension dislocation, min: {:.1f} mm, max: {:.1f} mm'.format(susp_min, susp_max),
             x_label='Suspension dislocation (mm)', y_label='Accumulated Time (s)', series_labels=series_labels)


def plot_height_over_dist(ax, session_data):
    distance = session_data[networking.Fields.distance.value]
    height = np.abs(session_data[networking.Fields.pos_y.value])
    ax.plot(distance, height, label='height')
    ax.set(xlabel='distance (m)', ylabel='height (m)',
           title='Track Elevation')
    ax.grid()


def plot_g_over_rpm(ax, session_data):

    data_gear = session_data[networking.Fields.gear.value]
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
        current_gear = session_data[networking.Fields.gear.value] == g
        full_throttle = session_data[networking.Fields.throttle.value] == 1.0
        interesting = np.logical_and(current_gear, full_throttle)

        g_force_lon = session_data[networking.Fields.g_force_lon.value, interesting]
        rpm = session_data[networking.Fields.rpm.value, interesting]
        throttle = session_data[networking.Fields.throttle.value, interesting]
        throttle_scaled = [t * scale for t in throttle]

        x_points += [rpm]
        y_points += [g_force_lon]
        scales += [throttle_scaled]

    scatter_plot(ax, x_points=x_points, y_points=y_points, title='G-force over RPM (full throttle)',
                 labels=labels, colors=colors, scales=scales, alphas=alphas, x_label='RPM', y_label='G-force X')


def plot_p_over_rpm(ax, session_data):

    data_gear = session_data[networking.Fields.gear.value]
    range_gears = list(set(data_gear))
    range_gears.sort()

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    scale = 50.0
    alphas = [0.5] * len(labels)
    colors = [static_colors[i] for i, g in enumerate(range_gears)]
    full_acceleration_mask = data_processing.get_full_acceleration_mask(session_data=session_data)

    rpm = session_data[networking.Fields.rpm.value]
    energy, kinetic_energy, potential_energy = data_processing.get_energy(session_data=session_data)
    times_steps = session_data[networking.Fields.lap_time.value]
    power = data_processing.derive_no_nan(x=energy, time_steps=times_steps) / 1000.0

    x_points = []
    y_points = []
    scales = []
    for gear in range_gears:
        current_gear = session_data[networking.Fields.gear.value] == gear
        interesting = np.logical_and(current_gear, full_acceleration_mask)

        x_points += [rpm[interesting]]
        y_points += [power[interesting]]
        scales += [np.ones_like(rpm[interesting]) * scale]

    scatter_plot(ax, x_points=x_points, y_points=y_points, title='Power over RPM (full throttle)',
                 labels=labels, colors=colors, scales=scales, alphas=alphas, x_label='RPM', y_label='Power [kW]')


def plot_p_over_vel(ax, session_data):

    data_gear = session_data[networking.Fields.gear.value]
    range_gears = list(set(data_gear))
    range_gears.sort()

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    scale = 50.0
    alphas = [0.5] * len(labels)
    colors = [static_colors[i] for i, g in enumerate(range_gears)]
    full_acceleration_mask = data_processing.get_full_acceleration_mask(session_data=session_data)

    energy, kinetic_energy, potential_energy = data_processing.get_energy(session_data=session_data)
    times_steps = session_data[networking.Fields.lap_time.value]
    power = data_processing.derive_no_nan(x=energy, time_steps=times_steps) / 1000.0

    x_points = []
    y_points = []
    scales = []
    for gear in range_gears:
        current_gear = session_data[networking.Fields.gear.value] == gear
        interesting = np.logical_and(current_gear, full_acceleration_mask)

        speed_ms = session_data[networking.Fields.speed_ms.value]
        x_points += [speed_ms[interesting]]
        y_points += [power[interesting]]
        scales += [np.ones_like(speed_ms[interesting]) * scale]

    scatter_plot(ax, x_points=x_points, y_points=y_points, title='Power over velocity (full throttle)',
                 labels=labels, colors=colors, scales=scales, alphas=alphas, x_label='Velocity [m/s]', y_label='Power [kW]')


def plot_g_over_throttle(ax, session_data):

    data_gear = session_data[networking.Fields.gear.value]
    range_gears = list(set(data_gear))
    range_gears.sort()

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    colors = [static_colors[i] for i, g in enumerate(range_gears)]
    scales = [25] * len(labels)
    alphas = [0.5] * len(labels)

    x_points = []
    y_points = []
    for i, g in enumerate(range_gears):
        current_gear = session_data[networking.Fields.gear.value] == g

        throttle = session_data[networking.Fields.throttle.value, current_gear]
        g_force_lon = session_data[networking.Fields.g_force_lon.value, current_gear]

        x_points += [throttle]
        y_points += [g_force_lon]

    scatter_plot(ax, x_points=x_points, y_points=y_points, title='G-force X over throttle',
                 labels=labels, colors=colors, scales=scales, alphas=alphas, x_label='throttle', y_label='G-force X')


def plot_v_over_rpm(ax, session_data):

    data_gear = session_data[networking.Fields.gear.value]
    range_gears = list(set(data_gear))
    range_gears.sort()

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    colors = [static_colors[i] for i, g in enumerate(range_gears)]
    scales = [25] * len(labels)
    alphas = [0.5] * len(labels)

    x_points = []
    y_points = []
    for i, g in enumerate(range_gears):
        current_gear = session_data[networking.Fields.gear.value] == g
        full_throttle = session_data[networking.Fields.throttle.value] == 1.0
        interesting = np.logical_and(current_gear, full_throttle)

        rpm = session_data[networking.Fields.rpm.value, interesting]
        speed_ms = session_data[networking.Fields.speed_ms.value, interesting]

        x_points += [rpm]
        y_points += [speed_ms]

    scatter_plot(ax, x_points=x_points, y_points=y_points, title='Speed over RPM (full throttle)',
                 labels=labels, colors=colors, scales=scales, alphas=alphas, x_label='RPM', y_label='Speed (m/s)')


def forward_over_2d_pos(ax, session_data):

    # if we take all data points, the plot is too crowded
    sample_rate = 10

    x, y = data_processing.get_2d_coordinates(session_data)
    x = x[::sample_rate]
    y = y[::sample_rate]
    x_min, x_middle, x_max = data_processing.get_min_middle_max(x)
    y_min, y_middle, y_max = data_processing.get_min_middle_max(y)

    diff = [x_max - x_min, y_max - y_min]
    diff_max = max(diff)

    pxy_normalized = data_processing.get_forward_dir_2d(session_data)
    vxy_normalized = data_processing.get_forward_vel_2d(session_data)
    pxy_normalized = pxy_normalized[:, ::sample_rate]
    vxy_normalized = vxy_normalized[:, ::sample_rate]

    # dot(dir, speed) = drift
    drift = list((pxy_normalized * vxy_normalized).sum(axis=0))
    drift_angle = np.arccos(drift)

    ax.plot(x, y, c='k')
    ax.quiver(x, y, pxy_normalized[0], pxy_normalized[1], drift_angle,
              angles='xy', scale_units='dots', scale=0.03, label='Forward dir', color='tab:purple')
    ax.quiver(x, y, vxy_normalized[0], vxy_normalized[1],
              angles='xy', scale_units='dots', scale=0.03, label='Forward vel', color='tab:red')
    lim_left = x_middle - diff_max * 0.6
    lim_right = x_middle + diff_max * 0.6
    if lim_left != lim_right:
        ax.set_xlim(lim_left, lim_right)
    lim_bottom = y_middle - diff_max * 0.6
    lim_top = y_middle + diff_max * 0.6
    if lim_bottom != lim_top:
        ax.set_ylim(lim_bottom, lim_top)
    ax.text(x[0], y[0], 'start')
    ax.text(x[-1], y[-1], 'finish')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.legend()


def wheel_speed_over_time(ax, session_data):

    lap_time = session_data[networking.Fields.lap_time.value]
    wsp_fl = session_data[networking.Fields.wsp_fl.value]
    wsp_fr = session_data[networking.Fields.wsp_fr.value]
    wsp_rl = session_data[networking.Fields.wsp_rl.value]
    wsp_rr = session_data[networking.Fields.wsp_rr.value]
    wsp_data = np.array([wsp_fl, wsp_fr, wsp_rl, wsp_rr])

    labels = ['front left', 'front right', 'rear left', 'rear right']
    x_points = np.array([lap_time] * len(wsp_data))
    y_points = np.array(wsp_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Wheel speed over lap time',
              labels=labels, alpha=0.5, x_label='Lap time (s)', y_label='Wheel speed (m/s)', min_max_annotations=True)


def wheel_speed_lr_fr_over_time(ax, session_data):

    lap_time = session_data[networking.Fields.lap_time.value]
    wsp_fl = session_data[networking.Fields.wsp_fl.value]
    wsp_fr = session_data[networking.Fields.wsp_fr.value]
    wsp_rl = session_data[networking.Fields.wsp_rl.value]
    wsp_rr = session_data[networking.Fields.wsp_rr.value]
    wsp_left_right = (wsp_fl + wsp_rl) * 0.5 - (wsp_fr + wsp_rr) * 0.5
    wsp_front_rear = (wsp_fl + wsp_fr) * 0.5 - (wsp_rl + wsp_rr) * 0.5
    wsp_data = np.array([wsp_left_right, wsp_front_rear])

    labels = ['left-right', 'front-rear']
    x_points = np.array([lap_time] * len(wsp_data))
    y_points = np.array(wsp_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Wheel speed difference over lap time', labels=labels,
              alpha=0.5, x_label='Lap time (s)', y_label='Wheel speed difference (m/s)', min_max_annotations=True)


def drift_over_speed(ax, session_data):

    steering = np.abs(session_data[networking.Fields.steering.value])
    speed_ms = session_data[networking.Fields.speed_ms.value]
    drift_angle_deg = data_processing.get_drift_angle(session_data)
    drift_angle_deg_der = data_processing.derive_no_nan(
        drift_angle_deg, time_steps=session_data[networking.Fields.lap_time.value])

    # filter very slow parts
    fast_enough = speed_ms > 1.0  # m/s
    steering = steering[fast_enough]
    speed_ms = speed_ms[fast_enough]
    # drift_angle_deg = drift_angle_deg[fast_enough]
    drift_angle_deg_der = drift_angle_deg_der[fast_enough]

    colors = [steering]
    scales = [25]
    alphas = [0.5]
    labels = ['drift over steer']

    # scatter_plot(ax, x_points=[speed_ms], y_points=[drift_angle_deg],
    #              title='Drift over speed (steering as color)',
    #              labels=labels, colors=colors, scales=scales, alphas=alphas,
    #              x_label='Speed (m/s)', y_label='Drift angle (deg)')
    scatter_plot(ax, x_points=[speed_ms], y_points=[drift_angle_deg_der],
                 title='Drift change over speed (steering as color)',
                 labels=labels, colors=colors, scales=scales, alphas=alphas,
                 x_label='Speed (m/s)', y_label='Drift angle (deg/s)')


def drift_angle_bars(ax, session_data):

    time_differences = data_processing.differences(session_data[networking.Fields.lap_time.value])
    # prevent negative times due to next lap
    time_differences[time_differences < 0.0] = np.finfo(time_differences.dtype).eps
    speed_ms = session_data[networking.Fields.speed_ms.value]
    drift_angle_deg = data_processing.get_drift_angle(session_data)

    # filter very slow parts
    fast_enough = speed_ms > 1.0  # m/s
    drift_angle_deg = drift_angle_deg[fast_enough]
    time_differences = time_differences[fast_enough]

    # filter out rare extreme values
    outlier_threshold = np.nanpercentile(drift_angle_deg, 99)
    usual_values = drift_angle_deg < outlier_threshold
    drift_angle_deg = drift_angle_deg[usual_values]
    time_differences = time_differences[usual_values]

    series_labels = ['']

    bar_plot(ax, data=[drift_angle_deg], weights=[time_differences], num_bins=10, title='Drift Angle Histogram',
             x_label='Drift Angle (deg)', y_label='Accumulated Time (s)', series_labels=series_labels)


def drift_angle_change_bars(ax, session_data):

    time_differences = data_processing.differences(session_data[networking.Fields.lap_time.value])
    # prevent negative times due to next lap
    time_differences[time_differences < 0.0] = np.finfo(time_differences.dtype).eps
    speed_ms = session_data[networking.Fields.speed_ms.value]
    drift_angle_deg = data_processing.get_drift_angle(session_data)
    drift_angle_deg_der = data_processing.derive_no_nan(
        drift_angle_deg, time_steps=session_data[networking.Fields.lap_time.value])

    # filter very slow parts
    fast_enough = speed_ms > 1.0  # m/s
    drift_angle_deg_der = drift_angle_deg_der[fast_enough]
    drift_angle_deg_der = np.abs(drift_angle_deg_der)

    # filter out rare extreme values
    outlier_threshold = np.nanpercentile(drift_angle_deg_der, 99)
    usual_values = drift_angle_deg_der < outlier_threshold
    drift_angle_deg_der = drift_angle_deg_der[usual_values]

    time_differences = time_differences[fast_enough]
    time_differences = time_differences[usual_values]
    series_labels = ['']

    bar_plot(ax, data=[drift_angle_deg_der], weights=[time_differences], num_bins=10,
             title='Drift Angle Change Histogram',
             x_label='Drift Angle Change (deg/s)', y_label='Accumulated Time (s)', series_labels=series_labels)


def rotation_over_time(ax, session_data):

    lap_time = session_data[networking.Fields.lap_time.value]

    forward_local_xyz = data_processing.get_forward_dir_3d(session_data)
    sideward_local_xyz = data_processing.get_sideward_dir_3d(session_data)

    def get_vertical_angle_dislocation(dirs):
        global_dirs = data_processing.normalize_3d_vectors(
            dirs[0], dirs[1], np.zeros_like(dirs[2]))
        dirs_dislocation = (dirs * global_dirs).sum(axis=0)
        dirs_angle = np.arccos(dirs_dislocation)
        dirs_angle[dirs[2] < 0.0] = -dirs_angle[dirs[2] < 0.0]
        dirs_angle_deg = np.rad2deg(dirs_angle)
        return dirs_angle_deg

    sideward_angle_deg = get_vertical_angle_dislocation(sideward_local_xyz)
    forward_angle_deg = get_vertical_angle_dislocation(forward_local_xyz)

    labels = ['Sideward Rotation Angle', 'Forward Rotation Angle']
    x_points = np.array([lap_time] * len(labels))
    y_points = np.array([sideward_angle_deg, forward_angle_deg])

    line_plot(ax, x_points=x_points, y_points=y_points,
              title='Rotation Angles over Lap Time',
              labels=labels, alpha=0.5, x_label='Lap Time (s)',
              y_label='Angle (deg)', min_max_annotations=True)


def suspension_lr_fr_angles_over_time(ax, session_data):
    lap_time = session_data[networking.Fields.lap_time.value]
    susp_fl = session_data[networking.Fields.susp_fl.value]
    susp_fr = session_data[networking.Fields.susp_fr.value]
    susp_rl = session_data[networking.Fields.susp_rl.value]
    susp_rr = session_data[networking.Fields.susp_rr.value]
    susp_left_right = (susp_fl + susp_rl) * 0.5 - (susp_fr + susp_rr) * 0.5
    susp_front_rear = (susp_fl + susp_fr) * 0.5 - (susp_rl + susp_rr) * 0.5

    def height_diff_to_angle(displacement, dist):
        angle = np.arcsin(displacement / dist)
        return np.rad2deg(angle)

    # approximately wheelbase and track for Audi Quattro S1 -> should be accurate enough for other cars
    angle_left_right = height_diff_to_angle(susp_left_right / 1000.0, 1.800)
    angle_front_rear = height_diff_to_angle(susp_front_rear / 1000.0, 2.200)

    angle_data = np.array([-angle_left_right, -angle_front_rear])

    labels = ['left-right angle', 'front-rear angle']
    x_points = np.array([lap_time] * len(angle_data))
    y_points = np.array(angle_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Suspension dislocation angle over lap time',
              labels=labels, alpha=0.5, x_label='Lap time (s)',
              y_label='Suspension dislocation angle (deg)', min_max_annotations=True)
