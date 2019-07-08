import socket
import numpy as np
import struct
import os
import sys
import keyboard

UDP_IP = "127.0.0.1"
UDP_PORT = 10001


def bit_stream_to_float32(data, pos):

    value = struct.unpack('f', data[pos:pos+4])
    return value[0]


def receive(data):

    tTime = bit_stream_to_float32(data, 0)
    lapTime = bit_stream_to_float32(data, 4)
    distance = max(bit_stream_to_float32(data, 8), 0)
    # missing
    posx = bit_stream_to_float32(data, 16)
    posy = bit_stream_to_float32(data, 20)
    # missing
    speed = bit_stream_to_float32(data, 28) * 3.6  # * 3.6 for Km/h
    # missing
    suspAL = bit_stream_to_float32(data, 68)  # Suspension travel aft left
    suspAR = bit_stream_to_float32(data, 72)  # Suspension travel aft right
    suspFL = bit_stream_to_float32(data, 76)  # Suspension travel fwd left
    suspFR = bit_stream_to_float32(data, 80)  # Suspension travel fwd right
    # missing
    wspAL = bit_stream_to_float32(data, 100)  # Wheel speed aft left
    wspAR = bit_stream_to_float32(data, 104)  # Wheel speed aft right
    wspFL = bit_stream_to_float32(data, 108)  # Wheel speed fwd left
    wspFR = bit_stream_to_float32(data, 112)  # Wheel speed fwd right
    throttle = bit_stream_to_float32(data, 116)  # Throttle 0-1
    steering = bit_stream_to_float32(data, 120)
    brakes = bit_stream_to_float32(data, 124)  # Brakes 0-1
    clutch = bit_stream_to_float32(data, 128)  # Clutch 0-1
    gear = bit_stream_to_float32(data, 132)  # Gear, neutral = 0
    gForce_X = bit_stream_to_float32(data, 136)
    gForce_Y = bit_stream_to_float32(data, 140)
    cLap = bit_stream_to_float32(data, 144)  # Current lap, starts at 0
    rpm = bit_stream_to_float32(data, 148) * 10  # RPM, requires * 10 for realistic values

    return tTime, speed, rpm


print('Dirt Rally 2.0 Race Logger by Philipp Erler')
print('Press q to quit')

sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(0.01)

while True:
    try:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        new_data = True
    except socket.timeout as e:
        new_data = False

    if new_data:
        receive_results = receive(data)

        sys.stdout.write('\rData: {}'.format(receive_results) + ' '*20)
        sys.stdout.flush()

    if keyboard.is_pressed('q'):
        break

print('Ending...')


