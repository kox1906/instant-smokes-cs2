import keyboard
from time import sleep
import random
import pyperclip
import time
import json
import os
import sys
# .py files import
import colors
import instruction_dict

# Enable ANSI colors
if os.name == 'nt':
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

# load config.json
try:
    with open(os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), 'config.json')) as f:
        config = json.load(f)
except Exception as e:
    print(f"[ERROR] Couldn't load config.json: {e}")
    sys.exit(1)

SETPOS_KEY = config['SETPOS_KEY']
SETANG_KEY = config['SETANG_KEY']
SHOWPOS_KEY = config['SHOWPOS_KEY']
INSTRUCTION_KEY = config['INSTRUCTION_KEY']
EXIT_KEY = config['EXIT_KEY']
EXEC_KEY = config['EXEC_KEY']
SHOW_COMMANDS_KEY = config['SHOW_COMMANDS_KEY']
EC_SLEEP_TIME = config['EC_SLEEP_TIME']

INSTRUCTION_MESSAGE_LIST = [f'',
                            f'\n{colors.GREEN}{SETPOS_KEY}{colors.RESET} to set spawn', 
                            f'\n{colors.BRIGHT_MAGENTA}{SETANG_KEY}{colors.RESET} to place crosshair in a proper place',
                            f'\n{colors.CYAN}{SHOWPOS_KEY}{colors.RESET} to show your current spawn',
                            f'\n{colors.YELLOW}{INSTRUCTION_KEY}{colors.RESET} to show instruction for smoke',
                            f'\n{EXIT_KEY} to exit']


instruction_dict = instruction_dict.instruction_dict

def print_communicates(n):
    match n:
        case 1:
            print(f'{colors.GREEN}spawn copied successfully!{colors.RESET}')
        case 2:
            print(f'{colors.BRIGHT_MAGENTA}angle set successfully!{colors.RESET}')
        case 3:
            print(f'{colors.CYAN}spawn shown successfully!{colors.RESET}')
        case 4:
            print(f'{colors.YELLOW}instruction shown successfully!{colors.RESET}')

def error_label(on_chat = False):
    if on_chat: 
        return f'[ERROR] please select a spawn first using {SETPOS_KEY} key'
    return f'{colors.RED}[ERROR]{colors.BRIGHT_RED} please select a spawn first using {colors.BOLD}{SETPOS_KEY} key{colors.RESET}'

def execute_console_command(command, say=False):
    keyboard.press('`')
    keyboard.release('`')
    sleep(EC_SLEEP_TIME)
    if say:
        keyboard.write('say ')
        sleep(EC_SLEEP_TIME)
    sleep(EC_SLEEP_TIME)
    keyboard.write(command)
    sleep(EC_SLEEP_TIME)
    keyboard.press('enter')
    keyboard.release('enter')
    sleep(EC_SLEEP_TIME)
    keyboard.press('`')
    keyboard.release('`')

def copy_instant(spawns_list):  
    if len(spawns_list) ==0:
        return False
    random_index = random.randint(0, len(spawns_list)-1)
    random_spawn = spawns_list[random_index]
    pyperclip.copy(random_spawn)
    return random_spawn, random_index

def find_spawn(spawn_index, angles_list):
    return angles_list[spawn_index]

def set_ang(spawn_index, angles_list):
    try:
        index = int(spawn_index)
        ang = find_spawn(index, angles_list)
        execute_console_command(ang)
        print_communicates(2)
    except ValueError:
        print(error_label())
        cmnd = error_label(True)
        execute_console_command(cmnd, say=True)

def display_showpos(index):
    cmnd = f'SPAWN: {index+1}'
    execute_console_command(cmnd, say=True)
    print_communicates(3)

def display_instruction(chosen_map):
    execute_console_command('THROW INSTRUCTION', say=True)
    for i in range(len(instruction_dict[chosen_map])):
        cmnd = {instruction_dict[chosen_map][i]}
        execute_console_command(cmnd, say=True)
    print_communicates(4)
    pass

def get_data():
    try:
        with open('shared_data.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Can't read shared_data.json: {e}")
        sys.exit(1)
    chosen_map = data.get('chosen_map')
    spawns_list = data.get('spawns_list')
    angles_list = data.get('angles_list')
    team = data.get('team')
    chosen_indexes = data.get('chosen_indexes')
    return chosen_map, spawns_list, angles_list, team, chosen_indexes

def get_indexes_data():
    try:
        with open('shared_indexes.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Can't read shared_indexes.json: {e}")
        sys.exit(1)
    t_len = data.get('t_len')
    return t_len

# action on each button press
def pressed_key_logic(spawns_list, angles_list, chosen_map, team, chosen_indexes):
    last_action_time = {'setpos': 0, 'setang': 0, 'showpos': 0, 'instruction': 0, 'exit': 0} #optimalization, less lags
    debounce_delay = 0.2
    spawn_index = ''
    while True:
        current_time = time.time()
        # --- set position --- #
        if keyboard.is_pressed(SETPOS_KEY) and (current_time - last_action_time['setpos'] > debounce_delay):
            spawn, spawn_index = copy_instant(spawns_list)
            execute_console_command(spawn)
            while keyboard.is_pressed(SETPOS_KEY):
                pass
            print_communicates(1)

        # --- set crosshair --- #
        elif keyboard.is_pressed(SETANG_KEY) and (current_time - last_action_time['setang'] > debounce_delay):
            set_ang(spawn_index, angles_list)
            while keyboard.is_pressed(SETANG_KEY):
                pass
        
        # --- spawn display --- #
        elif keyboard.is_pressed(SHOWPOS_KEY) and (current_time - last_action_time['showpos'] > debounce_delay):
            try:
                spawn_index = int(spawn_index)
                index = chosen_indexes[spawn_index]
                if team != 'both':
                    display_showpos(index)
                else:
                    t_len = get_indexes_data()
                    if index >= t_len:
                        display_showpos(index - t_len)
                    else:
                        display_showpos(index)
            except ValueError:
                print(error_label())
                cmnd = error_label(True)
                execute_console_command(cmnd, say=True)
            while keyboard.is_pressed(SHOWPOS_KEY):
                    pass
        
        # --- instrucion display --- #
        elif keyboard.is_pressed(INSTRUCTION_KEY) and (current_time - last_action_time['instruction'] > debounce_delay):
            display_instruction(chosen_map)
            while keyboard.is_pressed(INSTRUCTION_KEY):
                pass
        
        # --- exit --- #
        elif keyboard.is_pressed(EXIT_KEY):
            break
        sleep(0.05)


def main():
    chosen_map, spawns_list, angles_list, team, chosen_indexes = get_data()

    INSTRUCTION_MESSAGE = ''
    INSTRUCTION_MESSAGE_LIST[0] = f'WHEN ON {colors.BG_BRIGHT_WHITE}{colors.BLACK} {chosen_map.upper()} {colors.RESET}, {colors.BOLD}PRESS{colors.RESET}:'
    for i in INSTRUCTION_MESSAGE_LIST: INSTRUCTION_MESSAGE += i

    print(INSTRUCTION_MESSAGE)
    pressed_key_logic(spawns_list, angles_list, chosen_map, team, chosen_indexes)
    try:
        os.remove("shared_data.json")
        os.remove("shared_indexes.json")
    except FileNotFoundError:
        pass

main()