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


def differences(x):
    x_prev = np.concatenate((np.array([x[0]]), x[:-1]))
    x_diff = x - x_prev
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
    # TODO: add heat energy in brakes? lol

    energy = kinetic_energy + potential_energy

    return energy, kinetic_energy, potential_energy


def get_full_acceleration_mask(plot_data: pd.PlotData):

    import functools

    # full throttle inputs
    full_throttle = plot_data.throttle >= 0.99
    no_brakes = plot_data.brakes <= 0.01
    no_clutch = plot_data.clutch <= 0.01

    # take only times without a lot of drifting
    no_drift = np.abs(get_drift_angle(plot_data=plot_data)) <= 5.0  # degree

    # # take only times without a lot of slip
    # car_vel = plot_data.speed_ms
    # no_slip_fl = np.abs(plot_data.wsp_fl - car_vel) <= 5.0
    # no_slip_fr = np.abs(plot_data.wsp_fr - car_vel) <= 5.0
    # no_slip_rl = np.abs(plot_data.wsp_rl - car_vel) <= 5.0
    # no_slip_rr = np.abs(plot_data.wsp_rr - car_vel) <= 5.0

    # # take only mostly flat parts of the track
    # small_susp_vel_fl = np.abs(plot_data.susp_vel_fl) <= 0.01
    # small_susp_vel_fr = np.abs(plot_data.susp_vel_fr) <= 0.01
    # small_susp_vel_rl = np.abs(plot_data.susp_vel_rl) <= 0.01
    # small_susp_vel_rr = np.abs(plot_data.susp_vel_rr) <= 0.01

    # exclude times ~0.1 sec around gear shifts and gears < 1
    gear = plot_data.gear
    forward_gear = gear >= 1.0
    time_steps = plot_data.run_time
    gear_changes = derive_no_nan(gear, time_steps=time_steps)
    gear_changes[gear_changes != 0.0] = 1.0  # 1.0 if the gear changed, 0.0 otherwise
    box_filter = np.array([1.0] * 10)  # 10 -> 2 * 160ms at 60 FPS
    no_close_gear_changes = np.convolve(gear_changes, box_filter, mode='same') == 0.0

    full_acceleration_mask = functools.reduce(np.logical_and, (
        full_throttle, no_brakes, no_clutch,
        forward_gear, no_close_gear_changes,
        no_drift,
        # no_slip_fl, no_slip_fr, no_slip_rl, no_slip_rr,
        # small_susp_vel_fl, small_susp_vel_fr, small_susp_vel_rl, small_susp_vel_rr,
    ))

    return full_acceleration_mask
