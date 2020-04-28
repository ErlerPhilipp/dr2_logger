import os
import sys
import threading
import queue

from source.logger_backend import LoggerBackend


log_raw_data = False
version_string = '(Version 1.7, 2020-03-25)'

intro_text = '''
Dirt Rally 2.0 Race Logger {} by Philipp Erler
https://github.com/ErlerPhilipp/dr2_logger

Make sure, UDP data is enabled in the hardware_settings_config.xml 
Default: C:\\Users\\ [username] \\Documents\\My Games\\DiRT Rally 2.0\\hardwaresettings\\hardware_settings_config.xml
<motion_platform>
    <dbox enabled="false" />
    <udp enabled="true" extradata="3" ip="127.0.0.1" port="20777" delay="1" />
    <udp enabled="true" extradata="3" ip="127.0.0.1" port="10001" delay="1" />
    <custom_udp enabled="False" filename="packet_data.xml" ip="127.0.0.1" port="20777" delay="1" />
    <fanatec enabled="false" pedalVibrationScale="1.0" wheelVibrationScale="1.0" ledTrueForGearsFalseForSpeed="true" />
</motion_platform>
'''.format(version_string)

commands_hint = '''
Enter:
"e" to exit the program
"c" to clear the current run
"a" for analysis
"s" to save the current run
"l" to load a saved run
'''


def add_input(message_queue):
    running = True
    while running:
        read_res = input()
        message_queue.put(read_res)
        if read_res == 'e':
            running = False


def print_current_state(state_str):
    if state_str is not None:
        try:
            if os.name == 'nt':
                import ctypes
                ctypes.windll.kernel32.SetConsoleTitleW(state_str)
            else:
                # for Linux (Gnome) terminals:
                # https://stackoverflow.com/questions/25872409/set-gnome-terminal-window-title-in-python/47262154#47262154
                sys.stdout.write('\33]0;{}\a'.format(state_str))
                sys.stdout.flush()
        finally:
            pass


def main():

    end_program = False

    print(intro_text)
    print(commands_hint)

    logger_backend = LoggerBackend(game_name='Dirt Rally 2', debugging=False, log_raw_data=False)
    logger_backend.start_logging()

    message_queue = queue.Queue()
    input_thread = threading.Thread(target=add_input, args=(message_queue,))
    input_thread.daemon = True
    input_thread.start()

    while not end_program:

        logger_backend.check_udp_messages()
        print_current_state(logger_backend.get_game_state_str())

        while not message_queue.empty():
            command = message_queue.get()

            if command == 'e':
                print('Exit...\n')
                end_program = True
            elif command == 'c':
                print('Cleared {} data points\n'.format(logger_backend.get_num_samples()))
                logger_backend.clear_session_collection()
            elif command == 'a':
                print('Plotting {} data points\n'.format(logger_backend.get_num_samples()))
                logger_backend.show_plots()
            elif command == 's':
                logger_backend.save_run()
            elif command == 'l':
                logger_backend.load_run()
                print_current_state(logger_backend.get_game_state_str())
            elif command == '':
                pass  # just ignore empty inputs
            else:
                print('Unknown command: "{}"'.format(command))
                print(commands_hint + '\n')

        message = logger_backend.check_state_changes()
        if len(message) > 0:
            print(message)

    input_thread.join()
    logger_backend.end_logging()


if __name__ == "__main__":
    main()
