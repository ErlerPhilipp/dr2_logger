import numpy as np
import os
import sys
from enum import Enum

from source import networking
from source import utils
from source import plots
from source import settings
# from source.dr1.game_dr1 import GameDr1
from source.dirt_rally.game_dirt_rally import GameDirtRally


class GameState(Enum):
    ignore_package = 0
    race_not_running = 1
    race_running = 2


class LoggerBackend:

    def __init__(self, debugging=False, log_raw_data=False):
        self.debugging = debugging
        self.log_raw_data = log_raw_data

        self.game_name = settings.settings['general']['game']
        self.game = None
        self.change_game(settings.settings['general']['game'])

        self.session_collection = np.zeros((self.game.get_num_fields(), 0))
        self.first_sample = np.zeros((self.game.get_num_fields(),))
        self.raw_data = np.zeros((self.game.get_num_fields(), 0))
        self.last_sample = np.zeros((self.game.get_num_fields(),))
        self.receive_results = np.zeros((self.game.get_num_fields(),))
        self.receive_results_raw = np.zeros((self.game.get_num_fields(),))
        self.last_receive_results = None
        self.new_state = GameState.race_not_running
        self.last_state = GameState.race_not_running
        self.has_new_data = False
        self.udp_socket = None

    @staticmethod
    def get_all_valid_games():
        valid_games = GameDirtRally.get_valid_game_names()  # + ...
        return valid_games

    def change_game(self, new_game_name):

        if new_game_name in GameDirtRally.get_valid_game_names():
            self.game_name = new_game_name
            self.game = GameDirtRally(game_name=new_game_name)

            if new_game_name != settings.settings['general']['game']:
                settings.settings['general']['game'] = new_game_name
                settings.write_settings()
        # elif game_name == 'Project Cars 2':
        #     self.game = GameProjectCars2()
        else:
            print("Invalid game name in settings: {}, reverting to '{}'".format(
                new_game_name, GameDirtRally.valid_game_name_dr2))
            settings.init_settings_game(GameDirtRally.valid_game_name_dr2)
            settings.write_settings()
            self.change_game(GameDirtRally.valid_game_name_dr2)

    def forward_datagram(self, datagram):
        # forward datagram to another socket
        # not necessary atm because you can simply duplicate the entry in the DR2 settings file
        try:
            networking.send_datagram(self.udp_socket, datagram,
                                     settings.settings['general']['ip_out'],
                                     int(settings.settings['general']['port_out']))
        except ValueError:
            print('Invalid output socket. Resetting...')
            settings.init_settings_output_socket()
            settings.write_settings()
            networking.send_datagram(self.udp_socket, datagram,
                                     settings.settings['general']['ip_out'],
                                     int(settings.settings['general']['port_out']))

    def save_run_data(self, data, automatic_name=False):
        # TODO: this will block the main thread and data from the port may be lost -> put in extra process
        import tkinter as tk
        from tkinter import filedialog
        from datetime import datetime

        try:
            os.makedirs(settings.settings['general']['session_path'], exist_ok=True)
        except ValueError:
            print('Invalid session path. Resetting...')
            settings.init_settings_session_path()
            settings.write_settings()
            os.makedirs(settings.settings['general']['session_path'], exist_ok=True)

        # assemble default name
        last_sample = self.session_collection[:, -1]
        car_name = self.game.get_car_name(last_sample)
        track_name = self.game.get_track_name(last_sample)
        race_time = self.game.get_race_duration(self.session_collection)
        total_race_time = '{:.1f}'.format(race_time)
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H_%M_%S')
        file_name = '{} - {} - {} - {}s.npz'.format(now_str, car_name, track_name, total_race_time)
        file_path = os.path.join(settings.settings['general']['session_path'], file_name)

        if not automatic_name:
            root = tk.Tk()
            root.withdraw()
            file_path = filedialog.asksaveasfilename(
                initialdir=settings.settings['general']['session_path'],
                initialfile=file_name,
                title='Save race log',
                filetypes=(("numpy", "*.npz"),))

        if file_path is not None and file_path != '' and file_path != '.npz':
            utils.make_dir_for_file(file_path)
            self.game.save_data(data, file_path)
            print('Saved {} data points to {}\n'.format(data.shape[1], os.path.abspath(file_path)))

    def save_run(self, automatic_name=False):
        self.save_run_data(data=self.session_collection, automatic_name=automatic_name)

    def load_run(self):
        # TODO: this will block the main thread and data from the port may be lost

        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            initialdir=settings.settings['general']['session_path'],
            title='Load race log',
            filetypes=(("numpy", "*.npz"), ("all files", "*.*")))
        if file_path is not None and file_path != '':
            if os.path.isfile(file_path):
                try:
                    race_data = self.game.load_data(file_path)
                    self.session_collection = race_data
                    print('Loaded {} data points from {}\n'.format(self.session_collection.shape[1], file_path))
                except ValueError as er:
                    print('Error while loading race data: {}\n{}'.format(file_path, er))

                if self.session_collection is not None and self.session_collection.shape[1] > 0:
                    self.last_sample = self.session_collection[:, -1]
            else:
                print('"{}" is no valid file!\n'.format(file_path))

    def get_game_state_str(self):
        return self.game.get_game_state_str(self.new_state, self.last_sample, self.session_collection.shape[1])

    def get_num_samples(self):
        return self.session_collection.shape[1]

    def clear_session_collection(self):
        self.session_collection = np.zeros((self.game.get_num_fields(), 0))
        self.first_sample = np.zeros((self.game.get_num_fields(),))
        self.last_receive_results = None

    def start_logging(self):
        self.udp_socket = networking.open_port(settings.settings['general']['ip_in'],
                                          int(settings.settings['general']['port_in']))
        if self.udp_socket is not None:
            print('Listening on socket {} for data from {}\n'.format(self.udp_socket.getsockname(), self.game_name))
        else:
            print('Invalid input socket. Resetting...')
            settings.init_settings_input_socket()
            settings.write_settings()
            self.udp_socket = networking.open_port(settings.settings['general']['ip_in'],
                                                   int(settings.settings['general']['port_in']))
            print('Listening on socket {}\n'.format(self.udp_socket.getsockname()))

        self.raw_data = np.zeros((self.game.get_num_fields(), 0)) if self.log_raw_data else None

        if self.debugging:  # start with plots

            self.session_collection = self.game.load_data(
                r'C:\Users\pherl\Desktop\2020-03-18 21_22_15 - Peugeot 208 R2 - Kakaristo - 451.7s raw.npz')
            self.show_plots()

    @staticmethod
    def accept_new_data(state):
        if state == GameState.race_not_running:
            return False
        elif state == GameState.race_running:
            return True
        elif state == GameState.ignore_package:
            return False
        else:
            raise ValueError('Unknown state: {}'.format(state))

    def check_udp_messages(self):
        self.receive_results, datagram = self.game.get_data(self.udp_socket)
        # forward_datagram(udp_socket=self.udp_socket, datagram=datagram, settings=settings)

        if self.receive_results is not None:
            if self.log_raw_data:
                self.receive_results_raw = np.expand_dims(self.receive_results, 1)
                if self.raw_data.size == 0:
                    self.raw_data = self.receive_results_raw
                else:
                    self.raw_data = np.append(self.session_collection, self.receive_results_raw, axis=1)

            self.new_state = self.game.get_game_state(self.receive_results, self.last_receive_results)
            self.last_sample = self.receive_results
            self.has_new_data = self.accept_new_data(self.new_state)
            if self.has_new_data:
                if self.session_collection.size == 0:
                    self.session_collection = np.expand_dims(self.receive_results, 1)
                else:
                    self.session_collection = np.append(self.session_collection,
                                                        np.expand_dims(self.receive_results, 1), axis=1)
        else:
            self.new_state = self.last_state
            self.has_new_data = False

    def show_plots(self):
        plot_data = self.game.get_plot_data(self.session_collection)
        if self.debugging:
            plots.plot_main(plot_data=plot_data)
        else:
            try:
                plots.plot_main(plot_data=plot_data)
            except Exception:
                print('Error during plot: {}'.format(sys.exc_info()))

    def check_state_changes(self):
        message = []

        # simply ignore state changes through duplicates
        if self.new_state == GameState.ignore_package:
            self.new_state = self.last_state

        if self.debugging and self.last_state != self.new_state:
            message += ['State changed from {} to {}'.format(self.last_state, self.new_state)]

        if self.last_state == GameState.race_running and \
                self.new_state == GameState.race_running:
            game_state_str = self.get_game_state_str()
            sys.stdout.write('\r' + game_state_str),
            sys.stdout.flush()

        if self.last_state == GameState.race_running and \
                self.new_state == GameState.race_not_running:
            sys.stdout.write('\n')
            sys.stdout.flush()

            race_duration = self.game.get_race_duration(self.session_collection)
            if race_duration > 10.0:  # only save if more than 10 sec of race time
                self.save_run_data(self.session_collection, automatic_name=True)
            message += ['Race finished']

            if self.log_raw_data:
                self.save_run_data(self.raw_data, automatic_name=False)
        elif self.last_state == GameState.race_not_running and \
                self.new_state == GameState.race_running:
            message += ['Race starting: {} on {}'.format(
                self.game.get_car_name(self.session_collection[:, -1]),
                self.game.get_track_name(self.session_collection[:, -1])
            )]
            if self.session_collection.shape[1] > 10:  # should only be less than 100 at the first race after startup
                message += ['Cleared {} data points'.format(self.session_collection.shape[1])]
            self.clear_session_collection()

        self.last_state = self.new_state
        if self.has_new_data:
            self.last_receive_results = self.receive_results.copy()

        message_str = '\n'.join(message)
        return message_str

    def end_logging(self):
        self.udp_socket.close()
