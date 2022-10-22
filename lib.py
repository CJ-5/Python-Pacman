from colorama import Fore, Back, Style, init
import time
import class_data
from class_data import MQ
import json
import os
import sys
from pynput.keyboard import Key, Controller

kb = Controller()

def ck(text: str, color: str = None):  # Kind of useless
    return text, color


def gprint(queue, speed: int = 25):
    # Print as if the text was being typed
    if type(queue) is not MQ:
        # Converts raw string into MQ format
        queue = MQ([(queue, None)])
    delay = speed / 1000  # Seconds to milliseconds conversion
    # Used to index color by string key
    colors_list = {"red": Fore.RED, "green": Fore.GREEN, "yellow": Fore.YELLOW, "blue": Fore.BLUE,
                   "magenta": Fore.MAGENTA, "cyan": Fore.CYAN, "white": Fore.WHITE}
    for msg in queue.messages:
        if msg[1] is not None:
            # if color printing is specified
            print(colors_list[msg[1].lower()], end='')
            for char in msg[0]:
                print(char, end='')
                time.sleep(delay)
            print(Fore.RESET, end='')
        else:
            for char in msg[0]:
                print(char, end='')
                time.sleep(delay)
    print()  # Create new line


def map_loader(map_id: str = None):

    if not os.path.isfile("mapdata.json") and not class_data.debug.ignore_file_check:
        gprint(MQ([ck("Uh oh looks like you are missing the core map data file ", "yellow"),  ck("mapdata.json", "red"),
                   ck(" if this file is corrupt or missing please re-download it", "yellow")]))
        exit(0)

    map_data_file = open("./mapdata.json")
    map_data = json.load(map_data_file)

    if map_id not in map_data["maps"]:
        map_id = "main"

    #class_data.map.map_data = map_data["maps"][map_id]["map_data"]
    _m = map_data["maps"][map_id]

    # Map Data Conversion
    class_data.map.map_data = class_data.map_obj(_m["name"], _m["innate_diff"], [[*x] for x in _m["map_data"]])
    class_data.map.map_x_off = _m["x_off"]
    class_data.map.map_y_off = _m["y_off"]
    class_data.map.blocking_char += _m["additional_blocking"]
    map_data_file.close()

    # Map Size Calc
    x_max = 0
    for row in class_data.map.map_data.data:
        x_max = len(row) if len(row) > x_max else x_max
    class_data.map.map_size = x_max * len(class_data.map.map_data.data)


def moveq_master():  # Movement Queue Master
    # print("Movement Queue Master Running...")
    init()
    # print(Fore.RESET, end='\r')
    x_off = class_data.map.map_x_off
    y_off = class_data.map.map_y_off + class_data.map.initial_y_off
    _so = class_data.map.char_spacing

    while class_data.SysData.i_move_q:
        for pkg in class_data.SysData.move_q:
            # Update Position on backend

            #show_map()
            class_data.map.map_data.data[::-1][pkg.old_pos.y + y_off - 2][pkg.old_pos.x + x_off] = pkg.old_char
            class_data.map.map_data.data[::-1][pkg.new_pos.y + y_off - 2][pkg.new_pos.x + x_off] = pkg.tile_char
            #print(class_data.map.map_data.data[::-1][pkg.old_pos.y + y_off][pkg.old_pos.x + x_off])
            #show_map()

            # print("Processing Package")
            # Remove Old Character
            #print('\033[?25l', end="")  # Hide Cursor
            print(f"\x1b[{pkg.old_pos.y + y_off}A", end='')  # Move Y
            print(f"\x1b[{(pkg.old_pos.x + x_off) * _so}C", end='')  # Move X
            print(pkg.old_char, end='')  # Reset Tile
            print(f"\x1b[{pkg.old_pos.y + y_off}B", end='\r')  # Reset X and Y

            # Place in new character
            print(f"\x1b[{pkg.new_pos.y + y_off}A", end='')  # Move Y
            print(f"\x1b[{(pkg.new_pos.x + x_off) * _so}C", end='')  # Move X
            print(pkg.tile_char, end='')  # Reset Tile
            print(f"\x1b[{pkg.new_pos.y + y_off}B", end='\r')  # Reset X and Y
            # Coordinate Display
            #print('\033[?25h', end="")  # Show Cursor
        class_data.SysData.move_q.clear()


def check(coord: class_data.Coord):
    return



def pacmand():  # This makes pacman move
    # Default Direction: Left
    while class_data.map.movement_active:

        time.sleep(0.100)


def show_map(map_in: class_data.map_obj = None):
    # Map Visual Processing
    if map_in is None:
        map_in = class_data.map.map_data

    local_spacing = class_data.map.char_spacing
    map_out = ""
    _l = 0
    for row in map_in.data:
        _l = len(row) if len(row) > _l else _l  # Get max out of all rows
        for tile in row:
            if tile == "X":
                map_out += Fore.RED + f"{'■':<{local_spacing}}" + Fore.RESET
            elif tile == " ":
                map_out += f"{'·':<{local_spacing}}"
            elif tile == "0":
                map_out += f"{'○':<{local_spacing}}"
            else:
                map_out += f"{tile:<{local_spacing}}"
        map_out += "\n"

    # Panel Printing
    print(f"{map_in.name:^{_l * local_spacing}}")
    print(map_out, flush=True, end='')
    if class_data.debug.coord_printout:
        print(f"[{Fore.YELLOW}DEBUG{Fore.RESET}] {Fore.RED}X{Fore.RESET}: {Fore.LIGHTGREEN_EX}0 {Fore.RED}Y{Fore.RESET}: {Fore.LIGHTGREEN_EX}0")


# Main Key listener
def press_process(key):
    pass

