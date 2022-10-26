from colorama import Fore, Back, Style, init
import time
import class_data
from class_data import MQ, Coord
import json
import os
import sys
from pynput.keyboard import Key, Controller
import curses

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
    class_data.map.default_tile = _m["default_tile"]
    map_data_file.close()

    # Map Size Calc
    x_max = 0
    for row in class_data.map.map_data.data:
        x_max = len(row) if len(row) > x_max else x_max
    class_data.map.map_size = x_max * len(class_data.map.map_data.data)


def jsondump(obj):
    return json.dumps(obj, default=lambda o: o.__dict__,
        sort_keys=True, indent=4)


def moveq_master():  # Movement Queue Master
    # print("Movement Queue Master Running...")
    # print(Fore.RESET, end='\r')
    x_off = class_data.map.map_x_off
    y_off = class_data.map.map_y_off + class_data.map.initial_y_off
    _so = class_data.map.char_spacing
    p_y_off = 2 if class_data.debug.coord_printout else 1  # Includes both coord printout and Point printout

    while class_data.SysData.i_move_q:
        while not len(class_data.SysData.move_q):
            continue
        pkg_list = class_data.SysData.move_q
        for pkg in pkg_list:
            # Update Position on backend

            if class_data.debug.map_backend_view:  # Debug
                show_map()

            class_data.map.map_data.data[::-1][pkg.old_pos.y + y_off - 2][pkg.old_pos.x + x_off] = pkg.old_char
            class_data.map.map_data.data[::-1][pkg.new_pos.y + y_off - 2][pkg.new_pos.x + x_off] = pkg.tile_char

            if class_data.debug.map_backend_view:  # Debug
                show_map()
                continue

            # print("Processing Package")
            # Remove Old Character

            print(Fore.RESET, end='')
            print(f"\x1b[{pkg.old_pos.y + y_off}A", end='')  # Move Y
            print(f"\x1b[{(pkg.old_pos.x + x_off) * _so}C", end='')  # Move X
            print(f"{Fore.WHITE}{pkg.old_char}{Fore.RESET}", end='')  # Reset Tile
            print(f"\x1b[{pkg.old_pos.y + y_off}B", end='\r')  # Reset X and Y

            # Place in new character
            print(f"\x1b[{pkg.new_pos.y + y_off}A", end='')  # Move Y
            print(f"\x1b[{(pkg.new_pos.x + x_off) * _so}C", end='')  # Move X
            print(pkg.tile_char, end='')  # Reset Tile
            print(f"\x1b[{pkg.new_pos.y + y_off}B", end='\r')  # Reset X and Y

            # Coordinate Display Update
            print(Fore.RESET, end=f'\x1b[{p_y_off - 1}A\r')
            print(f"{Fore.YELLOW}Points{Fore.RESET}: {Fore.GREEN}{class_data.player_data.points}{Fore.RESET}")
            if class_data.debug.coord_printout:
                #print("{:<15}".format(f"[{Fore.YELLOW}DEBUG{Fore.RESET}] {Fore.RED}X{Fore.RESET}: {Fore.LIGHTGREEN_EX}{class_data.player_data.pos.x} {Fore.RED}Y{Fore.RESET}: {Fore.LIGHTGREEN_EX}{class_data.player_data.pos.y}", end='\r'))
                print(" " * 25, end='\r')
                print(f"[{Fore.YELLOW}DEBUG{Fore.RESET}] {Fore.RED}X{Fore.RESET}: {Fore.LIGHTGREEN_EX}{class_data.player_data.pos.x} {Fore.RED}Y{Fore.RESET}: {Fore.LIGHTGREEN_EX}{class_data.player_data.pos.y}", end='\r')
            #print(f"\x1b[{p_y_off - 1}B\r", end='')
        for pk in pkg_list:
            class_data.SysData.move_q.remove(pk)


def check(coord: class_data.Coord):  # Returns if move is valid or not
    x_off = class_data.map.map_x_off
    y_off = class_data.map.map_y_off
    return not class_data.map.map_data.data[::-1][coord.y + y_off][coord.x + x_off] in class_data.map.blocking_char


def pacmand():  # This makes pacman move
    # Default Direction: Left
    """
    \x1b[{n}A : Up
    \x1b[{n}B : Down
    \x1b[{n}C : Right
    \x1b[{n}D : Left
    """
    x_off = class_data.map.map_x_off
    y_off = class_data.map.map_y_off
    while class_data.map.movement_active:
        _active = class_data.player_data.active_direction
        x_diff = -1 if _active == "right" else 1 if _active == "left" else 0
        y_diff = 1 if _active == "up" else -1 if _active == "down" else 0
        _p = class_data.player_data.pos
        new_coord = Coord(_p.x + x_diff, _p.y + y_diff)
        if check(new_coord):
            class_data.SysData.move_q.append(
                class_data.movement(class_data.player_data.starting_tile, Coord(_p.x, _p.y), new_coord))

            class_data.player_data.pos = new_coord  # Update Player Coord

            # Add coordinate used list and add points

            if not new_coord in class_data.map.collected_coordinates:
                class_data.player_data.points += 1
                class_data.map.collected_coordinates.append(new_coord)

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
                map_out += f"{class_data.player_data.starting_tile:<{local_spacing}}"
            else:
                map_out += f"{tile:<{local_spacing}}"
        map_out += "\n"

    # Panel Printing
    print(f"{map_in.name:^{_l * local_spacing}}")
    print(map_out, flush=True)
    # if class_data.debug.coord_printout:
        # print("")
        # print(f"[{Fore.YELLOW}DEBUG{Fore.RESET}] {Fore.RED}X{Fore.RESET}: {Fore.LIGHTGREEN_EX}0 {Fore.RED}Y{Fore.RESET}: {Fore.LIGHTGREEN_EX}0")


# Main Key listener
def press_process(key):
    # class_data.player_data.active_direction
    #print(key.char)
    try:
        if key.char == "w":
            class_data.player_data.active_direction = "up"
        elif key.char == "a":
            class_data.player_data.active_direction = "right"
        elif key.char == "s":
            class_data.player_data.active_direction = "down"
        elif key.char == "d":
            class_data.player_data.active_direction = "left"

    except Exception:
        #print("Failed")
        pass

