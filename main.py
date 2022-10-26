import lib
from class_data import MQ, Coord
import class_data
from lib import gprint, ck
from colorama import init
from pynput import keyboard
import time
import os
from colorama import *
import configparser
import lib
import sys
import timeit
from threading import Thread
import cursor

init()  # Colorama Init
cursor.hide()

gprint(MQ([ck("Welcome to "), ck("pacman", "yellow"), ck("!")]))
gprint(MQ([ck("Initializing...")]))

# Print Map
# listen for arrow inputs
# Queue movements on press

lib.map_loader("main")
lib.show_map()

Thread(target=lib.moveq_master).start()
Thread(target=lib.pacmand).start()

# Debug Code Below
# print(lib.check(Coord(1, 1)))
# print(lib.jsondump(class_data.movement("t", Coord(0, 0), Coord(0, 0))))


with keyboard.Listener(on_press=lib.press_process) as listener:
    listener.join()
