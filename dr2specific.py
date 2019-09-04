import numpy as np
from enum import Enum

import networking


class GameState(Enum):
    error = -1
    startup = 0
    menu = 1
    service_area = 2
    race_start = 3
    race_running = 4
    race_paused = 5
    race_finished = 6


def get_game_state_str(state, receive_results, num_samples):
    state_str = 'Samples {:05d}, lap time: {:.1f}, speed: {:.1f} m/s, rpm {:5.1f}, {}'

    if state == GameState.startup:
        return state_str.format(
                num_samples,
                0.0,
                0.0,
                0.0,
                'game started')
    elif state == GameState.menu:
        return state_str.format(
                num_samples,
                receive_results[networking.fields.lap_time.value],
                receive_results[networking.fields.speed_ms.value],
                receive_results[networking.fields.rpm.value],
                'race running')
    elif state == GameState.service_area:
        return state_str.format(
                num_samples,
                receive_results[networking.fields.lap_time.value],
                receive_results[networking.fields.speed_ms.value],
                receive_results[networking.fields.rpm.value],
                'service area')
    elif state == GameState.race_start:
        return state_str.format(
                num_samples,
                receive_results[networking.fields.lap_time.value],
                receive_results[networking.fields.speed_ms.value],
                receive_results[networking.fields.rpm.value],
                'race starting')
    elif state == GameState.race_running:
        return state_str.format(
                num_samples,
                receive_results[networking.fields.lap_time.value],
                receive_results[networking.fields.speed_ms.value],
                receive_results[networking.fields.rpm.value],
                'race running')
    elif state == GameState.race_paused:
        return state_str.format(
                num_samples,
                receive_results[networking.fields.lap_time.value],
                receive_results[networking.fields.speed_ms.value],
                receive_results[networking.fields.rpm.value],
                'race paused')
    elif state == GameState.race_finished:
        return state_str.format(
                num_samples,
                receive_results[networking.fields.lap_time.value],
                receive_results[networking.fields.speed_ms.value],
                receive_results[networking.fields.rpm.value],
                'race finished')
    elif state == GameState.error:
        return None
    else:
        raise ValueError('Invalid game state: {}'.format(state))


def get_game_state(receive_results, last_receive_results):

    if receive_results is None:  # no data, error in receive?
        return GameState.error

    if last_receive_results is None:  # first package received
        return GameState.startup

    # car is at origin -> probably in finish
    if receive_results[networking.fields.pos_x.value] == 0.0 and \
        receive_results[networking.fields.pos_y.value] == 0.0 and \
        receive_results[networking.fields.pos_z.value] == 0.0:
        return GameState.race_finished

    # race has not yet started
    if receive_results[networking.fields.lap_time.value] == 0.0:
        return GameState.race_start

    # new race time is less than the previous -> race has ended and car is in service area or next race
    if receive_results[networking.fields.lap_time.value] < last_receive_results[networking.fields.lap_time.value]:
        return GameState.service_area

    # same time again -> game is probably paused
    if receive_results[networking.fields.lap_time.value] == last_receive_results[networking.fields.lap_time.value] and \
        receive_results[networking.fields.progress.value] == last_receive_results[networking.fields.progress.value]:
        return GameState.race_paused

    return GameState.race_running


def accept_new_data(state):
    if state == GameState.error:
        return False
    elif state == GameState.startup:
        return True
    elif state == GameState.menu:
        return False
    elif state == GameState.service_area:
        return False
    elif state == GameState.race_start:
        return False
    elif state == GameState.race_running:
        return True
    elif state == GameState.race_paused:
        return False
    elif state == GameState.race_finished:
        return False
    else:
        return False
