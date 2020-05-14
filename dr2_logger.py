import os
import sys
import threading
import queue

from source.logger_backend import LoggerBackend


log_raw_data = False
debugging = False
version_string = '(Version 1.8.1, 2020-05-15)'
# TODO: update date

intro_text = '''
Dirt Rally 2.0 Logger {} by Philipp Erler
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
"e" or "exit" to exit the program
"c" or "clear" to clear the current run
"p" or "plot" to show the important plots
"pa" or "plot_all" to show all plots
"s" or "save" to save the current run
"l" or "load" to load a saved run
"g game_name" to switch the target game, values for game_name: {}
'''.format(LoggerBackend.get_all_valid_games())


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
                # for Linux terminals:
                # while both Gnome Terminal and KDE's Konsole report TERM=xterm-256color,
                # Konsole needs different control chars
                # to change the terminal title
                if 'KONSOLE_VERSION' in os.environ:
                    # https://stackoverflow.com/questions/19897787/change-konsole-tab-title-from-command-line-and-make-it-persistent
                    # TODO this works only once per stage where it's updated at the very beginning
                    sys.stdout.write('\033]30;{}\007'.format(state_str))
                else:
                    # https://stackoverflow.com/questions/25872409/set-gnome-terminal-window-title-in-python/47262154#47262154
                    sys.stdout.write('\33]0;{}\a'.format(state_str))
                sys.stdout.flush()
        finally:
            pass


def main():

    end_program = False

    print(intro_text)
    print(commands_hint)

    logger_backend = LoggerBackend(debugging=debugging, log_raw_data=log_raw_data)
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

            if command == 'e' or command == 'exit':
                print('Exit...\n')
                end_program = True
            elif command == 'c' or command == 'clear':
                print('Cleared {} data points\n'.format(logger_backend.get_num_samples()))
                logger_backend.clear_session_collection()
            elif command == 'p' or command == 'plot':
                if logger_backend.get_num_samples() == 0:
                    print('No data points to plot\n')
                else:
                    print('Plotting {} data points\n'.format(logger_backend.get_num_samples()))
                    logger_backend.show_plots(False)
            elif command == 'pa' or command == 'plot_all':
                if logger_backend.get_num_samples() == 0:
                    print('No data points to plot\n')
                else:
                    print('Plotting {} data points\n'.format(logger_backend.get_num_samples()))
                    logger_backend.show_plots(True)
            elif command == 's' or command == 'save':
                logger_backend.save_run()
            elif command.startswith('g'):
                new_game_name = command.split(' ')[1]
                logger_backend.change_game(new_game_name)
                print('Switched game to "{}"'.format(logger_backend.game_name))
            elif command == 'l' or command == 'load':
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
