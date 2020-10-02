# see also: https://github.com/soong-construction/dirt-rally-time-recorder/blob/master/resources/setup-dr2.sql
# max_rpm, idle_rpm, max_gears, car_name
car_data = [
    # Crosskarts
    [1598.547119140625, 161.26841735839844, 6.0, 'Speedcar Xtrem'],

    # RX Super 1600S
    [994.8377075195312, 188.49555969238281, 6.0, 'Volkswagen Polo S1600'],
    [968.6577758789062, 198.96754455566406, 6.0, 'Renault Clio RS S1600'],
    [994.8377075195312, 198.96754455566406, 6.0, 'Opel Corsa Super 1600'],

    # RX Group B
    [890.1179809570312, 167.55160522460938, 5.0, 'Lancia Delta S4 RX'],  # same as Peugeot 208 R2 and Lancia Delta S4
    [942.477783203125, 167.55160522460938, 5.0, 'Ford RS200 Evolution'],
    [837.758056640625, 209.43951416015625, 5.0, 'Peugeot 205 T16 Evo 2 RX'],  # same as non-rx
    [994.8377075195312, 115.19173431396484, 5.0, 'MG Metro 6R4 RX'],

    # RX2
    [837.758056640625, 167.55160522460938, 6.0, 'Ford Fiesta OMSE SuperCar Lites'],

    # RX Supercars
    [874.4099731445312, 209.43951416015625, 6.0, 'Volkswagen Polo R Supercar'],  # same as Audi S1 EKS RX quattro
    [874.4099731445312, 209.43951416015625, 6.0, 'Audi S1 EKS RX Quattro'],  # same as Volkswagen Polo R Supercar
    [837.758056640625, 178.02359008789062, 6.0, 'Peugeot 208 WRX'],  # same as Renault Clio R.S. RX
    [816.81414794921875, 172.78759765625, 5.0, 'Renault Megane RS'],
    [811.578125, 188.49555969238281, 6.0, 'Ford Fiesta RX (MK8)'],
    [785.398193359375, 172.78759765625, 6.0, 'Ford Fiesta RX (MK7)'],
    [774.92620849609375, 178.02359008789062, 6.0, 'Subaru WRX STI RX'],  # same as Skoda Fabia Rally

    # RX Supercars 2019
    [837.758056640625, 178.02359008789062, 5.0, 'Renault Megane R.S. RX'],  # same as Subaru Impreza WRX STI NR4
    [837.758056640625, 178.02359008789062, 6.0, 'Peugeot 208 WRX'],  # same as Renault Clio R.S. RX
    [874.4099731445312, 209.43951416015625, 6.0, 'Audi S1 EKS RX Quattro'],  # same as Volkswagen Polo R Supercar
    [837.758056640625, 178.02359008789062, 6.0, 'Renault Clio R.S. RX'],  # same as Peugeot 208 WRX
    [837.758056640625, 188.49555969238281, 6.0, 'Ford Fiesta RXS Evo 5'],  # same as Ford Fiesta RX (Stard)
    [811.578125, 188.49555969238281, 6.0, 'Ford Fiesta RX (MK8)'],  # same as Ford Fiesta RX (MK8)
    [785.398193359375, 261.79940795898438, 6.0, 'Mini Cooper SX1'],
    [837.758056640625, 188.49555969238281, 6.0, 'Ford Fiesta RX (Stard)'],  # same as Ford Fiesta RXS Evo 5
    [785.398193359375, 178.02359008789062, 6.0, 'Seat Ibiza RX'],  # same as Ford Focus RS Rally 2001

    # H1 FWD
    [733.03826904296875, 83.77580261230469, 4.0, 'Mini Cooper S'],
    [628.31854248046875, 104.71975708007812, 4.0, 'Citroen DS 21'],
    [680.678466796875, 99.48377227783203, 4.0, 'Lancia Fulvia HF'],

    # H2 FWD
    [785.398193359375, 94.24777984619141, 5.0, 'Volkswagen Golf GTI 16V'],
    [733.03826904296875, 125.66371154785156, 5.0, 'Peugeot 205 GTI'],

    # H2 RWD
    [994.8377075195312, 125.66371154785156, 5.0, 'Ford Escort Mk II'],
    [837.758056640625, 167.55160522460938, 5.0, 'Renault Alpine A110 1600 S'],
    [837.758056640625, 178.02359008789062, 5.0, 'Fiat 131 Abarth Rally'],  # same as Renault Megane R.S. RX
    [942.477783203125, 157.07963562011719, 5.0, 'Opel Kadett C GT/E'],

    # H3 RWD
    [932.005859375, 115.19173431396484, 6.0, 'BMW E30 Evo Rally'],
    [785.398193359375, 136.13568115234375, 5.0, 'Opel Ascona 400'],
    [890.1179809570312, 104.71975708007812, 5.0, 'Lancia Stratos'],
    [837.758056640625, 151.84365844726562, 5.0, 'Renault 5 Turbo'],
    [779.7432861328125, 80.42477416992188, 5.0, 'Datsun 240Z'],
    [785.398193359375, 115.19173431396484, 5.0, 'Ford Sierra Cosworth RS500'],

    # F2 Kit Car
    [1151.9173583984375, 198.96754455566406, 6.0, 'Peugeot 306 Maxi'],
    [942.477783203125, 136.13568115234375, 6.0, 'Seat Ibiza Kit Car'],
    [942.477783203125, 125.66371154785156, 6.0, 'Volkswagen Golf Kitcar'],

    # Group B RWD
    [890.1179809570312, 125.66371154785156, 5.0, 'Lancia 037 Evo 2'],
    [816.81414794921875, 146.607666015625, 5.0, 'Opel Manta 400'],
    [968.6577758789062, 157.07963562011719, 5.0, 'BMW M1 Procar Rally'],
    [837.758056640625, 136.13568115234375, 5.0, 'Porsche 911 SC RS'],

    # Group B 4WD
    [942.477783203125, 136.13568115234375, 5.0, 'Audi Sport quattro S1 E2'],
    [837.758056640625, 209.43951416015625, 5.0, 'Peugeot 205 T16 Evo 2'],
    [890.1179809570312, 167.55160522460938, 5.0, 'Lancia Delta S4'],  # same as Peugeot 208 R2
    [942.477783203125, 125.66371154785156, 5.0, 'Ford RS200'],
    [994.8377075195312, 109.95574188232422, 5.0, 'MG Metro 6R4'],

    # R2
    [816.81414794921875, 157.07963562011719, 5.0, 'Ford Fiesta R2'],
    [905.825927734375, 178.02359008789062, 5.0, 'Opel Adam R2'],
    [890.1179809570312, 167.55160522460938, 5.0, 'Peugeot 208 R2'],  # same as Lancia Delta S4

    # Group A
    [733.03826904296875, 146.607666015625, 6.0, 'Mitsubishi Lancer Evo VI'],  # same as BMW M2 Competition
    [733.03826904296875, 115.19173431396484, 6.0, 'Subaru Impreza 1995'],
    [785.398193359375, 104.71975708007812, 6.0, 'Lancia Delta HF Integrale'],
    [733.03826904296875, 146.607666015625, 7.0, 'Ford Escort RS Cosworth'],
    [791.1577758789062, 202.4232940673828, 6.0, 'Subaru Legacy RS'],

    # NR4/R4
    [837.758056640625, 178.02359008789062, 5.0, 'Subaru Impreza WRX STI NR4'],
    [785.398193359375, 178.02359008789062, 5.0, 'Mitsubishi Lancer Evo X'],  # same as Peugeot 208 T16

    # 2000cc 4WD
    [774.92620849609375, 188.49555969238281, 6.0, 'Citroen C4 Rally'],
    [774.92620849609375, 178.02359008789062, 6.0, 'Skoda Fabia Rally'],  # same as Subaru WRX STI RX
    [769.69024658203125, 186.92477416992188, 5.0, 'Ford Focus RS Rally 2007'],
    [785.398193359375, 219.91148376464844, 6.0, 'Subaru Impreza 2008'],
    [785.398193359375, 178.02359008789062, 6.0, 'Ford Focus RS Rally 2001'],  # same as Seat Ibiza RX
    [837.758056640625, 204.2035369873047, 6.0, 'Subaru Impreza 2001'],
    [680.678466796875, 157.0796356201172, 5.0, 'Peugeot 206 Rally'],
    [816.8141479492188, 207.34512329101562, 6.0, 'Subaru Impreza S4 Rally'],

    # R5
    [774.92620849609375, 188.49555969238281, 5.0, 'Ford Fiesta R5'],
    [785.398193359375, 178.02359008789062, 5.0, 'Peugeot 208 T16'],  # same as Mitsubishi Lancer Evolution X
    [837.758056640625, 219.91148376464844, 5.0, 'Mitsubishi Space Star R5'],
    [774.92620849609375, 178.02359008789062, 5.0, 'Skoda Fabia R5'],  # same as Volkswagen Polo GTI R5
    [774.92620849609375, 178.02359008789062, 5.0, 'Volkswagen Polo GTI R5'],  # same as Skoda Fabia R5
    [743.51031494140625, 185.87757873535156, 5.0, 'Citroen C3 R5'],
    [774.9262084960938, 183.2595672607422, 5.0, 'Ford Fiesta R5 MKII'],

    # Rally GT
    [942.477783203125, 188.4955596923828, 6.0, 'Porsche 911 RGT Rally Spec'],
    [733.03826904296875, 146.607666015625, 6.0, 'BMW M2 Competition'],  # Mitsubishi Lancer Evo VI
    [759.21820068359375, 178.02359008789062, 6.0, 'Chevrolet Camaro GT4.R'],
    [733.03826904296875, 104.71975708007812, 6.0, 'Aston Martin V8 Vantage GT4'],
    [863.9380493164062, 146.607666015625, 6.0, 'Ford Mustang GT4 Ford RS200'],
]

car_dict = dict()
for d in car_data:
    car_dict[(d[0], d[1], d[2])] = d[3]
