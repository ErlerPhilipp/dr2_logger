import os
import numpy as np

def cls():
    print('\n' * 1000)  # for pycharm
    os.system('cls' if os.name == 'nt' else 'clear')


def make_dir_for_file(file):
    file_dir = os.path.dirname(file)
    if file_dir != '':
        if not os.path.exists(file_dir):
            try:
                os.makedirs(os.path.dirname(file))
            except OSError as exc: # Guard against race condition
                raise


def normalize_2d_vectors(x, y):
    xy = np.array([x, y])
    xy_len = np.linalg.norm(xy, axis=0, keepdims=True)
    xy_normalized = xy / xy_len
    return xy_normalized