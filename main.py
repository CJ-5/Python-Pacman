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
import ai
import pacman_func

if __name__ == "__main__":
    init()  # Colorama Init
    cursor.hide()

    gprint(MQ([ck("Welcome to "), ck("pacman", "yellow"), ck("!")]))
    gprint(MQ([ck("Initializing...")]))

    lib.map_loader("main")
    lib.show_map()

    time.sleep(1)
    pacman_func.script_init()
    ai.ghost_init()  # Initiate ghost data


    with keyboard.Listener(on_press=lib.press_process) as listener:
        listener.join()

