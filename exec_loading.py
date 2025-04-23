import keyboard
from time import sleep
from time import time
import config
import colors
import json
import sys
import os

# Enable ANSI colors
if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

BASE_DIR = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(BASE_DIR, 'config.json'), 'r') as f:
        config = json.load(f)
except Exception as e:
    print(f"[ERROR] Failed to load config.json: {e}")
    sys.exit(1)
    
EXIT_KEY = config['EXIT_KEY']
EXEC_KEY = config['EXEC_KEY']
SHOW_COMMANDS_KEY = config['SHOW_COMMANDS_KEY']
EC_SLEEP_TIME = config['EC_SLEEP_TIME']

INSTRUCTION_MESSAGE = ''
INSTRUCTION_MESSAGE_LIST = [f'{colors.BOLD}PRESS{colors.RESET}:',
                            f'\n{colors.BRIGHT_CYAN}{SHOW_COMMANDS_KEY}{colors.RESET} to show all exec commands',
                            f'\n{colors.BRIGHT_YELLOW}{EXEC_KEY}{colors.RESET} to load training exec {colors.RED}[ONLY WHILE IN-GAME]{colors.RESET}',
                            f'\n{EXIT_KEY} to exit']
for i in INSTRUCTION_MESSAGE_LIST: INSTRUCTION_MESSAGE+=i

def execute_exec():
    exec_commands_list = ''
    try:
        with open('exec.txt', 'r') as f:
            exec_commands_list = "; ".join([line.strip() for line in f])
    except FileNotFoundError:
        print("[ERROR] exec.txt not found.")
        return
    keyboard.press('`')
    keyboard.release('`')
    sleep(EC_SLEEP_TIME)
    keyboard.write(exec_commands_list)
    sleep(EC_SLEEP_TIME)
    keyboard.press('enter')
    keyboard.release('enter')
    sleep(EC_SLEEP_TIME)
    keyboard.press('`')
    keyboard.release('`')

def show_exec_commands():
    exec_commands_list = []
    with open('exec.txt', 'r') as f:
        for line in f:
            exec_commands_list.append(line.strip())
    print(f'{colors.BG_BRIGHT_WHITE}{colors.BLACK}ALL COMMANDS:{colors.RESET}')
    for command in exec_commands_list:
        print(f'- {command}')

def pressed_key_logic():
    last_action_time = {'exec': 0, 'show_exec': 0} #optimalization, less lags
    debounce_delay = 0.2
    commands_shown = False
    while True:
        current_time = time()
        # --- exec loading --- #
        if keyboard.is_pressed(EXEC_KEY) and (current_time - last_action_time['exec'] > debounce_delay):
            try:
                execute_exec()
                print(f'{colors.BRIGHT_YELLOW}exec loaded successfully!{colors.RESET}')
            except Exception as e:
                print(f'Error: {e}')
            while keyboard.is_pressed(EXEC_KEY):
                pass
        
        if keyboard.is_pressed(SHOW_COMMANDS_KEY) and (current_time - last_action_time['show_exec'] > debounce_delay):
            if not commands_shown:
                show_exec_commands()
                commands_shown = True
            else:
                print('^^^ commands shown upper ^^^')
            while keyboard.is_pressed(SHOW_COMMANDS_KEY):
                pass
        # --- exit --- #
        elif keyboard.is_pressed(EXIT_KEY):
            break
        sleep(0.05)

def main():
    print(INSTRUCTION_MESSAGE)
    pressed_key_logic()

main()