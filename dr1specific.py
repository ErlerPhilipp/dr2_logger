import numpy as np
from enum import Enum
from collections import defaultdict

import networking


# adapted from https://github.com/soong-construction/dirt-rally-time-recorder/blob/master/cars.sql
# max_rpm, idle_rpm, car_name
car_data = [
    # 1960s
    [7330.38, 1047.2, 'Mini Cooper S'],
    [7833.04, 984.366, 'Lancia Fulvia HF'],
    [7853.98193359375, 1675.5160522460938, 'Renault Alpine A110'],

    # 1970s
    [8691.74, 1256.64, 'Opel Kadett GT/E 16v'],
    [8848.82, 1507.96, 'Fiat 131 Abarth'],
    [9424.78, 1047.2, 'Ford Escort Mk II'],
    [8377.58056640625, 1675.5160522460938, 'Lancia Stratos'],

    # 1980s
    [9424.78, 1256.64, 'BMW E30 Evo Rally'],
    [7853.98193359375, 1727.875213623047, 'Ford Sierra Cosworth RS500'],
    [8063.421630859375, 1308.9968872070312, 'Renault 5 Turbo'],

    # Group B 4WD)
    [10995.6, 1570.8, 'MG Metro 6R4'],
    [7330.38, 1151.92, 'Audi Sport Quattro Rallye'],
    [8901.18, 1256.64, 'Ford RS200'],
    [8377.58, 2094.39, 'Peugeot 205 T16 Evo 2 '],
    [8901.18, 1047.2, 'Lancia Delta S4'],

    # Group A
    [7853.98193359375, 1832.5953674316406, 'Lancia Delta HF Integrale'],
    [7853.98193359375, 2042.035369873047, 'Subaru Impreza 1995'],
    [7853.98193359375, 1780.236053466797, 'Ford Escort RS Cosworth'],

    # F2 Kit Car
    [9424.78, 1361.36, 'Seat Ibiza Kitcar'],
    [11519.2, 1466.07, 'Peugeot 306 Maxi'],

    # R4
    [7749.262084960938, 1675.5160522460938, 'Subaru Impreza WRX STI 2011'],
    [7853.98193359375, 1780.236053466797, 'Mitsubishi Lancer Evolution X'],

    # 2000s
    [7853.98193359375, 1570.7962036132812, 'Subaru Impreza 2001'],
    [7853.98193359375, 1780.236053466797, 'Ford Focus RS Rally 2001'],
    [7330.38330078125, 2094.3943786621094, 'Ford Focus RS Rally 2007'],
    [7330.38330078125, 2094.3943786621094, 'Citroen C4 Rally 2007'],

    # 2010s
    [7853.98193359375, 1675.5160522460938, 'Mini Countryman Rally Edition'],
    [7853.98, 1466.07, 'Ford Fiesta 2010'],
    [7330.38330078125, 2094.3943786621094, 'Hyundai Rally'],
    [7330.38, 1989.68, 'Volkswagen Polo Rally'],

    # Group B RWD)
    [8377.58, 1466.07, 'Opel Manta 400'],
    [8901.18, 1256.64, 'Lancia 037 Evo 2'],

    # Hillclimb
    [8377.58, 2094.39, 'Peugeot 205 T16 Pikes Peak'],
    [8377.58, 1570.8, 'Peugeot 405 T16 Pikes Peak'],
    [8639.38, 1413.72, 'Audi Sport Quattro S1 PP'],
    [8168.1396484375, 1884.9559020996094, 'Peugeot 208 T16 Pikes Peak'],

    # Rally GT
    [7330.3826904296875, 1466.07666015625, 'BMW M2 Challenge'],
]

# adapted from https://github.com/soong-construction/dirt-rally-time-recorder/blob/master/tracks.sql
# length, start_z, track_name
track_data = [
    # Argolis, Greece
    [4860.1904, 0.0, 'Ampelonas Ormi'],
    [9665.9902, 0.0, 'Kathodo Leontiou'],
    [5086.8301, 0.0, 'Pomono Ekrixi'],
    [4582.0098, 0.0, 'Koryfi Dafni'],
    [4515.4, 0.0, 'Fourketa Kourva'],
    [10688.0899, 0.0, 'Perasma Platani'],
    [10357.8799, 0.0, 'Tsiristra Theo'],
    [5739.0996, 0.0, 'Ourea Spevsi'],
    [5383.0098, 0.0, 'Ypsna tou Dasos'],
    [7089.4102, 0.0, 'Abies Koilada'],
    [6595.3101, 0.0, 'Pedines Epidaxi'],
    [9666.5, 0.0, 'Anodou Farmakas'],

    # Baumholder, Germany
    [5393.2197, 0.0, 'Waldaufstieg'],
    [6015.0796, 0.0, 'Waldabstieg'],
    [6318.71, 0.0, 'Kreuzungsring'],
    [5685.2798, 0.0, 'Kreuzungsring reverse'],
    [10699.96, 0.0, 'Ruschberg'],
    [5855.6802, 0.0, 'Verbundsring'],
    [5550.8599, 0.0, 'Verbundsring reverse'],
    [4937.8501, 0.0, 'Flugzeugring'],
    [5129.04, 0.0, 'Flugzeugring Reverse'],
    [11684.1699, 0.0, 'Oberstein'],
    [10805.2393, 0.0, 'Hammerstein'],
    [11684.2207, 0.0, 'Frauenberg'],

    # Monte Carlo, Monaco
    [10805.2207, 1289.7208, 'Route de Turini'],
    [10866.8604, -2358.05, 'Vallee descendante'],
    [4730.02, 298.587, 'Col de Turini – Sprint en descente'],
    [4729.54, -209.405, 'Col de Turini sprint en Montee'],
    [5175.9102, -120.206, 'Col de Turini – Descente'],
    [5175.9102, -461.134, 'Gordolon – Courte montee'],
    [4015.3599, -1005.69, 'Route de Turini (Descente)'],
    [3952.1501, 1289.7462, 'Approche du Col de Turini – Montee'],
    [9831.4502, -461.6663, 'Pra d´Alart'],
    [9831.9707, 297.6757, 'Col de Turini Depart'],
    [6843.3203, -977.825, 'Route de Turini (Montee)'],
    [6846.8301, -2357.89, 'Col de Turini – Depart en descente'],

    # Powys, Wales
    [4821.6499, 2034.5620, 'Pant Mawr Reverse'],
    [4993.2597, 1928.69, 'Bidno Moorland'],
    [5165.9501, 2470.99, 'Bidno Moorland Reverse'],
    [11435.5107, -553.109, 'River Severn Valley'],
    [11435.5508, 11435.6, 'Bronfelen'],
    [5717.3999, -553.112, 'Fferm Wynt'],
    [5717.3896, -21.5283, 'Fferm Wynt Reverse'],
    [5718.0996, -26.0434, 'Dyffryn Afon'],
    [5718.1001, 156.4742, 'Dyffryn Afon Reverse'],
    [9944.8701, 2216.3730, 'Sweet Lamb'],
    [10063.5898, 2470.7358, 'Geufron Forest'],
    [4788.6699, 2216.2036, 'Pant Mawr'],

    # Jämsä, Finland
    [7509.3798828125, 30.892242431640625, 'Kailajärvi'],
    [7553.4599609375, 895.6185913085938, 'Paskuri'],
    [7427.68994140625, 831.8955078125, 'Naarajärvi'],
    [7337.35986328125, -208.6328125, 'Jyrkysjärvi'],
    [16205.1904296875, 3767.812744140625, 'Kakaristo'],
    [16205.259765625, 819.3272705078125, 'Pitkäjärvi'],
    [8042.5205078125, 3767.791015625, 'Iso Oksjärvi'],
    [8057.52978515625, -3283.9921875, 'Oksala'],
    [8147.560546875, -3250.078125, 'Kotajärvi'],
    [8147.419921875, 819.4571533203125, 'Järvenkylä'],
    [15041.48046875, 30.879966735839844, 'Kontinjärvi'],
    [14954.6796875, -208.6311798095703, 'Hämelahti'],

    # Värmland, Sweden
    [7054.830078125, -1633.27197265625, 'Älgsjön'],
    [4911.22998046875, -1730.606689453125, 'Östra Hinnsjön'],
    [6666.27978515625, -2144.06689453125, 'Stor-jangen Sprint'],
    [6692.23974609375, 552.0279541015625, 'Stor-jangen Sprint Reverse'],
    [4932.33984375, -5107.74365234375, 'Björklangen'],
    [11920.2802734375, -4330.77490234375, 'Ransbysäter'],
    [12122.2001953125, 2713.06494140625, 'Hamra'],
    [12122.009765625, -5107.564453125, 'Lysvik'],
    [11500.720703125, 552.0166625976562, 'Norraskoga'],
    [5247.4599609375, -4330.759765625, 'Älgsjön Sprint'],
    [7057.25, 2713.06494140625, 'Elgsjön'],
    [4802.4599609375, -2143.044677734375, 'Skogsrallyt'],

    # Pikes Peak, USA
    [19476.4688, -4701.25, 'Pikes Peak - Full Course'],
    [6327.6899, -4700.96, 'Pikes Peak - Sector 1'],
    [6456.3604, -1122.07, 'Pikes Peak - Sector 2'],
    [7077.2002, 1397.84, 'Pikes Peak - Sector 3'],
    [19476.5, -4701.11, 'Pikes Peak (Mixed Surface) - Full Course'],
    [6327.7002, -4700.94, 'Pikes Peak (Mixed Surface) - Sector 1'],
    [6456.3702, -1122.23, 'Pikes Peak (Mixed Surface) - Sector 2'],
    [7077.21, 1397.82, 'Pikes Peak (Mixed Surface) - Sector 3'],
    [19476.5, -4701.11, 'Pikes Peak (Gravel) - Full Course'],
    [6327.7002, -4700.94, 'Pikes Peak (Gravel) - Sector 1'],
    [6456.3702, -1122.23, 'Pikes Peak (Gravel) - Sector 2'],
    [7077.21, 1397.82, 'Pikes Peak (Gravel) - Sector 3'],
]


car_dict = dict()
for d in car_data:
    car_dict[(d[0], d[1])] = d[2]

# track length is not a unique key as some tracks are just reversed
# it's unique together with the starting position, which is not accurate to float precision
track_dict = defaultdict(list)
for t in track_data:
    track_dict[t[0]].append((t[1], t[2]))


class GameState(Enum):
    error = 0
    race_start = 1
    race_running = 2
    duplicate_package = 3
    race_finished_or_service_area = 4


def get_car_name(max_rpm, idle_rpm):
    key = (max_rpm, idle_rpm)
    if key in car_dict.keys():
        car_name = car_dict[key]
    else:
        car_name = 'Unknown car ' + str(key)
    return car_name


def get_track_name(length, start_z):
    if start_z is not None and length in track_dict.keys():
        track_candidates = track_dict[length]
        track_candidates_start_z = np.array([t[0] for t in track_candidates])
        track_candidates_start_z_dist = np.abs(track_candidates_start_z - start_z)
        best_match_id = np.argmin(track_candidates_start_z_dist)
        track_name = track_candidates[best_match_id][1]
    else:
        track_name = 'Unknown track ' + str((length, start_z))
    return track_name


def get_game_state_str(state, receive_results, num_samples, start_z):

    if state == GameState.error:
        return None

    state_str = '{car} on {track}, samples: {samples:05d}, lap time: {time:.1f}, ' \
                'speed: {speed:.1f} m/s, rpm {rpm:5.1f}, {state}'

    max_rpm = receive_results[networking.Fields.max_rpm.value]
    idle_rpm = receive_results[networking.Fields.idle_rpm.value]
    track_length = receive_results[networking.Fields.track_length.value]
    # start_z = receive_results[networking.Fields.pos_z.value]
    time = receive_results[networking.Fields.lap_time.value]
    speed = receive_results[networking.Fields.speed_ms.value]
    rpm = receive_results[networking.Fields.rpm.value]

    car_name = get_car_name(max_rpm, idle_rpm)
    track_name = get_track_name(track_length, start_z)

    if state == GameState.race_start:
        state = 'race starting'
    elif state == GameState.race_running:
        state = 'race running'
    elif state == GameState.duplicate_package:
        state = 'duplicate package'
    elif state == GameState.race_finished_or_service_area:
        state = 'race finished or in service area'
    else:
        raise ValueError('Invalid game state: {}'.format(state))

    state_str = state_str.format(
        car=car_name, track=track_name, samples=num_samples, time=time, speed=speed, rpm=rpm, state=state
    )
    return state_str


def get_game_state(receive_results, last_receive_results):

    if receive_results is None:  # no data, error in receive?
        return GameState.error

    # all values zero -> probably in finish
    # strange lap time = 0 and progress near 2 suddenly -> over finish line
    if np.all(receive_results == np.zeros_like(receive_results)) or \
        (receive_results[networking.Fields.lap_time.value] == 0.0 and
         receive_results[networking.Fields.progress.value] >= 1.0):
        return GameState.race_finished_or_service_area

    # race has not yet started
    if receive_results[networking.Fields.lap_time.value] == 0.0:
        return GameState.race_start

    # all equal except the run time -> new package, same game state in DR2 -> race paused
    if last_receive_results is not None and \
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

