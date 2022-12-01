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


def ghost_init():
    # Initiate Positions
    _pos = class_data.ai_data.ghost_spawn_pos
    class_data.ai_data.heatseek_pos = _pos[0]
    class_data.ai_data.intercept_pos = _pos[1]
    # class_data.ai_data.ghost2_pos = _pos[2]
    # class_data.ai_data.random_pos = _pos[3]

    # Start Management Threads
    Thread(target=ai.heat_seek_ai).start()  # Start management for heat-seeker ghost
    # Thread(target=ai.intercept_ai_v2).start()  # Start management for intercept ghost
    # Thread(target=ai.clyde_ai).start()  # Start management for clyde ghost

file_global = open("./debug.txt", "a")

init()  # Colorama Init
cursor.hide()

gprint(MQ([ck("Welcome to "), ck("pacman", "yellow"), ck("!")]))
gprint(MQ([ck("Initializing...")]))

lib.map_loader("main")
lib.show_map()
file_global.close()

time.sleep(1)
Thread(target=lib.moveq_master).start()  # Start management for global movement package queue
Thread(target=pacman_func.pacmand).start()  # Start management for pacman movement
ghost_init()  # Initiate ghost data


with keyboard.Listener(on_press=lib.press_process) as listener:
    listener.join()


