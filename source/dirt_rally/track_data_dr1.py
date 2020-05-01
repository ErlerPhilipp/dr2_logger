from collections import defaultdict

# adapted from https://github.com/soong-construction/dirt-rally-time-recorder/blob/master/resources/setup-dr1.sql
# length, start_z, track_name
track_data = [
    # RX
    [1348.85400390625,    96.47221374511719, 'England Full'],
    [1036.0970458984375, 125.0980453491211,  'Norway Full'],
    [1207.18798828125,   173.65447998046875, 'Sweden Full'],
    [575.1746215820312,   96.56448364257812, 'England Junior'],
    [985.9498901367188,  125.1002197265625,  'Norway Clubman'],
    [682.9323120117188,  -66.44092559814453, 'Sweden Junior'],
    [989.7551879882812,   96.58692169189453, 'England Clubman'],
    [936.9108276367188,  173.6415557861328,  'Sweden Clubman'],

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

# track length is not a unique key as some tracks are just reversed
# it's unique together with the starting position, which is not accurate to float precision
track_dict = defaultdict(list)
for t in track_data:
    track_dict[t[0]].append((t[1], t[2]))

