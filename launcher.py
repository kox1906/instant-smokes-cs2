import os
import json
import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QSizePolicy, QCheckBox, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

#========#
# layout #
#========#
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800
WINDOW_MOVE_X = 600
WINDOW_MOVE_Y = 100

#==================#
# global variables #
#==================#
BASE_DIR = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
PATH_MAPS = os.path.join(BASE_DIR, 'maps')
PATH_IMAGES = os.path.join(BASE_DIR, 'images')

maps = [f for f in os.listdir(PATH_MAPS) if os.path.isdir(os.path.join(PATH_MAPS, f))]
MAPS_LENGTH = len(maps)

team = ['t', 'ct']

MAP_BUTTON_HEIGHT = int(WINDOW_HEIGHT / (MAPS_LENGTH+0.75) - 20)
#===============================##===================##===============================#
#===============================##   P R O G R A M   ##===============================#
#===============================##===================##===============================#  

#-------------------------------------------------------------------------------------#

#==================#
# global functions #
#==================#
def teams_check_dict():
    team_status = {}
    for map_name in maps:
        for i in range(2):
            team_status[f'{map_name}_{team[i]}'] = True if os.path.isfile(f'{PATH_MAPS}/{map_name}/{map_name}_{team[i]}.txt') else False
    return team_status

def create_setparam_list(team_status, f_path = PATH_MAPS, suffix=''):
    result_dict = {}
    for map_name in maps:
        for t in team:
            key = f'{map_name}_{t}{suffix}'
            if team_status[f'{map_name}_{t}']:
                if os.path.isfile(f'{f_path}/{map_name}/{key}.txt'):
                    with open(f'{f_path}/{map_name}/{key}.txt', 'r') as f:
                        result_dict[key] = [line.strip() for line in f if line.strip()]
    return result_dict

def teams_check_map(chosen_map_index):
    chosen_map = maps[chosen_map_index]
    what_team = None
    i=0
    k=1
    while i<2:
        if teams_check_dict()[f'{chosen_map}_{team[i]}']:
            k+=1
            what_team = team[i]
        i+=1
    if k==3:
        k+=1
        what_team = 'both'
    return what_team

# run key_listener.exe (.py) after choose a map
def run_key_listener():
    if getattr(sys, 'frozen', False): #.exe version
        listener_path = os.path.join(os.path.dirname(sys.executable), 'key_listener.exe')
        subprocess.Popen(f'start "" "{listener_path}"', shell=True)
    else: #.py version
        script_path = os.path.join(os.path.dirname(__file__), "key_listener.py")
        python_path = sys.executable
        subprocess.Popen([python_path, script_path])

# run exec_loading.exe (.py) after choose a map
def run_exec():
    if getattr(sys, 'frozen', False):
        # .exe version
        exec_path = os.path.join(os.path.dirname(sys.executable), 'exec_loading.exe')
        subprocess.Popen(f'start "" "{exec_path}"', shell=True)
    else:
        # .py version
        script_path = os.path.join(os.path.dirname(__file__), "exec_loading.py")
        python_path = sys.executable
        subprocess.Popen([python_path, script_path])

# -> dump data into shared_data.json (that key listener using)
def send_data(chosen_map_index, chosen_spawns_list, chosen_angles_list, what_team, chosen_indexes):
    data = {
            'chosen_map': maps[chosen_map_index],
            'spawns_list': chosen_spawns_list,
            'angles_list': chosen_angles_list,
            'team': what_team,
            'chosen_indexes': chosen_indexes,
        }
    with open("shared_data.json", "w") as f:
        json.dump(data, f)

# -> dump indexes into shared_indexes.json (that key listener using)
def send_data_indexes(t_len):
    data = {
            't_len': t_len,
        }
    with open("shared_indexes.json", "w") as f:
        json.dump(data, f)

#==================#
#   class window   #
#==================#
class MainWindow(QWidget):
    def __init__(self, setpos_dict, setang_dict):
        super().__init__()
        self.setpos_dict = setpos_dict
        self.setang_dict = setang_dict
        self.setStyleSheet("""
        QWidget {
            background: qlineargradient(
                spread:pad,
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #121212,
                stop:0.5 #1a1a1a,
                stop:1 #000000
            );
        }
    """)

        self.setWindowTitle("Instant Smokes CS2")
        self.setWindowIcon(QIcon(f'smoke.ico'))
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.move(WINDOW_MOVE_X, WINDOW_MOVE_Y)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.display_map_button()

    def display_map_button(self):
        self.clear_layout(self.layout)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(20, 20, 20, 20)

        for i in range(MAPS_LENGTH):
            btn = self.build_map_button(i)
            self.layout.addWidget(btn)
        
        #exec button
        execbtn = self.build_exec_button()
        self.layout.addStretch()
        self.layout.addWidget(execbtn)

    def build_map_button(self, i: int) -> QPushButton:
        btn = QPushButton(maps[i])
        self.map_button_style(btn, maps[i])
        btn.clicked.connect(lambda _, x=i: self.handle_button(x))
        return btn
    
    def build_exec_button(self):
        btn = QPushButton('load exec')
        self.map_button_style(btn)
        btn.setToolTip('press to load exec for training')
        btn.clicked.connect(self.exec_loading)
        return btn
    
    def exec_loading(self):
        try:
            run_exec()
        except Exception as e:
            print(f"[ERROR] {e}")
            QMessageBox.critical(self, "Fatal error", str(e))

    def handle_button(self, index):
        self.chosen_map_index = index
        self.clear_layout(self.layout)
        self.display_spawn_checkbox(index)

    def check_all_checkboxes(self):
        for chbx in self.spawn_index_checkboxes:
            chbx.setChecked(True)

    def uncheck_all_checkboxes(self):
        for chbx in self.spawn_index_checkboxes:
            chbx.setChecked(False)

    def display_check_buttons(self):
        container = QWidget()
        check_layout = QHBoxLayout(container)
        container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        check_layout.setSpacing(10)
        check_layout.setContentsMargins(0,0,0,0)
        check_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_check = QPushButton('CHECK ALL')
        self.check_button_style(btn_check)
        btn_check.clicked.connect(self.check_all_checkboxes)
        check_layout.addWidget(btn_check, alignment=Qt.AlignmentFlag.AlignLeft)

        btn_uncheck = QPushButton('UNCHECK ALL')
        self.check_button_style(btn_uncheck)
        btn_uncheck.clicked.connect(self.uncheck_all_checkboxes)
        check_layout.addWidget(btn_uncheck, alignment=Qt.AlignmentFlag.AlignRight)

        self.checkbox_check_buttons_container = container
        
        self.checkbox_layout.addWidget(container)

    def display_spawn_checkbox(self, index):
        self.what_team = teams_check_map(index)
        if self.what_team == None:
            self.display_map_button()
            QMessageBox.information(self, 'Error', f'Missing setpos files in folder: {maps[index]}')
            return
        
        self.grid = QGridLayout()
        self.grid.setVerticalSpacing(10)
        self.grid.setHorizontalSpacing(10)

        container = QWidget()
        self.checkbox_layout = QVBoxLayout(container)

        if self.what_team != 'both':
            self.display_spawn_checkbox_one_team(index)
        else:
            self.display_spawn_checkbox_two_teams(index)

        if self.num_of_spawns == 0:
            self.display_map_button()
            QMessageBox.information(self, 'Error', f'Empty setpos files in folder: {maps[index]}')
            return
        
        self.checkbox_layout.setContentsMargins(0, 0, 0, 0)
        self.checkbox_layout.setSpacing(10)
        self.checkbox_layout.addLayout(self.grid)

        self.checkbox_layout.addStretch()
        self.display_check_buttons()
        self.display_run_button()

        self.layout.addWidget(container)
        self.display_back_button()
    
    def display_spawn_checkbox_one_team(self, index):
        self.spawn_index_checkboxes = []

        team_label = QLabel(self.what_team.upper())
        self.label_style(team_label)
        team_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.proper_spawns_list = self.setpos_dict[f'{maps[index]}_{self.what_team}']
        self.num_of_spawns = len(self.proper_spawns_list)

        for i in range(self.num_of_spawns):
            chbx = self.build_spawn_checkbox(i)
            row = i // 2
            col = i % 2
            self.grid.addWidget(chbx, row, col)
        
        self.checkbox_layout.addWidget(team_label)

    def display_spawn_checkbox_two_teams(self, index):
        self.spawn_index_checkboxes = []
        self.proper_spawns_list = self.setpos_dict[f'{maps[index]}_t'] + self.setpos_dict[f'{maps[index]}_ct']
        t_len = len(self.setpos_dict[f'{maps[index]}_t'])
        ct_len = len(self.setpos_dict[f'{maps[index]}_ct'])
        self.num_of_spawns = t_len + ct_len
        if t_len == 0:
            self.clear_layout(self.checkbox_layout)
            self.what_team = 'ct'
            self.display_spawn_checkbox_one_team(index)
        elif ct_len == 0:
            self.clear_layout(self.checkbox_layout)
            self.what_team = 't'
            self.display_spawn_checkbox_one_team(index)
        else:
            t_widget = QWidget()
            t_layout = QVBoxLayout(t_widget)
            t_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            t_label = QLabel("T")
            self.label_style(t_label)
            t_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t_layout.setSpacing(0)
            t_layout.setContentsMargins(0, 0, 0, 0)
            t_layout.addWidget(t_label)
            t_grid = QGridLayout()

            send_data_indexes(t_len)
            
            for i in range(t_len):
                chbx = self.build_spawn_checkbox(i)
                row = i // 2
                col = i % 2
                t_grid.addWidget(chbx, row, col)

            t_layout.addLayout(t_grid)
            self.checkbox_layout.addWidget(t_widget)

            ct_widget = QWidget()
            ct_layout = QVBoxLayout(ct_widget)
            ct_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            ct_label = QLabel("CT")
            self.label_style(ct_label)
            ct_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ct_layout.addWidget(ct_label)
            ct_layout.setSpacing(0)
            ct_layout.setContentsMargins(0, 0, 0, 0)

            ct_grid = QGridLayout()
            for j in range(t_len, t_len + ct_len):
                chbx = self.build_spawn_checkbox(j-t_len)
                row = (j - t_len) // 2
                col = (j - t_len) % 2
                ct_grid.addWidget(chbx, row, col)

            ct_layout.addLayout(ct_grid)
            self.checkbox_layout.addWidget(ct_widget)

    # run app button logic
    def run_app_logic(self):
        chosen_indexes = self.check_selected_spawns()
        if chosen_indexes == []:
            QMessageBox.information(self, 'Error', 'No spawn selected')
            return
        try:
            if self.what_team != 'both':
                self.proper_angles_list = self.setang_dict[f'{maps[self.chosen_map_index]}_{self.what_team}_setang']
            else:
                self.proper_angles_list = self.setang_dict[f'{maps[self.chosen_map_index]}_t_setang'] + self.setang_dict[f'{maps[self.chosen_map_index]}_ct_setang']
            chosen_spawns_list = []
            chosen_angles_list = []
            for i in chosen_indexes: 
                chosen_spawns_list.append(self.proper_spawns_list[i])
                chosen_angles_list.append(self.proper_angles_list[i])

            send_data(self.chosen_map_index, chosen_spawns_list, chosen_angles_list ,self.what_team, chosen_indexes)
            try:
                run_key_listener()
            except Exception as e:
                print(f"[ERROR] {e}")
                QMessageBox.critical(self, "Fatal error", str(e))
        except KeyError:
            if self.what_team in team:
                QMessageBox.information(self, 'Error', f'Missing files: {maps[self.chosen_map_index]}_{self.what_team}_setang')
            else:
                QMessageBox.information(self, 'Error', f'Missing files: {maps[self.chosen_map_index]}_[t / ct]_setang')
        

    def build_spawn_checkbox(self, i: int) -> QCheckBox:
        chbtn = QPushButton(f'SPAWN {i+1}')
        chbtn.setCheckable(True)
        chbtn.setChecked(True)
        self.spawn_checkbox_style(chbtn)
        self.spawn_index_checkboxes.append(chbtn)
        return chbtn

    def build_run_button(self) -> QPushButton:
        self.runapp_btn = QPushButton('RUN APP')
        self.runapp_btn.clicked.connect(self.run_app_logic)
        return self.runapp_btn

    def display_run_button(self):
        btn = self.build_run_button()
        self.run_button_style(btn)
        self.checkbox_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def build_back_button(self) -> QPushButton:
        btn = QPushButton('< BACK')
        btn.clicked.connect(self.display_map_button)
        return btn

    def display_back_button(self):
        btn = self.build_back_button()
        self.back_button_style(btn)
        self.checkbox_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)

    #===============================##================================##===============================#
    #===============================##   H E L P  F U N C T I O N S   ##===============================#
    #===============================##================================##===============================#   

    def check_selected_spawns(self):
        selected = []
        for i, chbx in enumerate(self.spawn_index_checkboxes):
            if chbx.isChecked():
                selected.append(i)
        return selected

    def clear_layout(self, layout: QVBoxLayout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    #===============================##================================##===============================#
    #===============================##   B U T T O N S  S T Y L E S   ##===============================#
    #===============================##================================##===============================#   
    def map_button_style(self, button: QPushButton, chosen_map = ''):
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.setMinimumHeight(MAP_BUTTON_HEIGHT)
        button.setStyleSheet(f"""
        QPushButton {{
            border-image: url("images/{chosen_map}.png") 0 0 0 0 stretch stretch;  
            background-repeat: no-repeat;
            background-position: center;

            color: white;
            font-size: 20px;
            font-family: 'Consolas', monospace;
            font-weight: bold;

            border: 2px solid #aaa;
            border-radius: 10px;
            padding: 10px;
        }}

        QPushButton:hover {{
            border: 2px solid #fff;
            color: #00ffff;
            background-color: rgba(0, 0, 0, 0.3);
            margin: 2px;  /* efekt „ściągnięcia” */
        }}

        QPushButton:pressed {{
            margin: 4px;
            background-color: rgba(0, 0, 0, 0.5);
            color: #ffcc00;
        }}
    """)
        return button
    
    def spawn_checkbox_style(self, button: QPushButton):
        button.setFixedSize(200,40)
        button.setStyleSheet("""
        QPushButton {
            font-size: 18px;
            font-family: Consolas, monospace;
            font-weight: bold;
            color: white;
            background-color: #333;
            border: 2px solid #666;
            border-radius: 8px;
            padding: 10px;
        }

        QPushButton:hover {
            background-color: #444;
            border: 2px solid #aaa;
            color: #00ffff;
        }

        QPushButton:checked {
            background-color: #00cc66;
            border: 2px solid #00ff99;
            color: black;
        }

        QPushButton:checked:hover {
            background-color: #00b359;
            border: 2px solid #00e68a;
        }
    """)
        return button

    def back_button_style(self, button: QPushButton):
        button.setFixedSize(100, 50)
        button.setStyleSheet("""
        QPushButton {
            font-size: 18px;
            font-family: Consolas, monospace;
            font-weight: bold;
            color: white;
            background-color: #333;
            border: 2px solid #666;
            border-radius: 8px;
            padding: 10px;
        }

        QPushButton:hover {
            background-color: #444;
            border: 2px solid #aaa;
            color: #00ffff;
        }

        QPushButton:checked {
            background-color: #00cc66;
            border: 2px solid #00ff99;
            color: black;
        }

        QPushButton:checked:hover {
            background-color: #00b359;
            border: 2px solid #00e68a;
        }
    """)
        
        return button
    
    def run_button_style(self, button: QPushButton):
        button.setFixedSize(200, 100)
        button.setStyleSheet("""
        QPushButton {
            font-size: 18px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: bold;
            color: #ffffff;
            background-color: #1f1f1f;
            border: 2px solid #444;
            border-radius: 8px;
            padding: 12px 24px;
        }

        QPushButton:hover {
            background-color: #292929;
            border: 2px solid #00bfff;
            color: #00eaff;
        }

        QPushButton:pressed {
            background-color: #111;
            border: 2px solid #007acc;
            color: #ffffff;
            padding-left: 26px;
            padding-right: 22px;
        }

        QPushButton:disabled {
            background-color: #555;
            color: #999;
            border: 2px solid #777;
        }
    """)

        return button
    
    def check_button_style(self, button: QPushButton):
        button.setFixedSize(170, 60)
        button.setStyleSheet("""
        QPushButton {
            font-size: 16px;
            font-family: 'Segoe UI', sans-serif;
            font-weight: 600;
            color: #ffffff;
            background-color: #2c2c2c;
            border: 2px solid #555;
            border-radius: 6px;
            padding: 10px 20px;
        }

        QPushButton:hover {
            background-color: #3d3d3d;
            border: 2px solid #00cc99;
            color: #00ffcc;
        }

        QPushButton:pressed {
            background-color: #1a1a1a;
            border: 2px solid #009977;
            color: #ffffff;
            padding-left: 22px;
            padding-right: 18px;
        }

        QPushButton:disabled {
            background-color: #444;
            color: #aaa;
            border: 2px solid #666;
        }
    """)
        return button

    def label_style(self, label: QLabel):
        label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-size: 64px;
                font-weight: 900;
                background-color: transparent;
                letter-spacing: 2px;
                padding: 10px;
            }
        """)

        return label



def main():
    team_status = teams_check_dict()
    setpos_dict = create_setparam_list(team_status)
    setang_dict = create_setparam_list(team_status, suffix='_setang')

    app = QApplication(sys.argv)
    window = MainWindow(setpos_dict, setang_dict)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()