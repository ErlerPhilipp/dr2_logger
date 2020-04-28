
import numpy as np

from source import logger_backend
from source import plot_data as pd
from source import data_processing
from source.game_base import GameBase
from source.dr2 import udp_data
from source.dr2 import car_data
from source.dr2 import track_data


class GameDr2(GameBase):

    def __init__(self):
        self.unknown_cars = set()
        self.unknown_tracks = set()

    def get_game_state_str(self, state, last_sample, num_samples):

        state_str = '{car} on {track}, samples: {samples:05d}, lap time: {time:.1f}, ' \
                    'speed: {speed:.1f} m/s, rpm: {rpm:5.1f}, ' \
                    'progress: {progress:.2f}, distance: {distance:.1f}, run_time: {run_time:.1f}, ' \
                    '{state}'

        time = last_sample[udp_data.Fields.lap_time.value]
        speed = last_sample[udp_data.Fields.speed_ms.value]
        rpm = last_sample[udp_data.Fields.rpm.value]
        progress = last_sample[udp_data.Fields.progress.value]
        distance = last_sample[udp_data.Fields.distance.value]
        run_time = last_sample[udp_data.Fields.run_time.value]

        car_name = self.get_car_name(last_sample)
        track_name = self.get_track_name(last_sample)

        if state == logger_backend.GameState.race_not_running:
            state = 'race not running'
        elif state == logger_backend.GameState.race_running:
            state = 'race running'
        elif state == logger_backend.GameState.ignore_package:
            state = 'ignore package'
        else:
            raise ValueError('Invalid game state: {}'.format(state))

        state_str = state_str.format(
            car=car_name, track=track_name,
            samples=num_samples, time=time, speed=speed, rpm=rpm,
            progress=progress, distance=distance, run_time=run_time,
            state=state
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

    def get_race_duration(self, session_collection):
        race_time = session_collection[udp_data.Fields.run_time.value, -1] - \
                    session_collection[udp_data.Fields.run_time.value, 0]
        return race_time

    def get_track_name(self, sample):

        length = sample[udp_data.Fields.track_length.value]
        start_z = sample[udp_data.Fields.pos_z.value]

        if start_z is not None and length in track_data.track_dict.keys():
            track_candidates = track_data.track_dict[length]
            track_candidates_start_z = np.array([t[0] for t in track_candidates])
            track_candidates_start_z_dist = np.abs(track_candidates_start_z - start_z)
            best_match_id = np.argmin(track_candidates_start_z_dist)
            track_name = track_candidates[best_match_id][1]
        else:
            track_name = 'Unknown track ' + str((length, start_z))

            # debugging, data mining
            unknown_track_data = (length, start_z)
            if unknown_track_data not in self.unknown_cars:
                self.unknown_cars.add(unknown_track_data)
                with open('unknown tracks.txt', 'a+') as f:
                    f.write('[{}, {}, \'Unknown track\'],\n'.format(length, start_z))
        return track_name

    @staticmethod
    def get_run_time_cleaned(run_time_raw: np.ndarray):
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