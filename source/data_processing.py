import sys
import functools
import typing

import numpy as np
import sklearn.pipeline

from source import plot_data as pd


def normalize_2d_vectors(x, y):
    xy = np.array([x, y])
    xy_len = np.linalg.norm(xy, axis=0, keepdims=True)
    zero_vectors = xy_len == 0.0
    xy_len[zero_vectors] = sys.float_info.epsilon
    xy_normalized = xy / xy_len
    return xy_normalized


def normalize_3d_vectors(x, y, z):
    xyz = np.array([x, y, z])
    xyz_len = np.linalg.norm(xyz, axis=0, keepdims=True)
    xyz_normalized = xyz / xyz_len
    return xyz_normalized


def convert_coordinate_system_3d(x, y, z):
    """
    Switch right-hand to left-hand coordinate system and vice versa.
    :param x: float scalar or numpy array
    :param y: float scalar or numpy array
    :param z: float scalar or numpy array
    :return:
    """

    return x, -z, y


def convert_coordinate_system_2d(x, z):
    """
    Switch 2D (top-down) right-hand to left-hand coordinate system and vice versa.
    :param x: float scalar or numpy array
    :param z: float scalar or numpy array
    :return:
    """

    return x, -z


def get_min_middle_max(x):
    x_min = x.min()
    x_max = x.max()
    x_middle = (x_max + x_min) * 0.5
    return x_min, x_middle, x_max


def no_outlier_mask(arr: np.ndarray, outlier_limit: float):
    if arr.size == 0:
        return np.array([])

    arr_min = arr.min()
    arr_max = arr.max()
    dist = arr_max - arr_min
    new_arr_min = arr_min + dist * outlier_limit
    new_arr_max = arr_min + dist * (1.0 - outlier_limit)
    large_enough = arr >= new_arr_min
    small_enough = arr <= new_arr_max
    mask = functools.reduce(np.logical_and, (
        large_enough, small_enough,
    ))
    return mask


def differences(x, fix_negative_dt=False):
    x_prev = np.concatenate((np.array([x[0]]), x[:-1]))
    x_diff = x - x_prev

    # prevent negative times due to next lap
    if fix_negative_dt:
        x_diff[x_diff < 0.0] = np.finfo(x_diff.dtype).eps
    return x_diff


def derive_nan(x, time_steps):
    time_diff = differences(time_steps)
    x_diff = differences(x)
    x_derived = x_diff / time_diff
    return x_derived


def derive_no_nan(x, time_steps):
    """
    Prevent nan
    :param x:
    :param time_steps:
    :return:
    """
    time_diff = differences(time_steps)
    time_diff[time_diff < 0.0] = np.finfo(time_diff.dtype).eps  # lap time is reset to 0.0 on a new lap, of course
    time_diff[time_diff == 0.0] = np.finfo(time_diff.dtype).eps  # same lap time should be filtered out but who knows
    x_diff = differences(x)
    x_derived = x_diff / time_diff
    return x_derived


def get_forward_dir_2d(plot_data: pd.PlotData):
    pxy_normalized = normalize_2d_vectors(plot_data.roll_x, plot_data.roll_y)
    return pxy_normalized


def get_forward_dir_3d(plot_data: pd.PlotData):
    pxyz_normalized = normalize_3d_vectors(plot_data.roll_x, plot_data.roll_y, plot_data.roll_z)
    return pxyz_normalized


def get_sideward_dir_3d(plot_data: pd.PlotData):
    pxy_normalized = normalize_3d_vectors(plot_data.pitch_x, plot_data.pitch_y, plot_data.pitch_z)
    return pxy_normalized


def get_forward_vel_2d(plot_data: pd.PlotData):
    vxy_normalized = normalize_2d_vectors(plot_data.vel_x, plot_data.vel_y)
    return vxy_normalized


def get_drift_angle(plot_data: pd.PlotData):

    pxy_normalized = get_forward_dir_2d(plot_data)
    vxy_normalized = get_forward_vel_2d(plot_data)

    # dot(dir, speed) = drift
    drift = (pxy_normalized * vxy_normalized).sum(axis=0)
    drift_angle = np.arccos(drift)
    drift_angle_deg = np.rad2deg(drift_angle)

    return drift_angle_deg


def get_energy(plot_data: pd.PlotData):

    mass = 1000.0  # kg, doesn't really matter because we want only the relative changes in energy
    gravity = 9.81  # m/s^2
    velocity = plot_data.speed_ms
    height = plot_data.pos_y
    height_relative = height - np.min(height)

    kinetic_energy = 0.5 * mass * np.square(velocity)
    potential_energy = mass * gravity * height_relative
    # TODO: add rotational energy
    # TODO: add rotational energy of wheels
    # TODO: add potential energy of springs
    # TODO: add heat energy in brakes? lol

    energy = kinetic_energy + potential_energy

    return energy, kinetic_energy, potential_energy


def grow_mask(arr: np.ndarray, grow_time_ms: float):
    # exclude times ~0.1 sec around gear shifts and gears < 1
    # assuming 1 UDP sample is 10 ms (delay=1 in Dirt Rally)
    box_filter_length = int(round(grow_time_ms / 2.0 / 10.0))
    box_filter = np.array([1.0] * box_filter_length)
    close_to_true = np.convolve(arr, box_filter, mode='same')
    return close_to_true > 0.0


def shrink_mask(arr: np.ndarray, shrink_time_ms: float):
    arr[arr >= 1.0] = 1.0
    arr[arr < 1.0] = 0.0
    # exclude times ~0.1 sec around gear shifts and gears < 1
    # assuming 1 UDP sample is 10 ms (delay=1 in Dirt Rally)
    box_filter_length = int(round(shrink_time_ms / 2.0 / 10.0))
    box_filter = np.array([1.0] * box_filter_length)
    close_to_true = np.convolve(arr, box_filter, mode='same')
    return close_to_true >= float(box_filter_length - sys.float_info.epsilon * 100.0)


def get_gear_shift_mask(plot_data: pd.PlotData, shift_time_ms=100.0):
    time_steps = plot_data.run_time
    gear_changes = derive_no_nan(plot_data.gear, time_steps=time_steps)
    gear_changes[gear_changes != 0.0] = 1.0  # 1.0 if the gear changed, 0.0 otherwise
    close_to_gear_changes = grow_mask(arr=gear_changes, grow_time_ms=shift_time_ms)
    return close_to_gear_changes


def add_boundary_samples_enforce_parabola(x: np.ndarray, y: np.ndarray):
    num_extra_samples = int(x.shape[0] / 2)

    y_arg_max = np.argmax(y)
    x_max = x[y_arg_max]
    y_max = np.percentile(a=y, q=95)  # max without possible outliers
    x_high = 1.3 * np.max(x)
    y_high = 2.0 * y_max

    x_low_extra_samples = np.linspace(start=0.0, stop=x_max * 0.1, num=num_extra_samples)
    x_high_extra_samples = np.linspace(start=x_high * 0.9, stop=x_high, num=num_extra_samples)

    y_low_extra_samples = np.linspace(start=0.0, stop=y_high * 0.1, num=num_extra_samples)
    y_high_extra_samples = np.linspace(start=y_high * 0.1, stop=0.0, num=num_extra_samples)

    x_extended = np.concatenate((x, x_low_extra_samples, x_high_extra_samples), axis=0)
    y_extended = np.concatenate((y, y_low_extra_samples, y_high_extra_samples), axis=0)

    return x_extended, y_extended


def get_acc_rpm_regressor(plot_data: pd.PlotData):
    from sklearn.linear_model import RANSACRegressor
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.pipeline import make_pipeline

    # the first gear is rather unreliable because the wheels usually spin freely at the start
    # median makes it more robust
    full_acceleration_mask = get_full_acceleration_mask(plot_data=plot_data)
    if not np.any(full_acceleration_mask):
        return None, None, None

    polynome_degree = 3

    acc_rpm_regressor = {}
    data_gear = plot_data.gear
    range_gears = list(set(data_gear))
    range_gears.sort()
    for g in range_gears:
        current_gear = plot_data.gear == g
        not_close_to_gear_changes = np.logical_not(get_gear_shift_mask(plot_data=plot_data, shift_time_ms=100.0))
        interesting = functools.reduce(np.logical_and, (
            not_close_to_gear_changes, current_gear, full_acceleration_mask
        ))
        if g <= 0 or np.count_nonzero(interesting) == 0:
            acc_rpm_regressor[int(g)] = None
        else:
            # add some zero samples at RPM 0 and high RPM to enforce a parabola with opening to the bottom
            rpm_gear_interesting = plot_data.rpm[interesting]
            acc_gear_interesting = plot_data.g_force_lon[interesting]

            no_outliers = no_outlier_mask(arr=rpm_gear_interesting, outlier_limit=0.05)
            acc_gear = acc_gear_interesting[no_outliers]  # optimal RPM prediction is noisy with acceleration
            rpm_gear = rpm_gear_interesting[no_outliers]

            if rpm_gear.size <= polynome_degree + 1:
                acc_rpm_regressor[int(g)] = None
            else:
                rpm_gear, acc_gear = add_boundary_samples_enforce_parabola(
                    x=rpm_gear, y=acc_gear)
                try:
                    model = make_pipeline(PolynomialFeatures(degree=polynome_degree), RANSACRegressor(random_state=42))
                    model.fit(X=rpm_gear[:, np.newaxis], y=acc_gear)
                    acc_rpm_regressor[int(g)] = model
                except np.linalg.LinAlgError as _:
                    # sometimes LinAlgError("SVD did not converge in Linear Least Squares"), maybe first gear
                    acc_rpm_regressor[int(g)] = None

    return acc_rpm_regressor


def get_optimal_rpm(acc_rpm_regressor: typing.Dict[int, sklearn.pipeline.Pipeline], evaluation_range: np.ndarray):
    gears_sorted = np.sort(tuple(acc_rpm_regressor.keys()))
    acc_eval_per_gear = {}
    for gear in gears_sorted:
        if acc_rpm_regressor[gear] is None:
            acc_eval_per_gear[gear] = None
        else:
            model = acc_rpm_regressor[gear]
            acc_eval = model.predict(evaluation_range[:, np.newaxis])
            acc_eval_per_gear[gear] = acc_eval

    rpm_shift_up_point_per_gear = {}
    for gear in gears_sorted:
        if acc_eval_per_gear[gear] is None:
            rpm_shift_up_point_per_gear[gear] = np.nan
        else:
            acc_this_gear = acc_eval_per_gear[gear]
            next_gear = gear + 1
            if next_gear > np.max(gears_sorted):
                rpm_next_gear_is_better = np.inf
            else:
                acc_next_gear = acc_eval_per_gear[next_gear]
                if acc_next_gear is None:
                    acc_next_gear = 0.0
                acc_this_gear_better = acc_this_gear > np.max(acc_next_gear)
                # argmax from back to get last index
                optimal_rpm_max_id = acc_this_gear_better.shape - np.argmax(acc_this_gear_better[::-1]) - 1
                rpm_next_gear_is_better = evaluation_range[np.asscalar(optimal_rpm_max_id)]

            rpm_shift_up_point_per_gear[gear] = rpm_next_gear_is_better

    rpm_optimum_per_gear = {}
    for gear in gears_sorted:
        if acc_eval_per_gear[gear] is None:
            rpm_optimum_per_gear[gear] = np.nan
        else:
            acc_this_gear = acc_eval_per_gear[gear]
            rpm_optimum_id = np.argmax(acc_this_gear)
            rpm_optimum = evaluation_range[rpm_optimum_id]
            rpm_optimum_per_gear[gear] = rpm_optimum

    return rpm_shift_up_point_per_gear, rpm_optimum_per_gear


def get_full_acceleration_mask(plot_data: pd.PlotData):

    # full throttle inputs
    # ignore possible ramp-up of turbo
    # ignore sudden release of handbreak (clutch also released)
    full_throttle = shrink_mask(arr=plot_data.throttle >= 0.9, shrink_time_ms=500.0)
    no_brakes = plot_data.brakes <= 0.1
    no_steering = np.abs(plot_data.steering) <= 0.1
    no_clutch = shrink_mask(arr=plot_data.clutch <= 0.1, shrink_time_ms=500.0)

    # take only times without a lot of drifting
    no_drift = np.abs(get_drift_angle(plot_data=plot_data)) <= 5.0  # degree

    # take only times without a lot of slip
    # threshold is unclear, maybe different for every car / tyre
    # 3 would probably be sufficient for soft tyres on gravel
    slip_threshold = 10.0
    car_vel = plot_data.speed_ms
    no_slip_fl = np.abs(plot_data.wsp_fl - car_vel) <= slip_threshold
    no_slip_fr = np.abs(plot_data.wsp_fr - car_vel) <= slip_threshold
    no_slip_rl = np.abs(plot_data.wsp_rl - car_vel) <= slip_threshold
    no_slip_rr = np.abs(plot_data.wsp_rr - car_vel) <= slip_threshold
    no_slip_f = np.abs(plot_data.wsp_fl - plot_data.wsp_fr) <= slip_threshold
    no_slip_r = np.abs(plot_data.wsp_rl - plot_data.wsp_rr) <= slip_threshold

    not_close_to_gear_changes = np.logical_not(get_gear_shift_mask(plot_data=plot_data, shift_time_ms=100.0))
    forward_gear = plot_data.gear >= 1.0

    full_acceleration_mask = functools.reduce(np.logical_and, (
        full_throttle, no_brakes, no_steering, no_clutch,
        forward_gear, not_close_to_gear_changes,
        no_drift,
        no_slip_fl, no_slip_fr, no_slip_rl, no_slip_rr,
        no_slip_f, no_slip_r,
    ))

    return full_acceleration_mask
