import os


def cls():
    print('\n' * 1000)  # for pycharm
    os.system('cls' if os.name == 'nt' else 'clear')


def make_dir_for_file(file):
    file_dir = os.path.dirname(file)
    if file_dir != '':
        if not os.path.exists(file_dir):
            try:
                os.makedirs(os.path.dirname(file))
            except OSError as _:  # Guard against race condition
                raise
