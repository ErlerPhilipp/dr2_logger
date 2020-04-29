import os
import configparser


settings = configparser.ConfigParser()


def init_settings():
    init_settings_input_socket()
    init_settings_output_socket()
    init_settings_session_path()
    init_settings_game('Dirt_Rally_2')


def init_settings_input_socket():
    settings['general']['ip_in'] = '127.0.0.1'
    settings['general']['port_in'] = '20777'


def init_settings_output_socket():
    # mirror the received datagrams to this port in order to enable other telemetry tools
    settings['general']['ip_out'] = '127.0.0.1'
    settings['general']['port_out'] = '10001'
    settings['general']['forward_udp'] = '0'


def init_settings_session_path():
    settings['general']['session_path'] = './races_auto_save/'


def init_settings_game(init_val):
    settings['general']['game'] = init_val


def write_settings():
    with open('settings.ini', 'w') as settings_file:
        settings.write(settings_file)


def read_settings():
    settings_file_path = 'settings.ini'
    if os.path.isfile(settings_file_path):
        settings.read(settings_file_path)
    else:
        settings['general'] = {}
        init_settings()
        write_settings()


read_settings()

