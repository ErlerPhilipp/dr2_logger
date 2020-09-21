# Setup #

## Enable UDP data for Dirt Rally 1 and 2 ##
1. Open the hardware_settings_config.xml:
    1. Windows (DR 1): "C:\Users\[USERNAME]\Documents\My Games\DiRT Rally\hardwaresettings\hardware_settings_config.xml"
    1. Windows (DR 2): "C:\Users\[USERNAME]\Documents\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config.xml"
    1. Linux (DR 1): "~/.local/share/feral-interactive/DiRT Rally/VFS/User/AppData/Roaming/My Games/DiRT Rally/hardwaresettings/hardware_settings_config.xml"
    1. Linux (DR 2 via Proton): "~/.local/share/Steam/steamapps/compatdata/690790/pfx/drive_c/users/steamuser/My Documents/My Games/DiRT Rally 2.0/hardwaresettings/hardware_settings_config.xml"
1. Set udp enabled="true".
1. Set extra_data=3 to get all information.
1. Set ip="127.0.0.1" (localhost) to keep the data on the machine running Dirt Rally.
1. Set port=20777 or change the port in the logger.
1. Set delay="1" so that Dirt Rally sends the current car state at 100 FPS (maximum temporal resolution).
1. You can add the 'custom_udp' line multiple times for multiple telemetry tools.

Example:
```xml
<motion_platform>
    <dbox enabled="false" />
    <udp enabled="True" extradata="3" ip="127.0.0.1" port="20777" delay="1" />
    <custom_udp enabled="false" filename="packet_data.xml" ip="127.0.0.1" port="20777" delay="1" />
    <custom_udp enabled="false" filename="packet_data.xml" ip="127.0.0.1" port="10001" delay="1" />
    <fanatec enabled="false" pedalVibrationScale="1.0" wheelVibrationScale="1.0" ledTrueForGearsFalseForSpeed="true" />
</motion_platform>
```


## Run the Logger ##

1. Download and unzip the drlogger.zip archive.
1. Run the drlogger.exe while you play Dirt Rally.
1. The logger is set to Dirt Rally 2.0 mode by default. To switch to Dirt Rally 1 enter 'g Dirt_Rally_1' when the logger runs.
1. After each race, the logger will automatically save the current data.
1. At the start of a race, the logger will delete the old data.
1. Switch (Alt+Tab) from Dirt Rally to the logger to create the plots.
1. Remarks:
    1. You can edit the settings.ini to change the path for automatic session saves, the ip and port.
    1. Don't save, load or analyze your run while the race is running. Otherwise, data might get lost. Pausing the race is ok.
    1. This tool will probably work with other racing games by Codemaster, for example Dirt 4 and F1. Those games use the same datastructure for the UDP packages. However, I didn't test it. Other racing games with UDP output, such as Project Cars, will require some changes.
    1. When you get an error about listening to the port, make sure that no other application is using this port.