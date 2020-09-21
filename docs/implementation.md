# Implementation Details #

This document explains how to run the Python code, how to build an executable and which information is available.


## Run and Build ##

To run the logger as a Windows executable, simply download the latest release, unzip and double click the .cmd file.

To run the logger as a Python script, run these commands:
~~~~
# install [Anaconda with Python 3](https://anaconda.org/)
# open your repos directory in a terminal

# clone repo ./dr2_logger
git clone https://github.com/ErlerPhilipp/dr2_logger.git

# go into the cloned logger dir
cd dr2_logger

# create a conda environment with the required packages
conda env create --file dr2_logger.yml

# activate the new conda environment
conda activate dr2_logger

# run the logger with Python
python dr2_logger.py
~~~~

To build an executable, run \
`pyinstaller dr2_logger.py`


## Raw Data ##

I can only use the information I get from Dirt Rally 1 and 2 via UDP. This is currently:

1. Run time (starts after loading screen)
1. Lap time (starts after countdown)
1. Distance (driven distance)
1. Progress (0.0..1.0)
1. Car position (3D vector in world space)
1. Forward speed (m/s as shown in HUD)
1. Car velocity (3D vector in world space)
1. Roll (3D vector in world space)
1. Pitch (3D vector in world space)
1. Suspension dislocation per wheel (mm)
1. Suspension dislocation change per wheel (mm/s)
1. Wheel speed per wheel (m/s)
1. Throttle (0.0..1.0)
1. Steering (-1.0..+1.0)
1. Brakes (0.0..1.0)
1. Clutch (0.0..1.0)
1. Gear (-1,0,1..n)
1. G-force (lat-lon)
1. Current lap
1. RPM of engine
1. Brake temperature
1. Laps
1. Track length
1. Max / idle RPM
1. Max gears

See [networking.py](source/networking.py) for more information.


## Open Issues and Contributing ##

Please, feel free to open issues and send pull requests when you have ideas for improvements.

On the long run, comparing two or more recordings would be great. However, this is not easy because most plots would need a common registration. Using the run time won't work and using the progress would make time-dependent data hard to understand.

You may see 'unknown car' or 'unknown track' in your logs. This happens when the internal database is outdated. In this case, please fill in the car names in the 'unknown cars.txt' and 'unknown tracks.txt' that you should find in the logger's directory. Then send the contents of those files to me.
Due to ambiguous data (exactly the same idle/max RPM and number of gears), the following cars in DR2 cannot be distinguished:
- Lancia Delta S4 RX, non-RX and Peugeot 208 R2
- Peugeot 205 T16 RX and non-RX
- Audi S1 EKS RX Quattro Supercars (2019) and Volkswagen Polo R Supercar
- Peugeot 208 WRX Supercars (2019) and Renault Clio R.S. RX
- Renault Megane R.S. RX (2019) and Subaru Impreza WRX STI NR4 and Fiat 131 Abarth Rally 
- Ford Fiesta RXS Evo 5 and Ford Fiesta RX (Stard)
- Ford Focus RS Rally 2001 and Seat Ibiza RX
- Mitsubishi Lancer Evo VI and BMW M2 Competition
- Mitsubishi Lancer Evo X and Peugeot 208 T16
- Skoda Fabia Rally and Subaru WRX STI RX
- Skoda Fabia R5 and Volkswagen Polo GTI R5

