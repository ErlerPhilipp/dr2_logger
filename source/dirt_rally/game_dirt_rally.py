import time

import numpy as np

from source import logger_backend
from source import plot_data as pd
from source import data_processing
from source.game_base import GameBase
from source.dirt_rally import udp_data
from source.dirt_rally import car_data_dr1
from source.dirt_rally import track_data_dr1
from source.dirt_rally import car_data_dr2
from source.dirt_rally import track_data_dr2


class GameDirtRally(GameBase):

    valid_game_name_dr1 = 'Dirt_Rally_1'
    valid_game_name_dr2 = 'Dirt_Rally_2'
    current_save_version = '1.0.0'

    def __init__(self, game_name):
        self.unknown_cars = set()
        self.unknown_tracks = set()
        if game_name != GameDirtRally.valid_game_name_dr1 and game_name != GameDirtRally.valid_game_name_dr2:
            raise ValueError('Invalid game name: {}'.format(game_name))
        self.game_name = game_name

    @staticmethod
    def get_valid_game_names():
        return [GameDirtRally.valid_game_name_dr1, GameDirtRally.valid_game_name_dr2]

    def load_data(self, file_path):
        npz_file = np.load(file_path)
        if 'arr_0' in npz_file:
            # initial simple saves
            samples = npz_file['arr_0']

            # RPM values were saved with x10 factor -> revert here
            samples[udp_data.Fields.rpm.value] /= 10.0
            samples[udp_data.Fields.max_rpm.value] /= 10.0
            samples[udp_data.Fields.idle_rpm.value] /= 10.0
        else:
            required_values = ['samples', 'game', 'save_version']
            for v in required_values:
                required_value_exists = v in npz_file
                if not required_value_exists:
                    raise ValueError('Saved race doesn\'t contain the required field "{}"'.format(v))
            game_name = npz_file['game']
            if game_name != self.game_name:
                raise ValueError('The saved race "{}" is from game: "{}". '
                                 'Switch the logger\'s game mode with "g {}".'.format(file_path, game_name, game_name))
            save_version = npz_file['save_version']
            if save_version == '1.0.0':
                samples = npz_file['samples']
            else:
                raise ValueError('Unknown save version "{}" for game "{}"'.format(save_version, game_name))
        return samples

    def save_data(self, data, file_path):
        np.savez_compressed(file_path, samples=data, game=self.game_name,
                            save_version=GameDirtRally.current_save_version)

    def get_game_state_str(self, state, last_sample, num_samples, bar_length=16):

        state_str = 'Race Logger {progress} Time: {time}, ' \
                    'ETA: {eta}, ' \
                    'Speed: {speed:.1f} m/s, RPM: {rpm:5.0f}, ' \
                    'Samples: {samples:05d}, {state}'

        current_time = last_sample[udp_data.Fields.lap_time.value]
        current_time_str = time.strftime('%M:%S', time.gmtime(current_time))
        progress_raw = last_sample[udp_data.Fields.progress.value]
        num_laps = max(1, last_sample[udp_data.Fields.total_laps.value])
        progress = progress_raw / num_laps
        filled_length = int(round(bar_length * progress))
        progress_str = '|' + f'{"█" * filled_length}{"-" * (bar_length - filled_length)}' + '|'
        eta = 0.0 if progress <= 0.0 else current_time * (1.0 / progress)
        eta_str = time.strftime('%M:%S', time.gmtime(eta))
        speed = last_sample[udp_data.Fields.speed_ms.value]
        rpm = last_sample[udp_data.Fields.rpm.value]

        if state == logger_backend.GameState.race_not_running:
            state = 'not racing'
        elif state == logger_backend.GameState.race_running:
            state = 'racing'
        elif state == logger_backend.GameState.ignore_package:
            state = 'paused'
        else:
            raise ValueError('Invalid game state: {}'.format(state))

        state_str = state_str.format(
            samples=num_samples, time=current_time_str, eta=eta_str, speed=speed, rpm=rpm * 10.0,
            progress=progress_str, state=state
        )
        return state_str

    def get_game_state(self, receive_results, last_receive_results):

        # no new data
        if receive_results is None:
            return logger_backend.GameState.ignore_package

        # all equal except the run time -> new package, same game state in DR2 -> race is paused
        if last_receive_results is not None and \
                np.all(receive_results[1:] == last_receive_results[1:]):
            return logger_backend.GameState.ignore_package

        # if receive_results[udp_data.Fields.progress.value] > 0.0:
        if receive_results[udp_data.Fields.lap_time.value] > 0.0:
            return logger_backend.GameState.race_running

        # race has not yet started
        if receive_results[udp_data.Fields.lap_time.value] == 0.0:
            return logger_backend.GameState.race_not_running
        if receive_results[udp_data.Fields.distance.value] <= 0.0:
            return logger_backend.GameState.race_not_running

        # RPM will never be zero at the start (it will be the idle RPM)
        # However, RPM can be zero for some reason in the service area. Ignore then.
        # TODO: check if RPM can be zero when the engine dies
        if receive_results[udp_data.Fields.rpm.value] == 0.0 and receive_results[udp_data.Fields.run_time.value] <= 0.1:
            return logger_backend.GameState.ignore_package

        # strange packages with position at zero after race, speed check to be sure
        if receive_results[udp_data.Fields.pos_y.value] == 0.0 and \
                receive_results[udp_data.Fields.speed_ms.value] == 0.0:
            return logger_backend.GameState.race_not_running

        print('Unknown reason for "not running": progress={}'.format(receive_results[udp_data.Fields.progress.value]))
        return logger_backend.GameState.race_not_running

    def get_fields_enum(self):
        return udp_data.Fields

    def get_num_fields(self):
        return udp_data.num_fields

    def get_data(self, udp_socket):
        return udp_data.receive(udp_socket=udp_socket)

    def get_car_name(self, sample):
        max_rpm = sample[udp_data.Fields.max_rpm.value]
        idle_rpm = sample[udp_data.Fields.idle_rpm.value]
        max_gears = sample[udp_data.Fields.max_gears.value]

        key = (max_rpm, idle_rpm, max_gears)
        car_data = car_data_dr1 if self.game_name == GameDirtRally.valid_game_name_dr1 else car_data_dr2
        if key in car_data.car_dict.keys():
            car_name = car_data.car_dict[key]
        else:
            car_name = 'Unknown car ' + str(key)

            # debugging, data mining
            unknown_car_data = (max_rpm, idle_rpm, max_gears)
            if unknown_car_data not in self.unknown_cars:
                self.unknown_cars.add(unknown_car_data)
                with open('unknown cars.txt', 'a+') as f:
                    f.write('[{}, {}, {}, \'Unknown car\'],\n'.format(max_rpm, idle_rpm, max_gears))

        return car_name

    def get_race_duration(self, session_collection: np.ndarray):
        if session_collection.shape[1] == 0:
            return 0.0
        else:
            race_time = session_collection[udp_data.Fields.run_time.value, -1] - \
                        session_collection[udp_data.Fields.run_time.value, 0]
            return race_time

    def get_progress(self, session_collection):
        if session_collection.shape[1] == 0:
            return 0.0
        else:
            return session_collection[udp_data.Fields.progress.value, -1]

    def get_track_name(self, sample):

        length = sample[udp_data.Fields.track_length.value]
        start_z = sample[udp_data.Fields.pos_z.value]

        track_data = track_data_dr1 if self.game_name == GameDirtRally.valid_game_name_dr1 else track_data_dr2
        if start_z is not None and length in track_data.track_dict.keys():
            track_candidates = track_data.track_dict[length]
            track_candidates_start_z = np.array([t[0] for t in track_candidates])
            track_candidates_start_z_dist = np.abs(track_candidates_start_z - start_z)
            best_match_id = np.argmin(track_candidates_start_z_dist)
            track_name = track_candidates[best_match_id][1]
        else:
            track_name = 'Unknown track ' + str((length, start_z))

            # debugging, data mining
            unknown_track_data = (length,)
            if unknown_track_data not in self.unknown_cars:
                self.unknown_cars.add(unknown_track_data)
                with open('unknown tracks.txt', 'a+') as f:
                    f.write('[{}, {}, \'Unknown track\'],\n'.format(length, start_z))
        return track_name

    @staticmethod
    def get_run_time_cleaned(run_time_raw: np.ndarray):
        if run_time_raw.shape[0] == 0:
            return np.array([0.0])
        else:
            start_time = run_time_raw[0]
            run_time_cleaned = run_time_raw - start_time
            return run_time_cleaned

    def get_plot_data(self, session_collection):

        # make consistent with other games
        run_time = self.get_run_time_cleaned(session_collection[udp_data.Fields.run_time.value])
        rpm = session_collection[udp_data.Fields.rpm.value] * 10.0
        max_rpm = session_collection[udp_data.Fields.max_rpm.value] * 10.0
        idle_rpm = session_collection[udp_data.Fields.idle_rpm.value] * 10.0

        # switch coordinate system to z - up
        pos_x, pos_y, pos_z = data_processing.convert_coordinate_system_3d(
            session_collection[udp_data.Fields.pos_x.value],
            session_collection[udp_data.Fields.pos_y.value],
            session_collection[udp_data.Fields.pos_z.value]
        )
        vel_x, vel_y, vel_z = data_processing.convert_coordinate_system_3d(
            session_collection[udp_data.Fields.vel_x.value],
            session_collection[udp_data.Fields.vel_y.value],
            session_collection[udp_data.Fields.vel_z.value]
        )
        pitch_x, pitch_y, pitch_z = data_processing.convert_coordinate_system_3d(
            session_collection[udp_data.Fields.roll_x.value],
            session_collection[udp_data.Fields.roll_y.value],
            session_collection[udp_data.Fields.roll_z.value]
        )
        roll_x, roll_y, roll_z = data_processing.convert_coordinate_system_3d(
            session_collection[udp_data.Fields.pitch_x.value],
            session_collection[udp_data.Fields.pitch_y.value],
            session_collection[udp_data.Fields.pitch_z.value],
        )

        plot_data = pd.PlotData(
            run_time=run_time,
            lap_time=session_collection[udp_data.Fields.lap_time.value],
            distance=session_collection[udp_data.Fields.distance.value],
            track_length=session_collection[udp_data.Fields.track_length.value],
            progress=session_collection[udp_data.Fields.progress.value],
            pos_x=pos_x,
            pos_y=pos_y,
            pos_z=pos_z,
            speed_ms=session_collection[udp_data.Fields.speed_ms.value],
            vel_x=vel_x,
            vel_y=vel_y,
            vel_z=vel_z,
            roll_x=roll_x,
            roll_y=roll_y,
            roll_z=roll_z,
            pitch_x=pitch_x,
            pitch_y=pitch_y,
            pitch_z=pitch_z,
            susp_rl=session_collection[udp_data.Fields.susp_rl.value],
            susp_rr=session_collection[udp_data.Fields.susp_rr.value],
            susp_fl=session_collection[udp_data.Fields.susp_fl.value],
            susp_fr=session_collection[udp_data.Fields.susp_fr.value],
            susp_vel_rl=session_collection[udp_data.Fields.susp_vel_rl.value],
            susp_vel_rr=session_collection[udp_data.Fields.susp_vel_rr.value],
            susp_vel_fl=session_collection[udp_data.Fields.susp_vel_fl.value],
            susp_vel_fr=session_collection[udp_data.Fields.susp_vel_fr.value],
            wsp_rl=session_collection[udp_data.Fields.wsp_rl.value],
            wsp_rr=session_collection[udp_data.Fields.wsp_rr.value],
            wsp_fl=session_collection[udp_data.Fields.wsp_fl.value],
            wsp_fr=session_collection[udp_data.Fields.wsp_fr.value],
            gear=session_collection[udp_data.Fields.gear.value],
            g_force_lat=session_collection[udp_data.Fields.g_force_lat.value],
            g_force_lon=session_collection[udp_data.Fields.g_force_lon.value],
            rpm=rpm,
            max_rpm=max_rpm,
            idle_rpm=idle_rpm,
            max_gear=session_collection[udp_data.Fields.max_gears.value],
            throttle=session_collection[udp_data.Fields.throttle.value],
            steering=session_collection[udp_data.Fields.steering.value],
            brakes=session_collection[udp_data.Fields.brakes.value],
            clutch=session_collection[udp_data.Fields.clutch.value]
        )

        return plot_data
