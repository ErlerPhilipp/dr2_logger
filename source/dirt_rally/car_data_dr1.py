# adapted from https://github.com/soong-construction/dirt-rally-time-recorder/blob/master/resources/setup-dr1.sql
# max_rpm, idle_rpm, car_name
car_data = [
    # RX
    [733.038330078125,  146.60714721679688, 4.0, 'Mini Classic Rallycross'],
    [968.6577758789062, 198.96754455566406, 6.0, 'Opel Corsa Super 1600'],
    [968.6577758789062, 198.96754455566406, 6.0, 'Renault Clio S1600'],
    [968.6577758789062, 198.96754455566406, 6.0, 'Peugeot 207 S1600'],
    [911.0618896484375, 141.37167358398438, 6.0, 'DS Automobiles DS3'],
    [785.398193359375,  172.78750610351562, 6.0, 'Ford Fiesta Rallycross'],
    [785.398193359375,  261.79940795898438, 6.0, 'Volkswagen Polo Rallycross'],
    [837.758056640625,  188.49555969238281, 6.0, 'Peugeot 208 WRX'],
    [837.758056640625,  188.49555969238281, 6.0, 'Mini Countryman Rallycross'],
    [785.398193359375,  209.43939208984375, 6.0, 'Subaru WRX STI'],

    # 1960s
    [733.038,          104.72,             4.0, 'Mini Cooper S'],
    [783.304,          98.4366,            4.0, 'Lancia Fulvia HF'],
    [785.398193359375, 167.55160522460938, 5.0, 'Renault Alpine A110'],

    # 1970s
    [869.174,          125.664,            5.0, 'Opel Kadett GT/E 16v'],
    [884.882,          150.796,            5.0, 'Fiat 131 Abarth'],
    [942.478,          104.72,             5.0, 'Ford Escort Mk II'],
    [837.758056640625, 167.55160522460938, 5.0, 'Lancia Stratos'],

    # 1980s
    [942.478,           125.664,            5.0, 'BMW E30 Evo Rally'],
    [785.398193359375,  172.7875213623047,  5.0, 'Ford Sierra Cosworth RS500'],
    [806.3421630859375, 130.89968872070312, 5.0, 'Renault 5 Turbo'],

    # Group B 4WD)
    [1099.56, 157.08,  5.0, 'MG Metro 6R4'],
    [733.038, 115.192, 5.0, 'Audi Sport Quattro Rallye'],
    [890.118, 125.664, 5.0, 'Ford RS200'],
    [837.758, 209.439, 5.0, 'Peugeot 205 T16 Evo 2 '],
    [890.118, 104.72,  5.0, 'Lancia Delta S4'],

    # Group A
    [785.398193359375, 183.25953674316406, 5.0, 'Lancia Delta HF Integrale'],
    [785.398193359375, 204.2035369873047,  6.0, 'Subaru Impreza 1995'],
    [785.398193359375, 178.0236053466797,  7.0, 'Ford Escort RS Cosworth'],

    # F2 Kit Car
    [942.478, 136.136, 6.0, 'Seat Ibiza Kitcar'],
    [1151.92, 146.607, 6.0, 'Peugeot 306 Maxi'],

    # R4
    [774.9262084960938, 167.55160522460938, 6.0, 'Subaru Impreza WRX STI 2011'],
    [785.398193359375,  178.0236053466797,  5.0, 'Mitsubishi Lancer Evolution X'],

    # 2000s
    [785.398193359375, 157.07962036132812, 6.0, 'Subaru Impreza 2001'],
    [785.398193359375, 178.0236053466797,  6.0, 'Ford Focus RS Rally 2001'],
    [733.038330078125, 209.43943786621094, 6.0, 'Ford Focus RS Rally 2007'],
    [733.038330078125, 209.43943786621094, 6.0, 'Citroen C4 Rally 2007'],

    # 2010s
    [785.398193359375, 167.55160522460938, 6.0, 'Mini Countryman Rally Edition'],
    [785.398,          146.607,            6.0, 'Ford Fiesta 2010'],
    [733.038330078125, 209.43943786621094, 6.0, 'Hyundai Rally'],
    [733.038,          198.968,            6.0, 'Volkswagen Polo Rally'],

    # Group B RWD)
    [837.758, 146.607, 5.0, 'Opel Manta 400'],
    [890.118, 125.664, 5.0, 'Lancia 037 Evo 2'],

    # Hillclimb
    [837.758,         209.439,            5.0, 'Peugeot 205 T16 Pikes Peak'],
    [837.758,         157.08,             6.0, 'Peugeot 405 T16 Pikes Peak'],
    [863.938,         141.372,            6.0, 'Audi Sport Quattro S1 PP'],
    [816.81396484375, 188.49559020996094, 6.0, 'Peugeot 208 T16 Pikes Peak'],
]


car_dict = dict()
for d in car_data:
    car_dict[(d[0], d[1], d[2])] = d[3]
