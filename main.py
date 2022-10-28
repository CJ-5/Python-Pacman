import lib
from class_data import MQ, Coord
import class_data
from lib import gprint, ck
from colorama import init
from pynput import keyboard
import time
import os
from os import system as sy
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
#sy("cls")

# Print Map
# listen for arrow inputs
# Queue movements on press

lib.map_loader("main")
lib.show_map()

Thread(target=lib.moveq_master).start()  # Start management for global movement package queue
#Thread(target=lib.pacmand).start()  # Start management for pacman movement
Thread(target=lib.heat_seek_ai).start()  # Start management for heat-seeker ghost
#Thread(target=lib.debug_map).start()
# Debug Code Below
# print(lib.check(Coord(1, 1)))
# print(lib.jsondump(class_data.movement("t", Coord(0, 0), Coord(0, 0))))


with keyboard.Listener(on_press=lib.press_process) as listener:
    listener.join()