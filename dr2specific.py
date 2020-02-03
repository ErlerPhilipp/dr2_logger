import numpy as np
from enum import Enum
from collections import defaultdict

import networking


# adapted from https://github.com/soong-construction/dirt-rally-time-recorder/blob/master/cars.sql
# max_rpm, idle_rpm, max_gears, car_name
car_data = [
    # H1 FWD
    [7330.3826904296875, 837.7580261230469, 4.0, 'Mini Cooper S'],
    [6283.1854248046875, 1047.1975708007812, 4.0, 'Citroen DS 21'],
    [6806.78466796875, 994.8377227783203, 4.0, 'Lancia Fulvia HF'],

    # H2 FWD
    [7853.98193359375, 942.4777984619141, 5.0, 'Volkswagen Golf GTI 16V'],
    [7330.3826904296875, 1256.6371154785156, 5.0, 'Peugeot 205 GTI'],

    # H2 RWD
    [9948.377075195312, 1256.6371154785156, 5.0, 'Ford Escort Mk II'],
    [8377.58056640625, 1675.5160522460938, 5.0, 'Renault Alpine A110 1600 S'],
    [8377.58056640625, 1780.2359008789062, 5.0, 'Fiat 131 Abarth Rally'],
    [9424.77783203125, 1570.7963562011719, 5.0, 'Opel Kadett C GT/E'],

    # H3 RWD
    [9320.05859375, 1151.9173431396484, 6.0, 'BMW E30 Evo Rally'],
    [7853.98193359375, 1361.3568115234375, 5.0, 'Opel Ascona 400'],
    [8901.179809570312, 1047.1975708007812, 5.0, 'Lancia Stratos'],
    [8377.58056640625, 1518.4365844726562, 5.0, 'Renault 5 Turbo'],
    [7797.432861328125, 804.2477416992188, 5.0, 'Datsun 240Z'],
    [7853.98193359375, 1151.9173431396484, 5.0, 'Ford Sierra Cosworth RS500'],

    # F2 Kit Car
    [11519.173583984375, 1989.6754455566406, 6.0, 'Peugeot 306 Maxi'],
    [9424.77783203125, 1361.3568115234375, 6.0, 'Seat Ibiza Kit Car'],
    [9424.77783203125, 1256.6371154785156, 6.0, 'Volkswagen Golf Kitcar'],

    # Group B RWD
    [8901.179809570312, 1256.6371154785156, 5.0, 'Lancia 037 Evo 2'],
    [8168.1414794921875, 1466.07666015625, 5.0, 'Opel Manta 400'],
    [9686.577758789062, 1570.7963562011719, 5.0, 'BMW M1 Procar Rally'],
    [8377.58056640625, 1361.3568115234375, 5.0, 'Porsche 911 SC RS'],

    # Group B 4WD
    [9424.77783203125, 1361.3568115234375, 5.0, 'Audi Sport quattro S1 E2'],
    [8377.58056640625, 2094.3951416015625, 5.0, 'Peugeot 205 T16 Evo 2'],
    [8901.179809570312, 1675.5160522460938, 5.0, 'Lancia Delta S4'],  # same as Peugeot 208 R2
    [9424.77783203125, 1256.6371154785156, 5.0, 'Ford RS200'],
    [9948.377075195312, 1099.5574188232422, 5.0, 'MG Metro 6R4'],

    # R2
    [8168.1414794921875, 1570.7963562011719, 5.0, 'Ford Fiesta R2'],
    [9058.25927734375, 1780.2359008789062, 5.0, 'Opel Adam R2'],
    [8901.179809570312, 1675.5160522460938, 5.0, 'Peugeot 208 R2'],  # same as Lancia Delta S4

    # Group A
    [7330.3826904296875, 1466.07666015625, 6.0, 'Mitsubishi Lancer Evo VI'],  # same as BMW M2 Competition
    [7330.3826904296875, 1151.9173431396484, 6.0, 'Subaru Impreza 1995'],
    [7853.98193359375, 1047.1975708007812, 6.0, 'Lancia Delta HF Integrale'],
    [7330.3826904296875, 1466.07666015625, 7.0, 'Ford Escort RS Cosworth'],

    # NR4/R4
    [8377.58056640625, 1780.2359008789062, 5.0, 'Subaru Impreza WRX STI NR4'],
    [7853.98193359375, 1780.2359008789062, 5.0, 'Mitsubishi Lancer Evo X'],  # same as Peugeot 208 T16

    # 2000cc 4WD
    [7749.2620849609375, 1884.9555969238281, 6.0, 'Citroen C4 Rally'],
    [7749.2620849609375, 1780.2359008789062, 6.0, 'Skoda Fabia Rally'],  # same as Subaru WRX STI RX
    [7696.9024658203125, 1869.2477416992188, 5.0, 'Ford Focus RS Rally 2007'],
    [7853.98193359375, 2199.1148376464844, 6.0, 'Subaru Impreza 2008'],
    [785.398193359375, 178.02359008789062, 6.0, 'Ford Focus RS Rally 2001'],
    [8377.58056640625, 2042.035369873047, 6.0, 'Subaru Impreza 2001'],
    [6806.78466796875, 1570.796356201172, 5.0, 'Peugeot 206 Rally'],

    # R5
    [7749.2620849609375, 1884.9555969238281, 5.0, 'Ford Fiesta R5'],
    [7853.98193359375, 1780.2359008789062, 5.0, 'Peugeot 208 T16'],  # same as Mitsubishi Lancer Evolution X
    [8377.58056640625, 2199.1148376464844, 5.0, 'Mitsubishi Space Star R5'],
    [7749.2620849609375, 1780.2359008789062, 5.0, 'Skoda Fabia R5'],
    [7435.1031494140625, 1858.7757873535156, 5.0, 'Citroen C3 R5'],
    [7749.2620849609375, 1780.2359008789062, 5.0, 'Volkswagen Polo GTI R5'],

    # Rally GT
    [7330.3826904296875, 1466.07666015625, 6.0, 'BMW M2 Competition'],  # Mitsubishi Lancer Evo VI
    [7592.1820068359375, 1780.2359008789062, 6.0, 'Chevrolet Camaro GT4.R'],
    [9424.77783203125, 1884.9555969238281, 6.0, 'Porsche 911 RGT Rally Spec'],
    [7330.3826904296875, 1047.1975708007812, 6.0, 'Aston Martin V8 Vantage GT4'],
    [8639.380493164062, 1466.07666015625, 6.0, 'Ford Mustang GT4 Ford RS200'],

    # RX Super 1600S
    [9948.377075195312, 1884.9555969238281, 6.0, 'Volkswagen Polo S1600'],
    [9686.577758789062, 1989.6754455566406, 6.0, 'Renault Clio RS S1600'],
    [9948.377075195312, 1989.6754455566406, 6.0, 'Opel Corsa Super 1600'],

    # Crosskarts
    [15985.47119140625, 1612.6841735839844, 6.0, 'Speedcar Xtrem'],

    # RX Group B
    # [8901.179809570312, 1675.5160522460938, 5.0, 'Lancia Delta S4 RX'],  # same as Peugeot 208 R2, non-rx
    [9424.77783203125, 1675.5160522460938, 5.0, 'Ford RS200 Evolution'],
    # [8377.58056640625, 2094.3951416015625, 5.0, 'Peugeot 205 T16 Evo 2 RX'],  # same as non-rx
    [9948.377075195312, 1151.9173431396484, 5.0, 'MG Metro 6R4 RX'],

    # RX2
    [8377.58056640625, 1675.5160522460938, 6.0, 'Ford Fiesta OMSE SuperCar Lites'],

    # RX Supercars
    [8744.099731445312, 2094.3951416015625, 6.0, 'Volkswagen Polo R Supercar'],
    [8744.099731445312, 2094.3951416015625, 6.0, 'Audi S1 EKS RX quattro'],
    [8377.58056640625, 1780.2359008789062, 6.0, 'Peugeot 208 WRX'],
    [8168.1414794921875, 1727.8759765625, 5.0, 'Renault Megane RS'],
    [8115.78125, 1884.9555969238281, 6.0, 'Ford Fiesta RX (MK8)'],
    [7853.98193359375, 1727.8759765625, 6.0, 'Ford Fiesta RX (MK7)'],
    [7749.2620849609375, 1780.2359008789062, 6.0, 'Subaru WRX STI RX'],  # same as Skoda Fabia Rally

    # RX Supercars 2019
    [8377.58056640625, 1780.2359008789062, 5.0, 'Renault Megane R.S. RX'],  # same as Subaru Impreza WRX STI NR4
    [8377.58056640625, 1780.2359008789062, 6.0, 'Peugeot 208 WRX'],  # same as Peugeot 208 WRX
    [8744.099731445312, 2094.3951416015625, 6.0, 'Audi S1 EKS RX Quattro'],  # same as Audi S1 EKS RX quattro
    [8377.58056640625, 1780.2359008789062, 6.0, 'Renault Clio R.S. RX'],  # same as Peugeot 208 WRX
    [8377.58056640625, 1884.9555969238281, 6.0, 'Ford Fiesta RXS Evo 5'],  # same as Ford Fiesta RX (Stard)
    [8115.78125, 1884.9555969238281, 6.0, 'Ford Fiesta RX (MK8)'],  # same as Ford Fiesta RX (MK8)
    [7853.98193359375, 2617.9940795898438, 6.0, 'Mini Cooper SX1'],
    [8377.58056640625, 1884.9555969238281, 6.0, 'Ford Fiesta RX (Stard)'],  # same as Ford Fiesta RXS Evo 5
    [7853.98193359375, 1780.2359008789062, 6.0, 'Seat Ibiza RX'],
]


# adapted from https://github.com/soong-construction/dirt-rally-time-recorder/blob/master/tracks.sql
# length, start_z, track_name
track_data = [
    # Baumholder, Germany
    [5361.90966796875, -2668.4755859375, 'Waldaufstieg'],
    [5882.1796875, -948.372314453125, 'Waldabstieg'],
    [6121.8701171875, -718.9346923828125, 'Kreuzungsring'],
    [5666.25, 539.2579345703125, 'Kreuzungsring reverse'],
    [10699.9599609375, 814.2764892578125, 'Ruschberg'],
    [5855.6796875, 513.0728759765625, 'Verbundsring'],
    [5550.85009765625, 657.1261596679688, 'Verbundsring reverse'],
    [5129.0400390625, 814.3093872070312, 'Innerer Feld-Sprint'],
    [4937.85009765625, 656.46044921875, 'Innerer Feld-Sprint reverse'],
    [11487.189453125, -2668.59033203125, 'Oberstein'],
    [10805.23046875, 513.07177734375, 'Hammerstein'],
    [11551.16015625, 539.3564453125, 'Frauenberg'],

    # Monte Carlo, Monaco
    [10805.220703125, 1276.76611328125, 'Route de Turini'],
    [10866.8603515625, -2344.705810546875, 'Vallee descendante'],
    [4730.02001953125, 283.7648620605469, 'Col de Turini – Sprint en descente'],
    [4729.5400390625, -197.3816375732422, 'Col de Turini sprint en Montee'],
    [5175.91015625, -131.84573364257812, 'Col de Turini – Descente'],
    [5175.91015625, -467.3677062988281, 'Gordolon – Courte montee'],
    [4015.35986328125, -991.9784545898438, 'Route de Turini (Descente)'],
    [3952.150146484375, 1276.780517578125, 'Approche du Col de Turini – Montee'],
    [9831.4501953125, -467.483154296875, 'Pra d´Alart'],
    [9832.0205078125, 283.4727478027344, 'Col de Turini Depart'],
    [6843.3203125, -991.945068359375, 'Route de Turini (Montee)'],
    [6846.830078125, -2344.592529296875, 'Col de Turini – Depart en descente'],

    # Powys, Wales
    [4821.64990234375, 2047.56201171875, 'Pant Mawr Reverse'],
    [4960.06005859375, 1924.06884765625, 'Bidno Moorland'],
    [5165.96044921875, 2481.105224609375, 'Bidno Moorland Reverse'],
    [11435.5107421875, -557.0780029296875, 'River Severn Valley'],
    [11435.5400390625, 169.15403747558594, 'Bronfelen'],
    [5717.39990234375, -557.11328125, 'Fferm Wynt'],
    [5717.3896484375, -22.597640991210938, 'Fferm Wynt Reverse'],
    [5718.099609375, -23.46375274658203, 'Dyffryn Afon'],
    [5718.10009765625, 169.0966033935547, 'Dyffryn Afon Reverse'],
    [9911.66015625, 2220.982177734375, 'Sweet Lamb'],
    [10063.6005859375, 2481.169677734375, 'Geufron Forest'],
    [4788.669921875, 2221.004150390625, 'Pant Mawr'],

    # Värmland, Sweden
    [7055.9501953125, -1618.4476318359375, 'Älgsjön'],
    [4911.68017578125, -1742.0498046875, 'Östra Hinnsjön'],
    [6666.89013671875, -2143.403076171875, 'Stor-jangen Sprint'],
    [6693.43994140625, 563.3468017578125, 'Stor-jangen Sprint Reverse'],
    [4931.990234375, -5101.59619140625, 'Björklangen'],
    [11922.6201171875, -4328.87158203125, 'Ransbysäter'],
    [12123.740234375, 2697.36279296875, 'Hamra'],
    [12123.5908203125, -5101.78369140625, 'Lysvik'],
    [11503.490234375, 562.8009033203125, 'Norraskoga'],
    [5248.35986328125, -4328.87158203125, 'Älgsjön Sprint'],
    [7058.47998046875, 2696.98291015625, 'Elgsjön'],
    [4804.0302734375, -2143.44384765625, 'Skogsrallyt'],

    # New England, USA
    [6575.8701171875, -408.4866027832031, 'Tolt Valley Sprint Forward'],
    [6468.2998046875, 2768.171142578125, 'Unknown track'],
    [6701.61962890625, 1521.6917724609375, 'Hancock Creek Burst'],
    [6109.5400390625, -353.0966796875, 'Hancock Hill Sprint Reverse'],
    [12228.830078125, 1521.5872802734375, 'North Fork Pass'],
    [12276.1201171875, 27.728849411010742, 'North Fork Pass Reverse'],
    [6488.330078125, 27.087112426757812, 'Fuller Mountain Descent'],
    [6468.2998046875, 2768.10107421875, 'Fuller Mountain Ascent'],
    [6681.60986328125, 2950.6044921875, 'Fury Lake Depart'],
    [12856.66015625, 518.76123046875, 'Beaver Creek Trail Forward'],
    [12765.919921875, -4617.37744140625, 'Beaver Creek Trail Reverse'],
    [6229.10986328125, 518.7451171875, 'Hancock Hill Sprint Forward'],
    [6604.0302734375, -4617.388671875, 'Tolt Valley Sprint Reverse'],

    # Catamarca Province, Argentina
    [7667.31982421875, 131.03880310058594, 'Valle de los puentes'],
    [3494.010009765625, -1876.9149169921875, 'Huillaprima'],
    [8265.9501953125, 205.80775451660156, 'Camino a la Puerta'],
    [8256.8603515625, 2581.345947265625, 'Las Juntas'],
    [5303.7900390625, 2581.339599609375, 'Camino de acantilados y rocas'],
    [4171.5, -3227.17626953125, 'San Isidro'],
    [3353.0400390625, 130.6753692626953, 'Miraflores'],
    [2845.6298828125, 206.18272399902344, 'El Rodeo'],
    [7929.18994140625, -3227.17724609375, 'Valle de los puentes a la inversa'],
    [5294.81982421875, 1379.72607421875, 'Camino de acantilados y rocas inverso'],
    [4082.2998046875, -1864.662109375, 'Camino a Coneta'],
    [2779.489990234375, 1344.307373046875, 'La Merced'],

    # Hawkes Bay, New Zealand
    [4799.84033203125, -4415.70703125, 'Te Awanga Sprint Forward'],
    [11437.0703125, 1789.1517333984375, 'Ocean Beach'],
    [6624.0302734375, 1789.0382080078125, 'Ocean Beach Sprint'],
    [4688.52978515625, -2004.0015869140625, 'Te Awanga Sprint Reverse'],
    [8807.490234375, 2074.951171875, 'Waimarama Sprint Forward'],
    [6584.10009765625, -1950.1710205078125, 'Ocean Beach Sprint Reverse'],
    [7137.81005859375, 2892.6181640625, 'Elsthorpe Sprint Forward'],
    [15844.529296875, 2074.938720703125, 'Waimarama Point Reverse'],
    [16057.8505859375, 2892.97216796875, 'Waimarama Point Forward'],
    [11507.4404296875, -4415.119140625, 'Te Awanga Forward'],
    [8733.98046875, 5268.0849609375, 'Waimarama Sprint Reverse'],
    [15844.529296875, 2074.8916015625, 'Waimarama Point Reverse'],
    [6643.490234375, 5161.06396484375, 'Elsthorpe Sprint Reverse'],

    # Poland, Leczna County:
    [6622.080078125, 4644.4375, 'Czarny Las'],
    [9254.900390625, 1972.7869873046875, 'Marynka'],
    [6698.81005859375, -3314.843505859375, 'Lejno'],
    [8159.81982421875, 7583.216796875, 'Józefin'],
    [7840.1796875, 4674.87548828125, 'Kopina'],
    [6655.5400390625, -402.56207275390625, 'Jagodno'],
    [13180.3798828125, -3314.898193359375, 'Zienki'],
    [16475.009765625, 4674.9150390625, 'Zaróbka'],
    [16615.0, 1973.2518310546875, 'Zagorze'],
    [13295.6796875, 4644.3798828125, 'Jezioro Rotcze'],
    [9194.3203125, 7393.35107421875, 'Borysik'],
    [6437.80029296875, -396.1388854980469, 'Jezioro Lukie'],

    # Australia, Monaro:
    [13304.1201171875, 2242.524169921875, 'Mount Kaye Pass'],
    [13301.109375, -2352.5615234375, 'Mount Kaye Pass Reverse'],
    [6951.15966796875, 2242.5224609375, 'Rockton Plains'],
    [7116.14990234375, 2457.100341796875, 'Rockton Plains Reverse'],
    [6398.90966796875, 2519.408447265625, 'Yambulla Mountain Ascent'],
    [6221.490234375, -2352.546630859375, 'Yambulla Mountain Descent'],
    [12341.25, 2049.85888671875, 'Chandlers Creek'],
    [12305.0400390625, -1280.10595703125, 'Chandlers Creek Reverse'],
    [7052.2998046875, -603.9149169921875, 'Bondi Forest'],
    [7007.02001953125, -1280.1004638671875, 'Taylor Farm Sprint'],
    [5277.02978515625, 2049.85791015625, 'Noorinbee Ridge Ascent'],
    [5236.91015625, -565.1859130859375, 'Noorinbee Ridge Descent'],

    # Spain, Ribadelles:
    [14348.3603515625, 190.28546142578125, 'Comienzo en Bellriu'],
    [10568.4296875, -2326.21142578125, 'Centenera'],
    [7297.27001953125, 2593.36376953125, 'Ascenso bosque Montverd'],
    [6194.7099609375, -2979.6650390625, 'Vinedos Dardenya inversa'],
    [6547.39990234375, -2002.0657958984375, 'Vinedos Dardenya'],
    [6815.4501953125, -2404.635009765625, 'Vinedos dentro del valle Parra'],
    [10584.6796875, -2001.96337890625, 'Camina a Centenera'],
    [4380.740234375, -3003.546630859375, 'Subida por carretera'],
    [6143.5703125, 2607.470947265625, 'Salida desde Montverd'],
    [7005.68994140625, 190.13796997070312, 'Ascenso por valle el Gualet'],
    [4562.80029296875, -2326.251708984375, 'Descenso por carretera'],
    [6547.39990234375, -2002.19580078125, 'Vinedos Dardenya'],
    [13164.330078125, -2404.1171875, 'Final de Bellriu'],

    # Greece, Argolis
    [4860.1904296875, 91.54808044433594, 'Ampelonas Ormi'],
    [9666.5, -2033.0767822265625, 'Anodou Farmakas'],
    [9665.990234375, 457.1891784667969, 'Kathodo Leontiou'],
    [5086.830078125, -2033.0767822265625, 'Pomono Ékrixi'],
    [4582.009765625, 164.40521240234375, 'Koryfi Dafni'],
    [4515.39990234375, 457.18927001953125, 'Fourketa Kourva'],
    [10487.060546875, 504.3974609375, 'Perasma Platani'],
    [10357.8798828125, -3672.5810546875, 'Tsiristra Théa'],
    [5739.099609375, 504.3973693847656, 'Ourea Spevsi'],
    [5383.009765625, -2277.10986328125, 'Ypsona tou Dasos'],
    [6888.39990234375, -1584.236083984375, 'Abies Koiláda'],
    [6595.31005859375, -3672.58154296875, 'Pedines Epidaxi'],

    # Finland, Jämsä
    [7515.40966796875, 39.52613830566406, 'Kailajärvi'],
    [7461.65966796875, 881.0377197265625, 'Paskuri'],
    [7310.5400390625, 846.68701171875, 'Naarajärvi'],
    [7340.3798828125, -192.40794372558594, 'Jyrkysjärvi'],
    [16205.1904296875, 3751.42236328125, 'Kakaristo'],
    [16205.259765625, 833.2575073242188, 'Pitkäjärvi'],
    [8042.5205078125, 3751.42236328125, 'Iso Oksjärvi'],
    [8057.52978515625, -3270.775390625, 'Oksala'],
    [8147.560546875, -3263.315185546875, 'Kotajärvi'],
    [8147.419921875, 833.2575073242188, 'Järvenkylä'],
    [14929.7998046875, 39.52613067626953, 'Kontinjärvi'],
    [14866.08984375, -192.407958984375, 'Hämelahti'],

    # Rallycross locations:
    [1075.0989990234375, 149.30722045898438, 'Mettet, Belgium'],
    [1400.0770263671875, -230.09457397460938, 'Trois-Rivieres, Canada'],
    [1348.85400390625, 101.5931396484375, 'Lydden Hill, England'],
    [991.1160278320312, -185.40646362304688, 'Silverstone, England'],
    [1064.97998046875, 195.76113891601562, 'Loheac, France'],
    [951.51171875, -17.769332885742188, 'Estering, Germany'],
    [1287.4329833984375, 134.0433807373047, 'Bikernieki, Latvia'],
    [1036.0970458984375, 122.2354736328125, 'Hell, Norway'],
    [1026.759033203125, -541.3275756835938, 'Montalegre, Portugal'],
    [1064.623046875, -100.92737579345703, 'Killarney, South Africa'],
    [1119.3590087890625, -341.3289794921875, 'Barcalona-Catalunya, Spain'],
    [1207.18798828125, 180.26181030273438, 'Holjes, Sweden'],
    [1194.22900390625, -133.4615936279297, 'Yas Marina, Abu Dhabi'],
]


car_dict = dict()
for d in car_data:
    car_dict[(d[0], d[1], d[2])] = d[3]

# track length is not a unique key as some tracks are just reversed
# it's unique together with the starting position, which is not accurate to float precision
track_dict = defaultdict(list)
for t in track_data:
    track_dict[t[0]].append((t[1], t[2]))


class GameState(Enum):
    #error = 0
    race_start = 1
    race_running = 2
    duplicate_package = 3
    race_finished_or_service_area = 4


def get_car_name_from_sample(start_sample):
    max_rpm = start_sample[networking.Fields.max_rpm.value]
    idle_rpm = start_sample[networking.Fields.idle_rpm.value]
    max_gears = start_sample[networking.Fields.max_gears.value]
    return get_car_name(max_rpm, idle_rpm, max_gears)


def get_car_name(max_rpm, idle_rpm, max_gears):
    key = (max_rpm, idle_rpm, max_gears)
    if key in car_dict.keys():
        car_name = car_dict[key]
    else:
        car_name = 'Unknown car ' + str(key)
    return car_name


def get_track_name_from_sample(start_sample):
    length = start_sample[networking.Fields.track_length.value]
    start_z = start_sample[networking.Fields.pos_z.value]
    return get_track_name(length, start_z)


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


def get_game_state_str(state, start_sample, num_samples):

    #if state == GameState.error:
    #    return None

    state_str = '{car} on {track}, samples: {samples:05d}, lap time: {time:.1f}, ' \
                'speed: {speed:.1f} m/s, rpm {rpm:5.1f}, {state}'

    time = start_sample[networking.Fields.lap_time.value]
    speed = start_sample[networking.Fields.speed_ms.value]
    rpm = start_sample[networking.Fields.rpm.value]

    car_name = get_car_name_from_sample(start_sample)
    track_name = get_track_name_from_sample(start_sample)

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

    #if receive_results is None:  # no data, error in receive?
    #    return GameState.error

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

    # RPM will never be zero at the start (it will be the idle RPM)
    # However, RPM can be zero for some reason in the service area. Ignore then.
    if receive_results[networking.Fields.rpm.value] == 0.0 and receive_results[networking.Fields.run_time.value] <= 0.1:
        return GameState.duplicate_package

    return GameState.race_running


def accept_new_data(state):
    #if state == GameState.error:
    #    return False
    if state == GameState.race_start:
        return False
    elif state == GameState.race_running:
        return True
    elif state == GameState.race_finished_or_service_area:
        return False
    elif state == GameState.duplicate_package:
        return False
    else:
        raise ValueError('Unknown state: {}'.format(state))

