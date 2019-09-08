import numpy as np

import networking


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


def get_3d_coordinates(session_data):

    return convert_coordinate_system_3d(
        session_data[networking.fields.pos_x.value],
        session_data[networking.fields.pos_y.value],
        session_data[networking.fields.pos_z.value])


def get_2d_coordinates(session_data):

    return convert_coordinate_system_2d(
        session_data[networking.fields.pos_x.value],
        session_data[networking.fields.pos_z.value])


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


def get_forward_dir_2d(session_data):
    px, py = convert_coordinate_system_2d(
        session_data[networking.fields.pitch_x.value],
        session_data[networking.fields.pitch_z.value])
    pxy_normalized = normalize_2d_vectors(px, py)
    return pxy_normalized


def get_forward_dir_3d(session_data):
    px, py, pz = convert_coordinate_system_3d(
        session_data[networking.fields.pitch_x.value],
        session_data[networking.fields.pitch_y.value],
        session_data[networking.fields.pitch_z.value])
    pxyz_normalized = normalize_3d_vectors(px, py, pz)
    return pxyz_normalized


def get_sideward_dir_3d(session_data):
    px, py, pz = convert_coordinate_system_3d(
        session_data[networking.fields.roll_x.value],
        session_data[networking.fields.roll_y.value],
        session_data[networking.fields.roll_z.value])
    pxy_normalized = normalize_3d_vectors(px, py, pz)
    return pxy_normalized


def get_forward_vel_2d(session_data):
    vx, vy = convert_coordinate_system_2d(
        session_data[networking.fields.vel_x.value],
        session_data[networking.fields.vel_z.value])
    vxy_normalized = normalize_2d_vectors(vx, vy)
    return vxy_normalized


def get_sideward_vel_3d(session_data):
    vy, vx, vz = convert_coordinate_system_3d(
        session_data[networking.fields.roll_x.value],
        session_data[networking.fields.roll_y.value],
        session_data[networking.fields.roll_z.value])
    vxy_normalized = normalize_3d_vectors(vx, vy, vz)
    return vxy_normalized


def get_drift_angle(session_data):

    pxy_normalized = get_forward_dir_2d(session_data)
    vxy_normalized = get_forward_vel_2d(session_data)

    # dot(dir, speed) = drift
    drift = (pxy_normalized * vxy_normalized).sum(axis=0)
    drift_angle = np.arccos(drift)
    drift_angle_deg = np.rad2deg(drift_angle)

    return drift_angle_deg
