import numpy as np
from dataclasses import dataclass


@dataclass
class PlotData:
    # times and progress
    run_time: np.ndarray  # raw times, what the player experiences, may skip penalties
    lap_time: np.ndarray  # includes penalties
    # last_lap_time: np.ndarray  # includes penalties
    distance: np.ndarray  # distance travelled in meters
    track_length: np.ndarray  # in meters
    progress: np.ndarray  # 0..1
    # car_pos: np.ndarray  # int: position in field
    # sector: np.ndarray  # int: sector of track
    # current_lap: np.ndarray  # int: lap number
    # laps_completed: np.ndarray  # int: lap number
    # total_laps: np.ndarray  # int: lap number

    # position and rotation, z axis is up
    pos_x: np.ndarray  # in meters
    pos_y: np.ndarray  # in meters
    pos_z: np.ndarray  # in meters
    speed_ms: np.ndarray  # forward velocity in m/s
    vel_x: np.ndarray  # in m/s
    vel_y: np.ndarray  # in m/s
    vel_z: np.ndarray  # in m/s
    roll_x: np.ndarray  # roll axis, back-front
    roll_y: np.ndarray  # roll axis, back-front
    roll_z: np.ndarray  # roll axis, back-front
    pitch_x: np.ndarray  # pitch axis, left-right
    pitch_y: np.ndarray  # pitch axis, left-right
    pitch_z: np.ndarray  # pitch axis, left-right

    # suspension and wheels
    susp_rl: np.ndarray  # suspension offset in mm
    susp_rr: np.ndarray  # suspension offset in mm
    susp_fl: np.ndarray  # suspension offset in mm
    susp_fr: np.ndarray  # suspension offset in mm
    susp_vel_rl: np.ndarray  # suspension velocity in mm/s
    susp_vel_rr: np.ndarray  # suspension velocity in mm/s
    susp_vel_fl: np.ndarray  # suspension velocity in mm/s
    susp_vel_fr: np.ndarray  # suspension velocity in mm/s
    wsp_rl: np.ndarray  # wheel velocity in m/s
    wsp_rr: np.ndarray  # wheel velocity in m/s
    wsp_fl: np.ndarray  # wheel velocity in m/s
    wsp_fr: np.ndarray  # wheel velocity in m/s
    # brakes_temp_rl: np.ndarray  # Celsius
    # brakes_temp_rr: np.ndarray  # Celsius
    # brakes_temp_fl: np.ndarray  # Celsius
    # brakes_temp_fr: np.ndarray  # Celsius

    # car data
    gear: np.ndarray  # int: -1, 0, .. max_gears
    g_force_lat: np.ndarray  # x * g
    g_force_lon: np.ndarray  # x * g
    rpm: np.ndarray  # RPM in 60/sec
    max_rpm: np.ndarray  # car max RPM in 60/sec
    idle_rpm: np.ndarray  # car max RPM in 60/sec
    max_gear: np.ndarray  # int: car max gear

    # user inputs
    throttle: np.ndarray  # raw input: 0..1
    steering: np.ndarray  # raw input: -1..+1
    brakes: np.ndarray  # raw input: 0..1
    clutch: np.ndarray  # raw input: 0..1
