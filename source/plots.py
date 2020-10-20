from typing import List
import functools
import os

import matplotlib
# TkAgg with default tk leads to the matplotlib mainloop not terminating although all plot windows are closed
matplotlib.use('qt5agg')  # MUST BE CALLED BEFORE IMPORTING plt
import matplotlib.pyplot as plt
import numpy as np
import scipy  # don't remove this or pyinstaller may fail to include this
from scipy.stats import binned_statistic

from source import plot_data as pd
from source import data_processing

static_colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
                 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']


# TODO: - correlation between power output and wheel speed (slip)
# TODO: - show oversteer vs understeer
# TODO: - check all correlations
# TODO: - show crashes in track overview (num crashes as legend) -> track overview in essential plots
# TODO: - continuous integration
# TODO: - put socket I/O in extra thread (add all those things in the message queue?)
# TODO: - add rotation energy to power plots?
# TODO: - add wheel rotation energy to power plots?
# TODO: - analyze slip
# TODO: - Fourier transform on suspension to check dampers?
# TODO: - estimate limit and Linear Region of Tire Force (https://www.paradigmshiftracing.com/racing-basics/racing-and-motorsports-terms-glossary#/)
# TODO: - https://www.youtube.com/watch?v=5xw8DJY7aZQ
# TODO: - https://www.youtube.com/watch?v=5U2t_2yberY
# TODO: - https://www.youtube.com/watch?v=Y6f4ar0IHwQ


def save_plot(title: str, title_post_fix: str, fig):

    path = r'.'
    file_path = os.path.join(path, title + title_post_fix + '.png')
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    fig.set_size_inches((16, 9), forward=False)
    plt.savefig(file_path, dpi=150, facecolor='w', edgecolor='w',
                orientation='landscape', transparent=False, bbox_inches='tight',  pad_inches=0.1)


def plot_main(plot_data: pd.PlotData, car_name: str, track_name: str, additional_plots=False):

    if plot_data.run_time.shape[0] > 0:
        title_post_fix = ' - {} on {}'.format(car_name, track_name)

        # experimental 3D plot. very bad performance.
        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')
        # fig.canvas.set_window_title('3D positions' + title_post_fix)
        # plot_gear_over_3d_pos(ax, plot_data)

        if additional_plots:
            # simple overview of track with height profile and 2D-plot with used gear from above
            fig, ax = plt.subplots(1, 2)
            fig.canvas.set_window_title('Map Basics' + title_post_fix)
            plot_height_over_dist(ax[0], plot_data)
            plot_gear_over_2d_pos(ax[1], plot_data)
            # save_plot('Map Basics', title_post_fix, fig)

        if additional_plots:
            # see the car's energy on the track.
            # this is pretty much the same as velocity + height so not much insight here.
            # this is somewhat useful for debugging power plots but not very useful on its own
            fig, ax = plt.subplots(2, 1, sharex='all')
            fig.canvas.set_window_title('Energy and Power' + title_post_fix)
            energy_over_time(ax[0], plot_data)
            power_over_time(ax[1], plot_data)
            # save_plot('Energy and Power', title_post_fix, fig)

        # see the car's energy on the track. this is pretty much the same as velocity + height so not much insight here.
        # fig, ax = plt.subplots(1, 1)
        # fig.canvas.set_window_title('Energy' + title_post_fix)
        # plot_energy_over_2d_pos(ax, plot_data)

        # see how much you use which gear. the most-used RPM interval should be around the optimal RPM
        fig, ax = plt.subplots(1, 1)
        fig.canvas.set_window_title('RPM Histogram per Gear' + title_post_fix)
        gear_rpm_bars(ax, plot_data)
        # save_plot('RPM Histogram per Gear', title_post_fix, fig)

        # overlaps on the y axis mean the driver shifts too early or too late and/or that the gears are too close.
        fig, ax = plt.subplots(1, 1)
        fig.canvas.set_window_title('Speed over RPM' + title_post_fix)
        plot_v_over_rpm(ax, plot_data)
        # save_plot('Speed over RPM', title_post_fix, fig)

        if additional_plots:
            # show the power output over RPM and velocity.
            # this is meant to show the maximum power output of the engine and the optimum RPM per gear.
            fig, ax = plt.subplots(1, 1, sharey='all')
            fig.canvas.set_window_title('Power Output' + title_post_fix)
            plot_p_over_rpm(ax, plot_data)
            # plot_p_over_vel(ax[1], plot_data)
            # save_plot('Power Output', title_post_fix, fig)

        if additional_plots:
            # the benefits of this plot are unclear. the idea is to see the max turning rate.
            fig, ax = plt.subplots(1, 1)
            fig.canvas.set_window_title('Forward G-Force' + title_post_fix)
            plot_g_over_rpm(ax, plot_data)
            # plot_g_over_throttle(ax[1], plot_data)
            # save_plot('Forward G-Force', title_post_fix, fig)

        if additional_plots:
            # see the typical drift angle.
            # normal distribution indicates control over the car.
            # common, large drift angles indicate less control and perhaps bad suspension settings
            fig, ax = plt.subplots(1, 3)
            fig.canvas.set_window_title('Drift at 2D positions ' + title_post_fix)
            forward_over_2d_pos(ax[0], plot_data)
            drift_angle_bars(ax[1], plot_data)
            drift_angle_change_bars(ax[2], plot_data)
            # drift_over_speed(ax[1][1], plot_data)
            # save_plot('Drift at 2D positions', title_post_fix, fig)

        # key plot for tuning the suspension height, dampers and springs
        fig, ax = plt.subplots(1, 1)
        fig.canvas.set_window_title('Suspension' + title_post_fix)
        suspension_bars(ax, plot_data)
        # suspension_l_r_f_r_bars(ax[1], plot_data)
        # save_plot('Suspension', title_post_fix, fig)

        if additional_plots:
            # mostly interesting to check slip caused by differentials.
            fig, ax = plt.subplots(2, 1, sharex='all')
            fig.canvas.set_window_title('Wheel Speed' + title_post_fix)
            wheel_speed_over_time(ax[0], plot_data)
            inputs_over_time(ax[1], plot_data)
            # save_plot('Wheel Speed', title_post_fix, fig)

        # this shows how much the car's body rotates because of track irregularities
        fig, ax = plt.subplots(3, 1, sharex='all')
        fig.canvas.set_window_title('Rotation vs Suspension' + title_post_fix)
        rotation_over_time(ax[0], plot_data)
        suspension_lr_fr_angles_over_time(ax[1], plot_data)
        suspension_l_r_f_r_over_time(ax[2], plot_data)
        # save_plot('Rotation vs Suspension', title_post_fix, fig)

        # mostly for tuning the dampers, but also springs and stabilizers
        fig, ax = plt.subplots(3, 1, sharex='all')
        fig.canvas.set_window_title('Ground Contact' + title_post_fix)
        ground_contact_over_time(ax[0], plot_data)
        suspension_over_time(ax[1], plot_data)
        suspension_vel_over_time(ax[2], plot_data)
        # save_plot('Ground Contact', title_post_fix, fig)

        # TODO: find maximum turn rate over velocity, depending on full steering, ground contact
        plt.show()


def plot_over_3d_pos(ax, plot_data: pd.PlotData, scale, color, slicing):

    x_min, x_middle, x_max = data_processing.get_min_middle_max(plot_data.pos_x)
    y_min, y_middle, y_max = data_processing.get_min_middle_max(plot_data.pos_y)
    z_min, z_middle, z_max = data_processing.get_min_middle_max(plot_data.pos_z)

    diff = np.array([x_max - x_min, y_max - y_min, z_max - z_min])
    diff_max = np.max(diff)
    # ax = fig.add_subplot(111, projection='3d')
    ax.scatter(plot_data.pos_x[::slicing], plot_data.pos_y[::slicing], plot_data.pos_z[::slicing], marker='o',
               s=scale[::slicing], c=color[::slicing], cmap='plasma')
    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.set_zlabel('Y')
    ax.text(plot_data.pos_x[0], plot_data.pos_y[0], plot_data.pos_z[0], 'start')
    ax.text(plot_data.pos_x[-1], plot_data.pos_y[-1], plot_data.pos_z[-1], 'finish')
    ax.set_xlim(x_middle - diff_max * 0.6, x_middle + diff_max * 0.6)
    ax.set_ylim(y_middle - diff_max * 0.6, y_middle + diff_max * 0.6)
    ax.set_zlim(z_middle - diff_max * 0.1, z_middle + diff_max * 1.1)
    return ax


def plot_over_2d_pos(ax, plot_data: pd.PlotData, lines_x, lines_y, scale, alpha, title, labels):
    x_min, x_middle, x_max = data_processing.get_min_middle_max(plot_data.pos_x)
    y_min, y_middle, y_max = data_processing.get_min_middle_max(plot_data.pos_y)

    diff = np.array([x_max - x_min, y_max - y_min])
    diff_max = np.max(diff)

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
    ax.text(plot_data.pos_x[0], plot_data.pos_y[0], 'start')
    ax.text(plot_data.pos_x[-1], plot_data.pos_y[-1], 'finish')
    ax.set_title(title)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')


def scatter_plot(ax: plt.axes, x_points: List, y_points: List, title: str, labels: List[str],
                 colors: List, scales: List, alphas: List,
                 x_label, y_label, plot_mean=True, plot_polynomial=True):

    for i in range(len(x_points)):
        ax.scatter(x=x_points[i], y=y_points[i], c=colors[i], s=scales[i], alpha=alphas[i], label=labels[i])
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    if labels is not None and len(labels) > 1:
        ax.legend()

    if plot_mean:
        x_series_mean = [np.mean(p) for p in x_points]
        y_series_mean = [np.mean(p) for p in y_points]
        ax.scatter(x_series_mean, y_series_mean, c=colors, s=200.0, alpha=1.0, marker='X', edgecolors='k')

    if plot_polynomial:
        for i in range(len(x_points)):
            if x_points[i].shape[0] > 0:
                x_min = np.min(x_points[i])
                x_max = np.max(x_points[i])
                try:
                    poly_coefficients = np.polyfit(x_points[i], y_points[i], 3)
                    poly = np.poly1d(poly_coefficients)
                    x_poly = np.linspace(x_min, x_max, 500)
                    y_poly = poly(x_poly)
                    ax.plot(x_poly, y_poly, '-', c=colors[i])
                except np.linalg.LinAlgError as _:
                    pass  # sometimes LinAlgError("SVD did not converge in Linear Least Squares"), maybe first gear


def line_plot(ax, x_points, y_points, title, labels, alpha, x_label, y_label, colors=None,
              flip_y=False, min_max_annotations=True):

    x_points_cat = np.concatenate(x_points.copy())
    y_points_cat = np.concatenate(y_points.copy())
    y_points_no_nan = y_points_cat.copy()
    y_points_no_nan_mean = np.nanmean(y_points_no_nan)
    y_points_no_nan[np.isnan(y_points_no_nan)] = y_points_no_nan_mean
    y_points_no_nan[np.isinf(y_points_no_nan)] = y_points_no_nan_mean
    arg_y_max = np.argmax(y_points_no_nan)
    arg_y_min = np.argmin(y_points_no_nan)

    x_min = x_points_cat[arg_y_min]
    y_min = y_points_cat[arg_y_min]
    x_max = x_points_cat[arg_y_max]
    y_max = y_points_cat[arg_y_max]

    if colors is not None:
        colors = np.array(colors)

    for i, g in enumerate(x_points):
        if colors is None:
            ax.plot(x_points[i], y_points[i], alpha=alpha)
        elif len(colors.shape) == 1 and colors.shape == (3,):
            ax.plot(x_points[i], y_points[i], alpha=alpha, color=colors)
        elif len(colors.shape) == 2 and colors.shape[-1] == 3:
            ax.plot(x_points[i], y_points[i], alpha=alpha, color=colors[i])
        else:
            raise ValueError('Invalid color: {}'.format(colors))

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
        bbox = dict(boxstyle='round', fc='0.8')
        arrow_props = dict(arrowstyle='->', connectionstyle='angle,angleA=0,angleB=90,rad=10')
        ax.annotate('max: {:.2f}'.format(y_max), (x_max, y_max),
                    xytext=(x_offset, y_offset), textcoords='offset points', bbox=bbox, arrowprops=arrow_props)
        ax.annotate('min: {:.2f}'.format(y_min), (x_min, y_min),
                    xytext=(x_offset, -y_offset), textcoords='offset points', bbox=bbox, arrowprops=arrow_props)

    # invert y axis and pad
    y_diff = y_max - y_min
    if not flip_y:
        ax.set_ylim(y_min - y_diff * 0.1, y_max + y_diff * 0.1)
    else:
        ax.set_ylim(y_max + y_diff * 0.1, y_min - y_diff * 0.1)


def histogram_plot(ax, samples, title, x_label, y_label, labels=None,
                   min_val=None, max_val=None, num_bins=20, color=None):

    if min_val is None:
        min_val = samples.min()
    if max_val is None:
        max_val = samples.max()
    ax.hist(list(samples), num_bins, color=color, label=labels)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xlim(min_val, max_val)
    if labels is not None and len(labels) > 1:
        ax.legend(labels)
    ax.set_title(title)


def bar_plot(ax, data, weights, num_bins=20,
             title=None, x_label=None, y_label=None, series_labels=None, tick_labels=None, highlight_value=None):

    if len(data) == 0 or data[0].size == 0:
        return

    data_min = min([d.min() for d in data])
    data_max = max([d.max() for d in data])
    bin_edges = np.linspace(start=data_min, stop=data_max, num=num_bins+1)

    x = np.arange(num_bins)
    num_series = len(series_labels)

    default_width = 0.8
    width = default_width / (float(num_series) + 1)
    for i in range(num_series):
        data_bin_sum, _, _ = \
            binned_statistic(data[i], weights[i], statistic='sum', bins=bin_edges)
        tick_labels = ['{:.0f} to\n {:.0f}'.format(bin_edges[0 + i], bin_edges[1 + i])
                       for i in range(bin_edges.shape[0] - 1)]

        ax.bar(x + (0.5 + i - float(num_series) * 0.5) * width, data_bin_sum, width, label=series_labels[i])

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    if series_labels is not None and num_series > 1:
        ax.legend(series_labels)
    ax.set_xticks(x)
    ax.set_xticklabels(tick_labels)
    ax.set_title(title)

    if highlight_value is not None:
        bin_edges_smaller = bin_edges <= highlight_value
        highlight_bin = np.sum(bin_edges_smaller) - 1
        highlight_bin_left_edge = highlight_bin + (-float(num_series) * 0.5) * width
        highlight_bin_right_edge = highlight_bin + (float(num_series) * 0.5) * width
        ax.axvspan(highlight_bin_left_edge, highlight_bin_right_edge, color='green', alpha=0.25)


def plot_optimal_rpm_region(ax: matplotlib.axes, plot_data: pd.PlotData):

    optimal_rpm, optimal_rpm_range_min, optimal_rpm_range_max = data_processing.get_optimal_rpm(plot_data=plot_data)
    if optimal_rpm is not None:
        ax.axvline(optimal_rpm, color='green', alpha=0.5)
    if optimal_rpm_range_min is not None and optimal_rpm_range_max is not None:
        ax.axvspan(optimal_rpm_range_min, optimal_rpm_range_max, color='green', alpha=0.25)


def plot_gear_over_3d_pos(ax, plot_data: pd.PlotData):

    slicing = 100
    dx, dy, dz = data_processing.get_forward_dir_3d(plot_data)

    rpm = plot_data.rpm
    rpm_max = np.max(rpm)
    scale = 50.0
    rpm_normalized_scaled = rpm / rpm_max * scale
    gear = plot_data.gear
    gear_max = max(gear)
    gear_normalized_scaled = gear / gear_max

    ax = plot_over_3d_pos(ax, plot_data=plot_data, scale=rpm_normalized_scaled,
                          color=gear_normalized_scaled, slicing=slicing)
    ax.quiver(plot_data.pos_x[::slicing], plot_data.pos_y[::slicing], plot_data.pos_z[::slicing],
              dx[::slicing], dy[::slicing], dz[::slicing], length=100.0, normalize=True)


def plot_gear_over_2d_pos(ax, plot_data: pd.PlotData):

    range_gears = np.unique(plot_data.gear)
    range_gears = np.sort(range_gears)

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    lines_x = []
    lines_y = []
    for i, g in enumerate(range_gears):
        current_gear = plot_data.gear == g
        lines_x += [plot_data.pos_x[current_gear]]
        lines_y += [plot_data.pos_y[current_gear]]

    plot_over_2d_pos(ax, plot_data=plot_data, lines_x=lines_x, lines_y=lines_y,
                     scale=10, alpha=0.5, title='Gear at 2D positions', labels=labels)


def plot_energy_over_2d_pos(ax, plot_data: pd.PlotData):

    scale_factor = 100.0
    range_gears = np.unique(plot_data.gear)
    range_gears = np.sort(range_gears)

    energy, kinetic_energy, potential_energy = data_processing.get_energy(plot_data=plot_data)
    energy_truncated = energy - np.min(energy)
    energy_normalized = energy_truncated / np.max(energy_truncated)

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    lines_x = []
    lines_y = []
    scales = []
    for i, g in enumerate(range_gears):
        current_gear = plot_data.gear == g
        lines_x += [plot_data.pos_x[current_gear]]
        lines_y += [plot_data.pos_y[current_gear]]
        scales += [energy_normalized[current_gear] * scale_factor]

    plot_over_2d_pos(ax, plot_data=plot_data, lines_x=lines_x, lines_y=lines_y,
                     scale=scales, alpha=0.5, title='Gear at 2D positions, scaled by energy', labels=labels)


def gear_rpm_bars(ax, plot_data: pd.PlotData):

    time_differences = data_processing.differences(plot_data.run_time, True)
    rpm = plot_data.rpm
    range_gears = np.unique(plot_data.gear)
    range_gears = np.sort(range_gears)

    total_time = time_differences.sum()
    gear_ids = [plot_data.gear == gear for gear in range_gears]
    gear_times = [time_differences[g] for g in gear_ids]
    gear_rpms = [rpm[g] for g in gear_ids]
    gear_time_sums = [gt.sum() for gt in gear_times]
    if total_time == 0.0:
        gear_ratio = [0.0] * len(gear_time_sums)
    else:
        gear_ratio = [gts / total_time for gts in gear_time_sums]
    series_labels = ['Gear {0}: {1:.1f}%'.format(
        int(g), gear_ratio[gi] * 100.0) for gi, g in enumerate(range_gears)]

    optimal_rpm, optimal_rpm_range_min, optimal_rpm_range_max = data_processing.get_optimal_rpm(plot_data=plot_data)
    bar_plot(ax, data=gear_rpms, weights=gear_times, num_bins=16,
             title='Gear RPM', x_label='RPM', y_label='Accumulated Time (s)', series_labels=series_labels,
             highlight_value=optimal_rpm)


def energy_over_time(ax, plot_data: pd.PlotData):
    race_time = plot_data.run_time
    energy, kinetic_energy, potential_energy = data_processing.get_energy(plot_data=plot_data)
    energy_data = np.array([energy, kinetic_energy, potential_energy])

    labels = ['Energy (kJ)', 'Kinetic Energy (kJ)', 'Potential Energy (kJ)']
    y_points = energy_data
    x_points = np.array([race_time] * y_points.shape[0])

    line_plot(ax, x_points=x_points, y_points=y_points, title='Energy over time',
              labels=labels, alpha=0.5, x_label='Time (s)', y_label='Energy (kJ)', min_max_annotations=False)


def power_over_time(ax, plot_data: pd.PlotData):
    race_time = plot_data.run_time
    energy, kinetic_energy, potential_energy = data_processing.get_energy(plot_data=plot_data)
    # energy is dominated by potential energy -> take only kinetic energy
    power = data_processing.derive_no_nan(kinetic_energy, race_time)
    full_acceleration = data_processing.get_full_acceleration_mask(plot_data=plot_data)
    not_full_acceleration = np.logical_not(full_acceleration)
    power_full_acceleration = power.copy()
    power_full_acceleration[not_full_acceleration] = 0.0
    power_not_full_acceleration = power.copy()
    power_not_full_acceleration[full_acceleration] = 0.0
    power_data = np.array([power_full_acceleration, power_not_full_acceleration])
    power_data_mean = [np.mean(d) for d in power_data]

    labels = ['Power at full throttle (kW)', 'Power otherwise (kW)']
    labels = [l + ', mean: {:.1f}'.format(power_data_mean[li]) for li, l in enumerate(labels)]
    y_points = power_data
    x_points = np.array([race_time] * y_points.shape[0])

    line_plot(ax, x_points=x_points, y_points=y_points, title='Power over time',
              labels=labels, alpha=0.5, x_label='Time (s)', y_label='Power (kW)', min_max_annotations=False)


def inputs_over_time(ax, plot_data: pd.PlotData):
    race_time = plot_data.run_time
    throttle = plot_data.throttle
    brakes = plot_data.brakes
    steering = plot_data.steering
    input_data = np.array([throttle, brakes, steering])

    labels = ['Throttle', 'Brakes', 'Steering']
    y_points = input_data
    x_points = np.array([race_time] * y_points.shape[0])

    line_plot(ax, x_points=x_points, y_points=y_points, title='Inputs over time',
              labels=labels, alpha=0.5, x_label='Time (s)', y_label='Inputs', min_max_annotations=False)


def suspension_over_time(ax, plot_data: pd.PlotData):
    race_time = plot_data.run_time
    susp_fl = plot_data.susp_fl
    susp_fr = plot_data.susp_fr
    susp_rl = plot_data.susp_rl
    susp_rr = plot_data.susp_rr
    susp_data = np.array([susp_fl, susp_fr, susp_rl, susp_rr])
    susp_data_stdev = [np.sqrt(np.var(d)) for d in susp_data]

    labels = ['Front left', 'Front right', 'Rear left', 'Rear right']
    labels = [l + ', stdev: {:.1f}'.format(susp_data_stdev[li]) for li, l in enumerate(labels)]
    y_points = susp_data
    x_points = np.array([race_time] * y_points.shape[0])

    line_plot(ax, x_points=x_points, y_points=y_points, title='Suspension dislocation over time',
              labels=labels, alpha=0.5, x_label='Time (s)', y_label='Suspension dislocation (mm)',
              flip_y=False, min_max_annotations=True)


def suspension_lr_fr_over_time(ax, plot_data: pd.PlotData):
    race_time = plot_data.run_time
    susp_fl = plot_data.susp_fl
    susp_fr = plot_data.susp_fr
    susp_rl = plot_data.susp_rl
    susp_rr = plot_data.susp_rr
    susp_left_right = (susp_fl + susp_rl) * 0.5 - (susp_fr + susp_rr) * 0.5
    susp_front_rear = (susp_fl + susp_fr) * 0.5 - (susp_rl + susp_rr) * 0.5
    susp_data = np.array([susp_left_right, susp_front_rear])
    susp_data_stdev = [np.sqrt(np.var(d)) for d in susp_data]

    labels = ['Left-right', 'Front-rear']
    labels = [l + ', stdev: {:.1f}'.format(susp_data_stdev[li]) for li, l in enumerate(labels)]
    x_points = np.array([race_time] * len(susp_data))
    y_points = np.array(susp_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Suspension dislocation difference over time',
              labels=labels, alpha=0.5, x_label='Time (s)',
              y_label='Suspension dislocation difference (mm)', flip_y=True, min_max_annotations=True)


def suspension_l_r_f_r_over_time(ax, plot_data: pd.PlotData):

    race_time = plot_data.run_time
    susp_fl = plot_data.susp_fl
    susp_fr = plot_data.susp_fr
    susp_rl = plot_data.susp_rl
    susp_rr = plot_data.susp_rr
    susp_left = (susp_fl + susp_rl) * 0.5
    susp_right = (susp_fr + susp_rr) * 0.5
    susp_front = (susp_fl + susp_fr) * 0.5
    susp_rear = (susp_rl + susp_rr) * 0.5
    susp_data = np.array([susp_left, susp_right, susp_front, susp_rear])
    susp_data_stdev = [np.sqrt(np.var(d)) for d in susp_data]

    labels = ['Left', 'Right', 'Front', 'Rear']
    labels = [l + ', stdev: {:.1f}'.format(susp_data_stdev[li]) for li, l in enumerate(labels)]
    x_points = np.array([race_time] * len(susp_data))
    y_points = np.array(susp_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Average suspension compression over time',
              labels=labels, alpha=0.5, x_label='Time (s)',
              y_label='Suspension compression (mm)', flip_y=False, min_max_annotations=True)


def suspension_vel_derived_l_r_f_r_over_time(ax, plot_data: pd.PlotData):

    race_time = plot_data.run_time
    susp_fl = plot_data.susp_fl
    susp_fr = plot_data.susp_fr
    susp_rl = plot_data.susp_rl
    susp_rr = plot_data.susp_rr
    susp_data = [susp_fl, susp_fr, susp_rl, susp_rr]
    susp_data = [data_processing.derive_no_nan(susp, race_time) for susp in susp_data]
    susp_data = np.array(susp_data)
    susp_data_stdev = [np.sqrt(np.var(d)) for d in susp_data]

    labels = ['Front left', 'Front right', 'Rear left', 'Rear right']
    labels = [l + ', stdev: {:.1f}'.format(susp_data_stdev[li]) for li, l in enumerate(labels)]
    x_points = np.array([race_time] * len(susp_data))
    y_points = np.array(susp_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Suspension velocity derived over time',
              labels=labels, alpha=0.5, x_label='Time (s)',
              y_label='Suspension velocity derived (mm/s)', flip_y=True, min_max_annotations=True)


def suspension_vel_der_diff_l_r_f_r_over_time(ax, plot_data: pd.PlotData):

    race_time = plot_data.run_time
    susp_fl = plot_data.susp_fl
    susp_fr = plot_data.susp_fr
    susp_rl = plot_data.susp_rl
    susp_rr = plot_data.susp_rr
    susp_data = [susp_fl, susp_fr, susp_rl, susp_rr]
    susp_data = [data_processing.derive_no_nan(susp, race_time) for susp in susp_data]

    susp_vel_fl = plot_data.susp_vel_fl
    susp_vel_fr = plot_data.susp_vel_fr
    susp_vel_rl = plot_data.susp_vel_rl
    susp_vel_rr = plot_data.susp_vel_rr
    susp_vel = [susp_vel_fl, susp_vel_fr, susp_vel_rl, susp_vel_rr]

    susp_data = np.array(susp_data) - np.array(susp_vel)
    susp_data_stdev = [np.sqrt(np.var(d)) for d in susp_data]

    labels = ['Front left', 'Front right', 'Rear left', 'Rear right']
    labels = [l + ', stdev: {:.1f}'.format(susp_data_stdev[li]) for li, l in enumerate(labels)]
    x_points = np.array([race_time] * len(susp_data))
    y_points = np.array(susp_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Suspension velocity derived over time',
              labels=labels, alpha=0.5, x_label='Time (s)',
              y_label='Suspension velocity derived - given (mm/s)', flip_y=True, min_max_annotations=True)


def suspension_bars(ax, plot_data: pd.PlotData):

    race_time = plot_data.run_time
    time_differences = data_processing.differences(race_time, True)
    susp_fl = plot_data.susp_fl
    susp_fr = plot_data.susp_fr
    susp_rl = plot_data.susp_rl
    susp_rr = plot_data.susp_rr
    susp_data = np.array([susp_fl, susp_fr, susp_rl, susp_rr])
    time_data = np.repeat(np.expand_dims(time_differences, axis=0), 4, axis=0)
    susp_min = np.min(susp_data)
    susp_max = np.max(susp_data)
    susp_max_ids = (susp_max == susp_data)
    series_labels = ['Front left', 'Front right', 'Rear left', 'Rear right']
    series_labels = [l + ', bump stops hit: {:.1f} s'.format(time_differences[susp_max_ids[li]].sum())
              for li, l in enumerate(series_labels)]

    bar_plot(ax, data=susp_data, weights=time_data, num_bins=20,
             title='Suspension compression, min: {:.1f} mm, max: {:.1f} mm'.format(susp_min, susp_max),
             x_label='Suspension compression (mm)', y_label='Accumulated Time (s)', series_labels=series_labels)


def suspension_l_r_f_r_bars(ax, plot_data: pd.PlotData):

    race_time = plot_data.run_time
    time_differences = data_processing.differences(race_time, True)
    susp_fl = plot_data.susp_fl
    susp_fr = plot_data.susp_fr
    susp_rl = plot_data.susp_rl
    susp_rr = plot_data.susp_rr
    susp_left = (susp_fl + susp_rl) * 0.5
    susp_right = (susp_fr + susp_rr) * 0.5
    susp_front = (susp_fl + susp_fr) * 0.5
    susp_rear = (susp_rl + susp_rr) * 0.5
    susp_data = np.array([susp_left, susp_right, susp_front, susp_rear])
    time_data = np.repeat(np.expand_dims(time_differences, axis=0), 4, axis=0)
    susp_min = np.min(susp_data)
    susp_max = np.max(susp_data)
    series_labels = ['Left', 'Right', 'Front', 'Rear']

    bar_plot(ax, data=susp_data, weights=time_data, num_bins=20,
             title='Average Suspension compression, min: {:.1f} mm, max: {:.1f} mm'.format(susp_min, susp_max),
             x_label='Suspension compression (mm)', y_label='Accumulated Time (s)', series_labels=series_labels)


def plot_height_over_dist(ax, plot_data: pd.PlotData):
    distance = plot_data.distance
    height = np.abs(plot_data.pos_z)
    ax.plot(distance, height, label='Height')
    ax.set(xlabel='Distance (m)', ylabel='Height (m)',
           title='Track Elevation')
    ax.grid()


def plot_g_over_rpm(ax: matplotlib.axes, plot_data: pd.PlotData):

    range_gears = np.unique(plot_data.gear)
    range_gears = np.sort(range_gears)
    range_gears = range_gears[range_gears > 0.0]

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    scale = 50.0
    alphas = [0.5] * len(labels)
    colors = [static_colors[i] for i, g in enumerate(range_gears)]

    full_acceleration_mask = data_processing.get_full_acceleration_mask(plot_data=plot_data)

    x_points = []
    y_points = []
    scales = []
    for g in range_gears:
        current_gear = plot_data.gear == g
        not_close_to_gear_changes = np.logical_not(
            data_processing.get_gear_shift_mask(plot_data=plot_data, shift_time_ms=100.0))
        full_in_current_gear = np.logical_and(not_close_to_gear_changes, current_gear)
        interesting = np.logical_and(full_in_current_gear, full_acceleration_mask)

        g_force_lon = plot_data.g_force_lon[interesting]
        rpm = plot_data.rpm[interesting]
        throttle = plot_data.throttle[interesting]
        throttle_scaled = [t * scale for t in throttle]

        x_points += [rpm]
        y_points += [g_force_lon]
        scales += [throttle_scaled]

    scatter_plot(ax, x_points=x_points, y_points=y_points, title='G-force over RPM (full throttle)',
                 labels=labels, colors=colors, scales=scales, alphas=alphas,
                 x_label='RPM', y_label='G-force X')
    plot_optimal_rpm_region(ax=ax, plot_data=plot_data)


def plot_p_over_rpm(ax, plot_data: pd.PlotData):

    range_gears = np.unique(plot_data.gear)
    range_gears = np.sort(range_gears)
    range_gears = range_gears[range_gears > 0.0]

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    scale = 50.0
    alphas = [0.5] * len(labels)
    colors = [static_colors[i] for i, g in enumerate(range_gears)]
    full_acceleration_mask = data_processing.get_full_acceleration_mask(plot_data=plot_data)

    rpm = plot_data.rpm
    energy, kinetic_energy, potential_energy = data_processing.get_energy(plot_data=plot_data)
    times_steps = plot_data.run_time
    power = data_processing.derive_no_nan(x=kinetic_energy, time_steps=times_steps) / 1000.0

    x_points = []
    y_points = []
    scales = []
    for gear in range_gears:
        current_gear = plot_data.gear == gear
        interesting = np.logical_and(current_gear, full_acceleration_mask)

        x_points += [rpm[interesting]]
        y_points += [power[interesting]]
        scales += [np.ones_like(rpm[interesting]) * scale]

    scatter_plot(ax, x_points=x_points, y_points=y_points, title='Power over RPM (full throttle)',
                 labels=labels, colors=colors, scales=scales, alphas=alphas,
                 x_label='RPM', y_label='Power (kW)', plot_mean=True, plot_polynomial=True)
    plot_optimal_rpm_region(ax=ax, plot_data=plot_data)


def plot_p_over_vel(ax, plot_data: pd.PlotData):

    range_gears = np.unique(plot_data.gear)
    range_gears = np.sort(range_gears)
    range_gears = range_gears[range_gears > 0.0]

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    scale = 50.0
    alphas = [0.5] * len(labels)
    colors = [static_colors[i] for i, g in enumerate(range_gears)]
    full_acceleration_mask = data_processing.get_full_acceleration_mask(plot_data=plot_data)

    energy, kinetic_energy, potential_energy = data_processing.get_energy(plot_data=plot_data)
    times_steps = plot_data.run_time
    power = data_processing.derive_no_nan(x=kinetic_energy, time_steps=times_steps) / 1000.0

    x_points = []
    y_points = []
    scales = []
    for gear in range_gears:
        current_gear = plot_data.gear == gear
        interesting = np.logical_and(current_gear, full_acceleration_mask)

        speed_ms = plot_data.speed_ms
        x_points += [speed_ms[interesting]]
        y_points += [power[interesting]]
        scales += [np.ones_like(speed_ms[interesting]) * scale]

    scatter_plot(ax, x_points=x_points, y_points=y_points, title='Power over velocity (full throttle)',
                 labels=labels, colors=colors, scales=scales, alphas=alphas,
                 x_label='Velocity (m/s)', y_label='Power (kW)', plot_mean=True, plot_polynomial=False)


def plot_g_over_throttle(ax, plot_data: pd.PlotData):

    range_gears = np.unique(plot_data.gear)
    range_gears = np.sort(range_gears)
    range_gears = range_gears[range_gears > 0.0]

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    colors = [static_colors[i] for i, g in enumerate(range_gears)]
    scales = [25] * len(labels)
    alphas = [0.5] * len(labels)

    x_points = []
    y_points = []
    for g in range_gears:
        current_gear = plot_data.gear == g

        throttle = plot_data.throttle[current_gear]
        g_force_lon = plot_data.g_force_lon[current_gear]

        x_points += [throttle]
        y_points += [g_force_lon]

    scatter_plot(ax, x_points=x_points, y_points=y_points, title='G-force X over throttle',
                 labels=labels, colors=colors, scales=scales, alphas=alphas, x_label='Throttle', y_label='G-force X')


def plot_v_over_rpm(ax, plot_data: pd.PlotData):

    range_gears = np.unique(plot_data.gear)
    range_gears = np.sort(range_gears)
    range_gears = range_gears[range_gears > 0.0]
    not_close_to_gear_changes = np.logical_not(
        data_processing.get_gear_shift_mask(plot_data=plot_data, shift_time_ms=100.0))

    labels = ['Gear {}'.format(str(g)) for g in range_gears]
    colors = [static_colors[i] for i, g in enumerate(range_gears)]
    scales = [25] * len(labels)
    alphas = [0.5] * len(labels)

    x_points = []
    y_points = []
    for i, g in enumerate(range_gears):
        current_gear = plot_data.gear == g
        full_in_current_gear = np.logical_and(not_close_to_gear_changes, current_gear)
        full_throttle = plot_data.throttle == 1.0
        interesting = np.logical_and(full_in_current_gear, full_throttle)

        rpm = plot_data.rpm[interesting]
        speed_ms = plot_data.speed_ms[interesting]

        x_points += [rpm]
        y_points += [speed_ms]

    scatter_plot(ax, x_points=x_points, y_points=y_points, title='Speed over RPM (full throttle)',
                 labels=labels, colors=colors, scales=scales, alphas=alphas,
                 x_label='RPM', y_label='Speed (m/s)', plot_mean=True, plot_polynomial=True)
    plot_optimal_rpm_region(ax=ax, plot_data=plot_data)


def forward_over_2d_pos(ax, plot_data: pd.PlotData):

    # if we take all data points, the plot is too crowded
    sample_rate = 10

    x = plot_data.pos_x[::sample_rate]
    y = plot_data.pos_y[::sample_rate]
    x_min, x_middle, x_max = data_processing.get_min_middle_max(x)
    y_min, y_middle, y_max = data_processing.get_min_middle_max(y)

    diff = [x_max - x_min, y_max - y_min]
    diff_max = max(diff)

    pxy_normalized = data_processing.get_forward_dir_2d(plot_data)
    vxy_normalized = data_processing.get_forward_vel_2d(plot_data)
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


def wheel_speed_over_time(ax, plot_data: pd.PlotData):

    race_time = plot_data.run_time
    wsp_data = np.array([plot_data.wsp_fl, plot_data.wsp_fr, plot_data.wsp_rl, plot_data.wsp_rr])

    labels = ['Front left', 'Front right', 'Rear left', 'Rear right']
    x_points = np.array([race_time] * len(wsp_data))
    y_points = np.array(wsp_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Wheel speed over time',
              labels=labels, alpha=0.5, x_label='Time (s)', y_label='Wheel speed (m/s)', min_max_annotations=True)


def wheel_speed_lr_fr_over_time(ax, plot_data: pd.PlotData):

    race_time = plot_data.run_time
    wsp_left_right = (plot_data.wsp_fl + plot_data.wsp_rl) * 0.5 - (plot_data.wsp_fr + plot_data.wsp_rr) * 0.5
    wsp_front_rear = (plot_data.wsp_fl + plot_data.wsp_fr) * 0.5 - (plot_data.wsp_rl + plot_data.wsp_rr) * 0.5
    wsp_data = np.array([wsp_left_right, wsp_front_rear])

    labels = ['left-right', 'front-rear']
    x_points = np.array([race_time] * len(wsp_data))
    y_points = np.array(wsp_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Wheel speed difference over time', labels=labels,
              alpha=0.5, x_label='Time (s)', y_label='Wheel speed difference (m/s)', min_max_annotations=True)


def suspension_vel_over_time(ax, plot_data: pd.PlotData):

    race_time = plot_data.run_time
    susp_vel_fl = plot_data.susp_vel_fl
    susp_vel_fr = plot_data.susp_vel_fr
    susp_vel_rl = plot_data.susp_vel_rl
    susp_vel_rr = plot_data.susp_vel_rr

    susp_data = np.array([susp_vel_fl, susp_vel_fr, susp_vel_rl, susp_vel_rr])
    susp_data_stdev = [np.sqrt(np.var(d)) for d in susp_data]

    labels = ['Front left', 'Front right', 'Rear left', 'Rear right']
    labels = [l + ', stdev: {:.1f}'.format(susp_data_stdev[li]) for li, l in enumerate(labels)]
    x_points = np.array([race_time] * len(susp_data))
    y_points = np.array(susp_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Suspension velocity over time',
              labels=labels, alpha=0.5, x_label='Time (s)',
              y_label='Suspension velocity (mm/s)', min_max_annotations=True)


def slip_over_time(ax, plot_data: pd.PlotData):

    race_time = plot_data.run_time
    speed_ms = plot_data.speed_ms
    wsp_fl = plot_data.wsp_fl
    wsp_fr = plot_data.wsp_fr
    wsp_rl = plot_data.wsp_rl
    wsp_rr = plot_data.wsp_rr
    wsp = [wsp_fl, wsp_fr, wsp_rl, wsp_rr]
    slip = [w - speed_ms for w in wsp]
    wsp_data = np.array(slip)
    wsp_data_var = [np.var(d) for d in wsp_data]

    labels = ['Front left', 'Front right', 'Rear left', 'Rear right']
    labels = [l + ', stdev: {:.1f}'.format(wsp_data_var[li]) for li, l in enumerate(labels)]
    x_points = np.array([race_time] * len(wsp_data))
    y_points = np.array(wsp_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Wheel slip over time',
              labels=labels, alpha=0.5, x_label='Time (s)', y_label='Wheel slip (m/s)', min_max_annotations=True)


def ground_contact_over_time(ax, plot_data: pd.PlotData):

    susp_vel = [plot_data.susp_vel_fl, plot_data.susp_vel_fr, plot_data.susp_vel_rl, plot_data.susp_vel_rr]
    in_air_masks = [data_processing.get_in_air_mask(
        susp_vel_arr=susp, time_steps=plot_data.run_time,
        susp_vel_lim=100.0, susp_vel_var_max=100.0, filter_length=6)
        for susp in susp_vel]

    # boolean mask to 0.0 or 1.0, also take sum
    in_air_masks = [gc.astype(np.float) for gc in in_air_masks]
    in_air_masks_sum = np.sum(np.array(in_air_masks), axis=0)  # also show sum of wheels in air
    in_air_masks_sum[in_air_masks_sum < 4.0] = 0.0
    in_air_masks_sum[in_air_masks_sum == 4.0] = 1.0
    in_air_masks = in_air_masks + [in_air_masks_sum]
    in_air = [gc + gci * 0.05 for gci, gc in enumerate(in_air_masks)]  # small offset to avoid overlaps
    in_air_data = np.array(in_air)

    # aggregate time of wheels in air
    time_differences = data_processing.differences(plot_data.run_time, True)
    in_air_times = [np.sum(time_differences[ia > 0.0]) for ia in in_air_masks]

    labels = ['Front left', 'Front right', 'Rear left', 'Rear right', 'All wheels']
    labels = [l + ': {:.1f} s'.format(in_air_times[li]) for li, l in enumerate(labels)]
    x_points = np.array([plot_data.run_time] * len(in_air_data))
    y_points = np.array(in_air_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Wheels in air over lap time',
              labels=labels, alpha=0.5, x_label='Lap time (s)',
              y_label='Wheels in air', min_max_annotations=False)


def drift_over_speed(ax, plot_data: pd.PlotData):

    steering = np.abs(plot_data.steering)
    speed_ms = plot_data.speed_ms
    drift_angle_deg = data_processing.get_drift_angle_deg(plot_data)
    race_time = plot_data.run_time
    drift_angle_deg_der = data_processing.derive_no_nan(
        drift_angle_deg, time_steps=race_time)

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


def drift_angle_bars(ax, plot_data: pd.PlotData):

    race_time = plot_data.run_time
    time_differences = data_processing.differences(race_time, True)
    speed_ms = plot_data.speed_ms
    drift_angle_deg = data_processing.get_drift_angle_deg(plot_data)

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


def drift_angle_change_bars(ax, plot_data: pd.PlotData):

    race_time = plot_data.run_time
    time_differences = data_processing.differences(race_time, True)
    speed_ms = plot_data.speed_ms
    drift_angle_deg = data_processing.get_drift_angle_deg(plot_data)
    drift_angle_deg_der = data_processing.derive_no_nan(
        drift_angle_deg, time_steps=race_time)

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


def rotation_over_time(ax, plot_data: pd.PlotData):

    race_time = plot_data.run_time

    forward_local_xyz = data_processing.get_forward_dir_3d(plot_data)
    sideward_local_xyz = data_processing.get_sideward_dir_3d(plot_data)

    def get_vertical_angle_dislocation(dirs):
        global_dirs = data_processing.normalize_3d_vectors(
            dirs[0], dirs[1], np.zeros_like(dirs[2]))
        dirs_dislocation = (dirs * global_dirs).sum(axis=0)
        dirs_angle = np.arccos(dirs_dislocation)
        dirs_angle[dirs[2] < 0.0] = -dirs_angle[dirs[2] < 0.0]
        dirs_angle_deg = np.rad2deg(dirs_angle)
        return dirs_angle_deg

    directions = [sideward_local_xyz, forward_local_xyz]
    angle_deg = [get_vertical_angle_dislocation(d) for d in directions]
    angle_deg_stdev = [np.sqrt(np.var(a)) for a in angle_deg]

    labels = ['Sidewards, stdev: {:.1f}'.format(angle_deg_stdev[0]),
              'Forward, stdev: {:.1f}'.format(angle_deg_stdev[1])]
    x_points = np.array([race_time] * len(labels))
    y_points = np.array(angle_deg)

    line_plot(ax, x_points=x_points, y_points=y_points,
              title='Rotation Angles over Time',
              labels=labels, alpha=0.5, x_label='Time (s)',
              y_label='Car rotation angle (deg)', min_max_annotations=True)


def suspension_lr_fr_angles_over_time(ax, plot_data: pd.PlotData):

    race_time = plot_data.run_time
    susp_fl = plot_data.susp_fl
    susp_fr = plot_data.susp_fr
    susp_rl = plot_data.susp_rl
    susp_rr = plot_data.susp_rr
    susp_left_right = (susp_fl + susp_rl) * 0.5 - (susp_fr + susp_rr) * 0.5
    susp_front_rear = (susp_fl + susp_fr) * 0.5 - (susp_rl + susp_rr) * 0.5

    def height_diff_to_angle(displacement, dist):
        angle = np.arcsin(displacement / dist)
        return np.rad2deg(angle)

    # approximately wheelbase and track for Audi Quattro S1 -> should be accurate enough for other cars
    angle_left_right = height_diff_to_angle(susp_left_right / 1000.0, 1.800)
    angle_front_rear = height_diff_to_angle(susp_front_rear / 1000.0, 2.200)

    angle_data = np.array([-angle_left_right, -angle_front_rear])

    sidewards_angle_deg_stdev = np.sqrt(np.var(angle_left_right))
    forward_angle_deg_stdev = np.sqrt(np.var(angle_front_rear))

    labels = ['Sidewards, stdev: {:.3f}'.format(sidewards_angle_deg_stdev),
              'Forward, stdev: {:.3f}'.format(forward_angle_deg_stdev)]
    x_points = np.array([race_time] * len(angle_data))
    y_points = np.array(angle_data)

    line_plot(ax, x_points=x_points, y_points=y_points, title='Suspension compression angle over time',
              labels=labels, alpha=0.5, x_label='Time (s)',
              y_label='Suspension compression angle (deg)', min_max_annotations=True)
