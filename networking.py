import numpy as np
import socket
import struct

# https://docs.google.com/spreadsheets/d/1eA518KHFowYw7tSMa-NxIFYpiWe5JXgVVQ_IMs7BVW0/edit?usp=drivesdk
fields = {
    'run_time':            0,
    'lap_time':            1,
    'distance':            2,
    'progress':            3,
    'pos_x':               4,
    'pos_y':               5,
    'pos_z':               6,
    'speed_ms':            7,
    'vel_x':               8,
    'vel_y':               9,
    'vel_z':               10,
    'roll_x':              11,
    'roll_y':              12,
    'roll_z':              13,
    'pitch_x':             14,
    'pitch_y':             15,
    'pitch_z':             16,
    'susp_rl':             17,
    'susp_rr':             18,
    'susp_fl':             19,
    'susp_fr':             20,
    'susp_vel_rl':         21,
    'susp_vel_rr':         22,
    'susp_vel_fl':         23,
    'susp_vel_fr':         24,
    'wsp_rl':              25,
    'wsp_rr':              26,
    'wsp_fl':              27,
    'wsp_fr':              28,
    'throttle':            29,
    'steering':            30,
    'brakes':              31,
    'clutch':              32,
    'gear':                33,
    'g_force_lat':         34,
    'g_force_lon':         35,
    'current_lap':         36,
    'rpm':                 37,
    'sli_pro_support':     38,
    'car_pos':             39,
    'kers_level':          40,
    'kers_max_level':      41,
    'drs':                 42,
    'traction_control':    43,
    'anti_lock_brakes':    44,
    'fuel_in_tank':        45,
    'fuel_capacity':       46,
    'in_pit':              47,
    'sector':              48,
    'sector_1_time':       49,
    'sector_2_time':       50,
    'brakes_temp':         51,
    'wheels_pressure_psi': 52,
    'team_info':           53,
    'total_laps':          54,
    'track_size':          55,
    'last_lap_time':       56,
    'max_rpm':             57,
    'idle_rpm':            58,
    'max_gears':           59,
    'session_type':        60,
    'drs_allowed':         61,
    'track_number':        62,
    'vehicle_fia_flags':   63,
    'unknown_0':           64,
    'unknown_1':           65,
}


def bit_stream_to_float32(data, pos):
    try:
        value = struct.unpack('f', data[pos:pos+4])
    except ValueError as e:
        value = 0
        print('Failed to get data item at pos {}'.format(pos))
    return value[0]


def receive(udp_socket):
    try:
        data, addr = udp_socket.recvfrom(1024)  # buffer size is 1024 bytes
    except socket.timeout as e:
        return None

    run_time = bit_stream_to_float32(data, 0)
    lap_time = bit_stream_to_float32(data, 4)
    distance = max(bit_stream_to_float32(data, 8), 0)
    progress = bit_stream_to_float32(data, 12)  # 0-1
    pos_x = bit_stream_to_float32(data, 16)
    pos_y = bit_stream_to_float32(data, 20)
    pos_z = bit_stream_to_float32(data, 24)
    speed_ms = bit_stream_to_float32(data, 28)  # * 3.6  # * 3.6 for Km/h
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
    steering = bit_stream_to_float32(data, 120)
    brakes = bit_stream_to_float32(data, 124)  # Brakes 0-1
    clutch = bit_stream_to_float32(data, 128)  # Clutch 0-1
    gear = bit_stream_to_float32(data, 132)  # Gear, neutral = 0
    g_force_lat = bit_stream_to_float32(data, 136)
    g_force_lon = bit_stream_to_float32(data, 140)
    current_lap = bit_stream_to_float32(data, 144)  # Current lap, starts at 0
    rpm = bit_stream_to_float32(data, 148) * 10  # RPM, requires * 10 for realistic values
    sli_pro_support = bit_stream_to_float32(data, 152)
    car_pos = bit_stream_to_float32(data, 156)
    kers_level = bit_stream_to_float32(data, 160)
    kers_max_level = bit_stream_to_float32(data, 164)
    drs = bit_stream_to_float32(data, 168)
    traction_control = bit_stream_to_float32(data, 172)
    anti_lock_brakes = bit_stream_to_float32(data, 176)
    fuel_in_tank = bit_stream_to_float32(data, 180)
    fuel_capacity = bit_stream_to_float32(data, 184)
    in_pit = bit_stream_to_float32(data, 188)
    sector = bit_stream_to_float32(data, 192)
    sector_1_time = bit_stream_to_float32(data, 196)
    sector_2_time = bit_stream_to_float32(data, 200)
    brakes_temp = bit_stream_to_float32(data, 204)
    wheels_pressure_psi = bit_stream_to_float32(data, 208)
    team_info = bit_stream_to_float32(data, 212)
    total_laps = bit_stream_to_float32(data, 216)
    track_size = bit_stream_to_float32(data, 220)
    last_lap_time = bit_stream_to_float32(data, 224)
    max_rpm = bit_stream_to_float32(data, 228)
    idle_rpm = bit_stream_to_float32(data, 232)
    max_gears = bit_stream_to_float32(data, 236)
    session_type = bit_stream_to_float32(data, 240)
    drs_allowed = bit_stream_to_float32(data, 244)
    track_number = bit_stream_to_float32(data, 248)
    vehicle_fia_flags = bit_stream_to_float32(data, 252)
    unknown_0 = bit_stream_to_float32(data, 256)
    unknown_1 = bit_stream_to_float32(data, 260)

    return np.array([
        run_time, lap_time, distance, progress, pos_x, pos_y, pos_z, speed_ms, vel_x, vel_y, vel_z,
        roll_x, roll_y, roll_z, pitch_x, pitch_y, pitch_z, susp_rl, susp_rr, susp_fl, susp_fr,
        susp_vel_rl, susp_vel_rr, susp_vel_fl, susp_vel_fr, wsp_rl, wsp_rr, wsp_fl, wsp_fr,
        throttle, steering, brakes, clutch, gear, g_force_lat, g_force_lon, current_lap, rpm, sli_pro_support, car_pos,
        kers_level, kers_max_level, drs, traction_control, anti_lock_brakes, fuel_in_tank, fuel_capacity, in_pit,
        sector, sector_1_time, sector_2_time, brakes_temp, wheels_pressure_psi, team_info, total_laps, track_size,
        last_lap_time, max_rpm, idle_rpm, max_gears, session_type, drs_allowed, track_number, vehicle_fia_flags,
        unknown_0, unknown_1
    ])


def get_port():

    try:
        port_str = input('Enter port (default 10001): ')
        if port_str is None or port_str == '':
            return 10001
        else:
            port_int = int(port_str)
            return port_int
    except ValueError as e:
        return 10001


def open_port(port):

    udp_ip = "127.0.0.1"
    udp_port = port
    udp_socket = socket.socket(socket.AF_INET,  # Internet
                               socket.SOCK_DGRAM)  # UDP
    udp_socket.bind((udp_ip, udp_port))
    udp_socket.settimeout(0.01)
    return udp_socket

