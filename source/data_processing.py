import sys
import functools

import numpy as np

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


def get_optimal_rpm(plot_data: pd.PlotData):
    # from sklearn.linear_model import HuberRegressor
    from sklearn.linear_model import RANSACRegressor
    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.pipeline import make_pipeline

    # # strange strong acc debug
    # interesting_samples = plot_data.g_force_lon > 1.2
    # interesting_samples = np.logical_and(get_full_acceleration_mask(plot_data=plot_data), interesting_samples)
    # interesting_samples = grow_mask(arr=interesting_samples, grow_time_ms=3000.0)
    # debug_test = np.stack((plot_data.lap_time, plot_data.g_force_lat, plot_data.g_force_lon, plot_data.throttle), axis=1)
    # debug_test = debug_test[interesting_samples]

    # the first gear is rather unreliable because the wheels usually spin freely at the start
    # median makes it more robust
    full_acceleration_mask = get_full_acceleration_mask(plot_data=plot_data)
    if not np.any(full_acceleration_mask):
        return None, None, None
    # energy, kinetic_energy, potential_energy = get_energy(plot_data=plot_data)

    polynome_degree = 2

    optimal_acc_per_gear = {}
    optimal_rpm_per_gear = {}
    data_gear = plot_data.gear
    range_gears = list(set(data_gear))
    range_gears.sort()
    range_gears = [g for g in range_gears if g > 0.0]
    for g in range_gears:
        current_gear = plot_data.gear == g
        not_close_to_gear_changes = np.logical_not(get_gear_shift_mask(plot_data=plot_data, shift_time_ms=100.0))
        interesting = functools.reduce(np.logical_and, (
            not_close_to_gear_changes, current_gear, full_acceleration_mask
        ))
        if np.count_nonzero(interesting) == 0:
            continue

        no_outliers = no_outlier_mask(arr=plot_data.rpm[interesting], outlier_limit=0.05)
        acc_gear = plot_data.g_force_lon[interesting][no_outliers]  # optimal RPM prediction is noisy with acceleration
        # vel_gear = plot_data.speed_ms[interesting][no_outliers]
        # acc_gear = energy[interesting][no_outliers]
        rpm_gear = plot_data.rpm[interesting][no_outliers]

        if rpm_gear.size > polynome_degree + 1:
            rpm_min = np.min(rpm_gear)
            rpm_max = np.max(rpm_gear)
            try:
                # model = make_pipeline(PolynomialFeatures(degree=polynome_degree), HuberRegressor())
                model = make_pipeline(PolynomialFeatures(degree=polynome_degree), RANSACRegressor(random_state=42))
                model.fit(X=np.expand_dims(rpm_gear, axis=2), y=acc_gear)
                rpm_poly = np.linspace(rpm_min, rpm_max, 500)
                acc_poly = model.predict(rpm_poly[:, np.newaxis])
                # poly_coefficients = np.polyfit(x=rpm_gear, y=acc_gear, deg=2)
                # poly = np.poly1d(poly_coefficients)
                # # poly_derived = np.polyder(poly)
                # # acc_poly = poly_derived(rpm_poly)
                # acc_poly = poly(rpm_poly)
                optimal_acc_per_gear[int(g)] = np.max(acc_poly)
                optimal_rpm_per_gear[int(g)] = rpm_poly[np.argmax(acc_poly)]
            except np.linalg.LinAlgError as _:
                pass  # sometimes LinAlgError("SVD did not converge in Linear Least Squares"), maybe first gear

    return optimal_rpm_per_gear, optimal_acc_per_gear


def get_full_acceleration_mask(plot_data: pd.PlotData):

    # full throttle inputs
    # ignore possible ramp-up of turbo
    # ignore sudden release of handbreak (clutch also released)
    full_throttle = shrink_mask(arr=plot_data.throttle >= 0.9, shrink_time_ms=500.0)
    no_brakes = plot_data.brakes <= 0.1
    no_steering = np.abs(plot_data.steering) <= 0.1
    no_clutch = shrink_mask(arr=plot_data.clutch <= 0.1, shrink_time_ms=3000.0)

    # take only times without a lot of drifting
    no_drift = np.abs(get_drift_angle(plot_data=plot_data)) <= 5.0  # degree

    # take only times without a lot of slip
    # threshold is unclear, maybe different for every car / tyre
    # 3 would probably be sufficient for soft tyres on gravel
    slip_threshold = 5.0
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
