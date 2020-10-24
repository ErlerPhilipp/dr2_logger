import numpy as np

from source import plot_data as pd


def normalize_2d_vectors(x, y):
    xy = np.array([x, y])
    xy_len = np.linalg.norm(xy, axis=0, keepdims=True)
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
    # TODO: add heat energy in brakes? lol

    energy = kinetic_energy + potential_energy

    return energy, kinetic_energy, potential_energy


def get_gear_shift_mask(plot_data: pd.PlotData, shift_time_ms=100.0):

    # exclude times ~0.1 sec around gear shifts and gears < 1
    # assuming 1 UDP sample is 10 ms (delay=1 in Dirt Rally)
    time_steps = plot_data.run_time
    gear_changes = derive_no_nan(plot_data.gear, time_steps=time_steps)
    gear_changes[gear_changes != 0.0] = 1.0  # 1.0 if the gear changed, 0.0 otherwise
    box_filter_length = int(round(shift_time_ms / 2.0 / 10.0))
    box_filter = np.array([1.0] * box_filter_length)
    close_to_gear_changes = np.convolve(gear_changes, box_filter, mode='same') > 0.0
    return close_to_gear_changes


def get_optimal_rpm(plot_data: pd.PlotData):

    # the first gear is rather unreliable because the wheels usually spin freely at the start
    # median makes it more robust
    full_acceleration_mask = get_full_acceleration_mask(plot_data=plot_data)
    if not np.any(full_acceleration_mask):
        return None, None, None
    # energy, kinetic_energy, potential_energy = get_energy(plot_data=plot_data)

    optimal_vel_per_gear = {}
    optimal_rpm_per_gear = {}
    data_gear = plot_data.gear
    range_gears = list(set(data_gear))
    range_gears.sort()
    range_gears = [g for g in range_gears if g > 0.0]
    for g in range_gears:
        current_gear = plot_data.gear == g
        not_close_to_gear_changes = np.logical_not(get_gear_shift_mask(plot_data=plot_data, shift_time_ms=100.0))
        full_in_current_gear = np.logical_and(not_close_to_gear_changes, current_gear)
        interesting = np.logical_and(full_in_current_gear, full_acceleration_mask)
        # acc_gear = plot_data.g_force_lon[interesting]  # optimal RPM prediction is noisy with acceleration
        vel_gear = plot_data.speed_ms[interesting]
        # acc_gear = kinetic_energy[interesting]
        rpm_gear = plot_data.rpm[interesting]

        rpm_min = np.min(rpm_gear)
        rpm_max = np.max(rpm_gear)
        try:
            poly_coefficients = np.polyfit(x=rpm_gear, y=vel_gear, deg=3)
            poly = np.poly1d(poly_coefficients)
            poly_derived = np.polyder(poly)
            rpm_poly = np.linspace(rpm_min, rpm_max, 500)
            vel_poly = poly_derived(rpm_poly)
            optimal_vel_per_gear[int(g)] = np.max(vel_poly)
            optimal_rpm_per_gear[int(g)] = rpm_poly[np.argmax(vel_poly)]
        except np.linalg.LinAlgError as _:
            pass  # sometimes LinAlgError("SVD did not converge in Linear Least Squares"), maybe first gear

    return optimal_rpm_per_gear, optimal_vel_per_gear


def get_full_acceleration_mask(plot_data: pd.PlotData):

    import functools

    # full throttle inputs
    full_throttle = plot_data.throttle >= 0.99
    no_brakes = plot_data.brakes <= 0.01
    no_clutch = plot_data.clutch <= 0.01

    # take only times without a lot of drifting
    no_drift = np.abs(get_drift_angle(plot_data=plot_data)) <= 5.0  # degree

    # take only times without a lot of slip
    car_vel = plot_data.speed_ms
    no_slip_fl = np.abs(plot_data.wsp_fl - car_vel) <= 15.0
    no_slip_fr = np.abs(plot_data.wsp_fr - car_vel) <= 15.0
    no_slip_rl = np.abs(plot_data.wsp_rl - car_vel) <= 15.0
    no_slip_rr = np.abs(plot_data.wsp_rr - car_vel) <= 15.0

    # # take only mostly flat parts of the track
    # small_susp_vel_fl = np.abs(plot_data.susp_vel_fl) <= 0.01
    # small_susp_vel_fr = np.abs(plot_data.susp_vel_fr) <= 0.01
    # small_susp_vel_rl = np.abs(plot_data.susp_vel_rl) <= 0.01
    # small_susp_vel_rr = np.abs(plot_data.susp_vel_rr) <= 0.01

    not_close_to_gear_changes = np.logical_not(get_gear_shift_mask(plot_data=plot_data, shift_time_ms=100.0))
    forward_gear = plot_data.gear >= 1.0

    full_acceleration_mask = functools.reduce(np.logical_and, (
        full_throttle, no_brakes, no_clutch,
        forward_gear, not_close_to_gear_changes,
        no_drift,
        no_slip_fl, no_slip_fr, no_slip_rl, no_slip_rr,
        # small_susp_vel_fl, small_susp_vel_fr, small_susp_vel_rl, small_susp_vel_rr,
    ))

    return full_acceleration_mask
