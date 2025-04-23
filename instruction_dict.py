# dict for proper instructions labels to print in the chat
import json
import os
import sys

BASE_DIR = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(BASE_DIR, 'config.json'), 'r') as f:
        config = json.load(f)
        SHOWPOS_KEY = config['SHOWPOS_KEY']
except Exception as e:
    print(f"[ERROR] instruction_dict.py: cannot read config.json: {e}")
    SHOWPOS_KEY = "P"

spawn_check_str = f'to check current spawn click [{SHOWPOS_KEY}] button'

instruction_dict = {
                    'ancient'   :   ['T -> window:', 
                                     'w + jumpthrow', 
                                     'SPAWNS 1, 4 AREN\'T INSTANT',
                                     'CT -> elbow:', 
                                     'shift, 2 steps + jumpthrow',
                                     spawn_check_str],
                    'anubis'    :   ['T -> window:', 
                                     'jumpthrow', 
                                     'CT -> stairs:', 
                                     'spawns 1,2 -> w + jumpthrow', 
                                     'spawns 3,4 -> jumpthrow',
                                     spawn_check_str],
                    'dust2'     :   ['T -> xbox:', 
                                     'spawns 1, 4, 5, 6, 7 -> jumpthrow', 
                                     'spawn 2 -> w + jumpthrow', 
                                     'spawn 3 -> crouch, go to the middle of the window and throw',
                                     spawn_check_str],
                    'inferno'   :   ['CT -> mid:', 
                                     'spawns 1, 4, 6 -> jumpthrow', 
                                     'spawns 2, 3, 5 -> w+jumpthrow',
                                     spawn_check_str],
                    'mirage'    :   ['T -> window:', 
                                     'w + jumpthrow'],
                    'train'     :   ['T -> sandwitch:', 
                                     'jumpthrow']
                    
                   }