import numpy as np
from enum import Enum

import networking


class GameState(Enum):
    error = 0
    race_start = 1
    race_running = 2
    duplicate_package = 3
    race_finished_or_service_area = 4


def get_game_state_str(state, receive_results, num_samples):
    state_str = 'Samples {:05d}, lap time: {:.1f}, speed: {:.1f} m/s, rpm {:5.1f}, {}'

    if state == GameState.race_start:
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
    elif state == GameState.duplicate_package:
        return state_str.format(
                num_samples,
                receive_results[networking.fields.lap_time.value],
                receive_results[networking.fields.speed_ms.value],
                receive_results[networking.fields.rpm.value],
                'duplicate package')
    elif state == GameState.race_finished_or_service_area:
        return state_str.format(
                num_samples,
                receive_results[networking.fields.lap_time.value],
                receive_results[networking.fields.speed_ms.value],
                receive_results[networking.fields.rpm.value],
                'race finished or in service area')
    elif state == GameState.error:
        return None
    else:
        raise ValueError('Invalid game state: {}'.format(state))


def get_game_state(receive_results, last_receive_results):

    if receive_results is None:  # no data, error in receive?
        return GameState.error

    # all values zero -> probably in finish
    if np.all(receive_results == np.zeros_like(receive_results)):
        return GameState.race_finished_or_service_area

    # race has not yet started
    if receive_results[networking.fields.lap_time.value] == 0.0 and \
        receive_results[networking.fields.distance.value] == 0.0 and \
        receive_results[networking.fields.progress.value] == 0.0:
        return GameState.race_start

    # all equal except the run time -> new package, same game state in DR2 -> race paused
    if last_receive_results is not None and \
        receive_results[networking.fields.run_time.value] != \
        last_receive_results[networking.fields.run_time.value] and \
        np.all(receive_results[1:] == last_receive_results[1:]):
        return GameState.duplicate_package

    return GameState.race_running


def accept_new_data(state):
    if state == GameState.error:
        return False
    elif state == GameState.race_start:
        return False
    elif state == GameState.race_running:
        return True
    elif state == GameState.race_finished_or_service_area:
        return False
    elif state == GameState.duplicate_package:
        return False
    else:
        raise ValueError('Unknown state: {}'.format(state))
