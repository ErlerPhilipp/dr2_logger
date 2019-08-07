import numpy as np

import networking
import utils


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
        session_data[networking.fields['pos_x']],
        session_data[networking.fields['pos_y']],
        session_data[networking.fields['pos_z']])


def get_2d_coordinates(session_data):

    return convert_coordinate_system_2d(
        session_data[networking.fields['pos_x']],
        session_data[networking.fields['pos_z']])


def get_min_middle_max(x):

    x_min = x.min()
    x_max = x.max()
    x_middle = (x_max + x_min) * 0.5

    return x_min, x_middle, x_max



