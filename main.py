import lib
from class_data import MQ, Coord
import class_data
from lib import gprint, ck
import lib
from colorama import init
from pynput import keyboard
from threading import Thread


init() # Colorama Init

gprint(MQ([ck("Welcome to "), ck("pacman", "yellow"), ck("!")]))
gprint(MQ([ck("Initializing...")]))

# Print Map
# listen for arrow inputs
# Queue movements on press

lib.map_loader("main")
lib.show_map()

# class_data.SysData.kb_listen = keyboard.Listener(on_press=lib.press_process)
Thread(target=lib.moveq_master()).start()
with keyboard.Listener(on_press=lib.press_process) as listener:
    listener.join()
