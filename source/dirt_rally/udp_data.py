import numpy as np
import socket
import struct
from enum import Enum

debugging = False  # enable to simulate incoming UDP datagrams
debugging_counter = -1
if debugging:
    debug_data = np.load(
        r'C:\Users\pherl\Desktop\2020-03-18 21_22_15 - Peugeot 208 R2 - Kakaristo - 451.7s raw.npz')['arr_0']
else:
    debug_data = None

# https://docs.google.com/spreadsheets/d/1UTgeE7vbnGIzDz-URRk2eBIPc_LR1vWcZklp7xD9N0Y/edit#gid=0
# https://github.com/soong-construction/


class Fields(Enum):
    run_time =            0
    lap_time =            1
    distance =            2
    progress =            3
    pos_x =               4
    pos_y =               5
    pos_z =               6
    speed_ms =            7
    vel_x =               8
    vel_y =               9
    vel_z =               10
    roll_x =              11
    roll_y =              12
    roll_z =              13
    pitch_x =             14
    pitch_y =             15
    pitch_z =             16
    susp_rl =             17
    susp_rr =             18
    susp_fl =             19
    susp_fr =             20
    susp_vel_rl =         21
    susp_vel_rr =         22
    susp_vel_fl =         23
    susp_vel_fr =         24
    wsp_rl =              25
    wsp_rr =              26
    wsp_fl =              27
    wsp_fr =              28
    throttle =            29
    steering =            30
    brakes =              31
    clutch =              32
    gear =                33
    g_force_lat =         34
    g_force_lon =         35
    current_lap =         36
    rpm =                 37  # / 10
    sli_pro_support =     38  # ignored
    car_pos =             39
    kers_level =          40  # ignored
    kers_max_level =      41  # ignored
    drs =                 42  # ignored
    traction_control =    43  # ignored
    anti_lock_brakes =    44  # ignored
    fuel_in_tank =        45  # ignored
    fuel_capacity =       46  # ignored
    in_pit =              47  # ignored
    sector =              48
    sector_1_time =       49
    sector_2_time =       50
    brakes_temp_rl =      51
    brakes_temp_rr =      52
    brakes_temp_fl =      53
    brakes_temp_fr =      54
    tyre_pressure_rl =    55  # ignored
    tyre_pressure_rr =    56  # ignored
    tyre_pressure_fl =    57  # ignored
    tyre_pressure_fr =    58  # ignored
    laps_completed =      59
    total_laps =          60
    track_length =        61
    last_lap_time =       62
    max_rpm =             63  # / 10
    idle_rpm =            64  # / 10
    max_gears =           65


num_fields = 66


def bit_stream_to_float32(data, pos):
    try:
        value = struct.unpack('f', data[pos:pos+4])[0]
    except struct.error as _:
        value = 0
        # print('Failed to get data item at pos {}'.format(pos))
    except Exception as e:
        value = 0
        print('Failed to get data item at pos {}. Make sure to set extradata=3 in the hardware settings.'.format(pos))
    return value


def receive(udp_socket):

    global debugging
    global debugging_counter
    global debug_data
    if debugging:
        import time
        time.sleep(0.01)
        debugging_counter += 1
        return debug_data[:, debugging_counter], None

    if udp_socket is None:
        return None, None

    try:
        data, addr = udp_socket.recvfrom(1024)  # buffer size is 1024 bytes
    except socket.timeout as _:
        return None, None

    run_time = bit_stream_to_float32(data, 0)
    lap_time = bit_stream_to_float32(data, 4)
    distance = max(bit_stream_to_float32(data, 8), 0)
    progress = bit_stream_to_float32(data, 12)  # 0-1
    pos_x = bit_stream_to_float32(data, 16)
    pos_y = bit_stream_to_float32(data, 20)
    pos_z = bit_stream_to_float32(data, 24)
    speed_ms = bit_stream_to_float32(data, 28)  # * 3.6 for Km/h
    vel_x = bit_stream_to_float32(data, 32)  # velocity in world space
    vel_y = bit_stream_to_float32(data, 36)  # velocity in world space
    vel_z = bit_stream_to_float32(data, 40)  # velocity in world space
    roll_x = bit_stream_to_float32(data, 44)
    roll_y = bit_stream_to_float32(data, 48)
    roll_z = bit_stream_to_float32(data, 52)
    pitch_x = bit_stream_to_float32(data, 56)
    pitch_y = bit_stream_to_float32(data, 60)
    pitch_z = bit_stream_to_float32(data, 64)
    susp_rl = bit_stream_to_float32(data, 68)  # Suspension travel aft left
    susp_rr = bit_stream_to_float32(data, 72)  # Suspension travel aft right
    susp_fl = bit_stream_to_float32(data, 76)  # Suspension travel fwd left
    susp_fr = bit_stream_to_float32(data, 80)  # Suspension travel fwd right
    susp_vel_rl = bit_stream_to_float32(data, 84)
    susp_vel_rr = bit_stream_to_float32(data, 88)
    susp_vel_fl = bit_stream_to_float32(data, 92)
    susp_vel_fr = bit_stream_to_float32(data, 96)
    wsp_rl = bit_stream_to_float32(data, 100)  # Wheel speed aft left
    wsp_rr = bit_stream_to_float32(data, 104)  # Wheel speed aft right
    wsp_fl = bit_stream_to_float32(data, 108)  # Wheel speed fwd left
    wsp_fr = bit_stream_to_float32(data, 112)  # Wheel speed fwd right
    throttle = bit_stream_to_float32(data, 116)  # Throttle 0-1
    steering = bit_stream_to_float32(data, 120)  # -1..+1
    brakes = bit_stream_to_float32(data, 124)  # Brakes 0-1
    clutch = bit_stream_to_float32(data, 128)  # Clutch 0-1
    gear = bit_stream_to_float32(data, 132)  # Gear, neutral = 0
    g_force_lat = bit_stream_to_float32(data, 136)
    g_force_lon = bit_stream_to_float32(data, 140)
    current_lap = bit_stream_to_float32(data, 144)  # Current lap, starts at 0
    rpm = bit_stream_to_float32(data, 148)  # RPM, requires * 10 for realistic values
    sli_pro_support = bit_stream_to_float32(data, 152)  # ignored
    car_pos = bit_stream_to_float32(data, 156)
    kers_level = bit_stream_to_float32(data, 160)  # ignored
    kers_max_level = bit_stream_to_float32(data, 164)  # ignored
    drs = bit_stream_to_float32(data, 168)  # ignored
    traction_control = bit_stream_to_float32(data, 172)  # ignored
    anti_lock_brakes = bit_stream_to_float32(data, 176)  # ignored
    fuel_in_tank = bit_stream_to_float32(data, 180)  # ignored
    fuel_capacity = bit_stream_to_float32(data, 184)  # ignored
    in_pit = bit_stream_to_float32(data, 188)  # ignored
    sector = bit_stream_to_float32(data, 192)
    sector_1_time = bit_stream_to_float32(data, 196)
    sector_2_time = bit_stream_to_float32(data, 200)
    brakes_temp_rl = bit_stream_to_float32(data, 204)
    brakes_temp_rr = bit_stream_to_float32(data, 208)
    brakes_temp_fl = bit_stream_to_float32(data, 212)
    brakes_temp_fr = bit_stream_to_float32(data, 216)
    tyre_pressure_rl = bit_stream_to_float32(data, 220)
    tyre_pressure_rr = bit_stream_to_float32(data, 224)
    tyre_pressure_fl = bit_stream_to_float32(data, 228)
    tyre_pressure_fr = bit_stream_to_float32(data, 232)
    laps_completed = bit_stream_to_float32(data, 236)
    total_laps = bit_stream_to_float32(data, 240)
    track_length = bit_stream_to_float32(data, 244)
    last_lap_time = bit_stream_to_float32(data, 248)
    max_rpm = bit_stream_to_float32(data, 252)  # requires * 10 for realistic values
    idle_rpm = bit_stream_to_float32(data, 256)  # requires * 10 for realistic values
    max_gears = bit_stream_to_float32(data, 260)

    return np.array([
        run_time, lap_time, distance, progress, pos_x, pos_y, pos_z, speed_ms, vel_x, vel_y, vel_z,
        roll_x, roll_y, roll_z, pitch_x, pitch_y, pitch_z, susp_rl, susp_rr, susp_fl, susp_fr,
        susp_vel_rl, susp_vel_rr, susp_vel_fl, susp_vel_fr, wsp_rl, wsp_rr, wsp_fl, wsp_fr,
        throttle, steering, brakes, clutch, gear, g_force_lat, g_force_lon, current_lap, rpm, sli_pro_support, car_pos,
        kers_level, kers_max_level, drs, traction_control, anti_lock_brakes, fuel_in_tank, fuel_capacity, in_pit,
        sector, sector_1_time, sector_2_time, brakes_temp_rl, brakes_temp_rr, brakes_temp_fl, brakes_temp_fr,
        tyre_pressure_rl, tyre_pressure_rr, tyre_pressure_fl, tyre_pressure_fr, laps_completed,
        total_laps, track_length, last_lap_time, max_rpm, idle_rpm, max_gears
    ]), data

