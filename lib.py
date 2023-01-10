import math
import random
from colorama import Fore, Back, Style, init
import time
import class_data
from class_data import MQ, Coord, movement, char_trans
import json
import os
import sys
import copy
from pynput.keyboard import Key, Controller
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from os import system
from threading import Thread

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


def gen_path(ghost_id: int):
    _g = class_data.ai_data

    ghost_pos_index = {
        1: _g.heatseek_pos,
        2: _g.intercept_pos,
        3: _g.ghost2_pos,
        4: _g.random_pos
    }

    pos = ghost_pos_index[ghost_id]
    final = random.choice(class_data.map.vp_coord)
    path = find_path(pos, final)
    return path


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
    gen_map = [[*x] for x in _m["map_data"]]

    # Map Data Conversion
    class_data.map.map_data = class_data.map_obj(_m["name"], _m["innate_diff"], gen_map)
    class_data.map.map_x_off = _m["x_off"]
    class_data.map.map_y_off = _m["y_off"]
    class_data.player_data.starting_pos = Coord(_m["starting_pos"][0], _m["starting_pos"][1])
    class_data.map.blocking_char += _m["additional_blocking"]
    class_data.map.default_tile = _m["default_tile"]
    class_data.map.collision_tiles += _m["collision_tiles"]
    map_data_file.close()

    # Map Size Calc
    x_max = 0
    for row in class_data.map.map_data.data:
        x_max = len(row) if len(row) > x_max else x_max

    class_data.map.map_size = x_max * len(class_data.map.map_data.data)
    class_data.map.collected_coordinates.append(class_data.player_data.starting_pos)

    # Generate Pathfinding Map
    """
    Takes the entire map and checks character by character
    if the current tile is a blocking character if it is
    add a 0 to the pathfinding map row to represent a spot that
    cannot be moved on, if not a blocking character add a 1 to
    represent a spot that is (True) valid to use for pathfinding
    """
    def update(coord: Coord):  # Add ghost to available ghost position list
        class_data.map.ghost_house.append(coord)
        class_data.map.ghost_collected.append(coord)

    class_data.SysData.path_find_map = []
    class_data.map.points_avail = 0
    ghost_pos = []
    for _y, row in enumerate(gen_map[::-1]):
        _l = []  # Create local list to generate single row
        for _x, tile in enumerate(row):
            _block = tile in class_data.map.blocking_char
            _c = Coord(_x - 1, _y - 1)  # Coord shift
            _l.append(int(not _block or tile == "="))  # Path map generation

            if not _block:  # Adds coordinate to list of valid generic coordinates
                class_data.map.vp_coord.append(_c)

            # Tile functions
            if tile == "1":  # Check if tile is a Ghost Loader tile
                ghost_pos.append(_c)
                update(_c)
                # print(f"{Fore.GREEN}Found ghostpos {Fore.RESET}{ghost_pos}")
            elif tile == "@":  # Non-Point Blank space
                update(_c)
            elif tile == "$":  # Cherry tile
                class_data.map.ref_coord["$"].append(_c)
                class_data.map.points_avail += 1
            elif tile == "=":  # Ghost House Gate
                class_data.map.ghost_gate = _c
            elif tile == " ":  # Point tile
                class_data.map.points_avail += 1
        class_data.SysData.path_find_map.append(_l)  # Add created row to path_find_map
    # print(class_data.SysData.path_find_map)

    # Ghost Generation
    # _aiv.heatseak_pos, _aiv.random_pos, _aiv.ghost2_pos, _aiv.ghost3_pos = [x for x in ghost_pos]
    class_data.ai_data.ghost_spawn_pos = ghost_pos


def jsondump(obj):  # DEBUG, Remove in production
    return json.dumps(obj, default=lambda o: o.__dict__,
        sort_keys=True, indent=4)


def init_val():  # Initiate All Starting Values in class_data
    pass


def moveq_master():  # Movement Queue Master [TRUE INDEX for positioning]
    x_off = class_data.map.map_x_off
    y_off = class_data.map.map_y_off + class_data.map.initial_y_off
    _so = class_data.map.char_spacing
    p_y_off = 2   # Includes both coord printout and Point printout
    g_pkg_list = []
    while class_data.map.movement_active:
        while len(class_data.SysData.move_q) == 0:  # Loop Lock
            time.sleep(0.000000000001)  # Yep this is the single most important line. DO NOT REMOVE

        #pkg_list = class_data.SysData.move_q
        pkg_list = copy.deepcopy(class_data.SysData.move_q)
        for pkg in pkg_list:
            g_pkg_list.append(pkg)
            # Check for collisions

            # Update Position on backend
            if class_data.debug.map_backend_view:  # Debug
                show_map()

            # Print and overwrite for characters on display (y_off with -2 to account for coord display)
            class_data.map.map_data.data[::-1][pkg.old_pos.y + y_off - 2][pkg.old_pos.x + x_off] = pkg.old_char
            class_data.map.map_data.data[::-1][pkg.new_pos.y + y_off - 2][pkg.new_pos.x + x_off] = pkg.tile_char

            if class_data.debug.map_backend_view:  # Debug
                show_map()
                continue

            if not class_data.map.movement_active:
                break

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
            _pd = class_data.player_data
            print(Fore.RESET, end=f'\x1b[{p_y_off - 1}A\r')
            print(f"{Fore.YELLOW}Lives{Fore.RESET}: {Fore.LIGHTRED_EX}{_pd.lives}{Fore.RESET}/{Fore.RED}{_pd.max_lives} | {Fore.YELLOW}Points{Fore.RESET}: {Fore.GREEN}{class_data.player_data.points} | {class_data.map.points_avail}{Fore.RESET}")
            if class_data.debug.coord_printout:
                print(" " * 100, end='\r')  # line reset
                # print(f"[{Fore.YELLOW}DEBUG{Fore.RESET}] {Fore.RED}X{Fore.RESET}: {Fore.LIGHTGREEN_EX}{class_data.player_data.pos.x} {Fore.RED}Y{Fore.RESET}: {Fore.LIGHTGREEN_EX}{class_data.player_data.pos.y} {Fore.RESET}[{Fore.LIGHTGREEN_EX}Error_Count{Fore.RESET}] {Fore.YELLOW}{class_data.SysData.global_err}{Fore.RESET} Active_DIR: {class_data.player_data.active_direction}", end='\r')
                # print(f"[{Fore.YELLOW}DEBUG{Fore.RESET}] [Gen_Path: {Fore.LIGHTRED_EX}{class_data.debug.gen_path}{Fore.RESET}] [Distance: {Fore.LIGHTRED_EX}{class_data.debug.distance}{Fore.RESET}] [Dist_Chk: {Fore.LIGHTRED_EX}{class_data.debug.path_switch}{Fore.RESET}]", end='\r')
                print(f"{class_data.debug.test_val}", end='\r')
            else:
                print("\r", end='')

        for pk in g_pkg_list:
            if class_data.map.movement_active:
                class_data.SysData.move_q.remove(pk)
        g_pkg_list.clear()


def debug_map():
    # for row in class_data.SysData.path_find_map[::-1]:
    #     for tile in row:
    #         print(tile, end='')
    #     print("\n", end='')
    grid = Grid(matrix=class_data.SysData.path_find_map)
    start = grid.node(41, 8)
    end = grid.node(1, 1)
    finder = AStarFinder()
    path, runs = finder.find_path(start, end, grid)
    print(grid.grid_str(path=path, start=start, end=end))
    print(f"Runs: {runs}")
    grid.cleanup()


def find_path(s_pos: Coord, e_pos: Coord):  # [TRUE INDEX]
    grid = Grid(matrix=class_data.SysData.path_find_map)

    # x_off = class_data.map.map_x_off  # Map X Offset
    # y_off = class_data.map.map_y_off  # Map Y Offset

    x_off = 1
    y_off = 1

    start = grid.node(s_pos.x + x_off, s_pos.y + y_off)
    end = grid.node(e_pos.x + x_off, e_pos.y + y_off)
    finder = AStarFinder()
    path, runs = finder.find_path(start, end, grid)
    # Debug Code
    # print('operations:', runs, 'path length:', len(path))
    # print(grid.grid_str(path=path, start=start, end=end))
    # print(path)
    # print(class_data.SysData.move_q)
    return path


def get_distance(object_pos0: Coord, object_pos1: Coord, return_abs=True):  # Return absolute distance from p0 to p1
    dist = (object_pos1.x - object_pos0.x) ** 2 + (object_pos1.y - object_pos0.y) ** 2
    return math.sqrt(abs(dist) if return_abs else dist)


def translate_char(char: str):  # Translate a backend value into a display character for tile in row:
    d = {
        "X": char_trans("■", Fore.RED),
        "0": char_trans(class_data.player_data.starting_tile, Fore.LIGHTGREEN_EX),
        "1": char_trans("☺", Fore.LIGHTBLUE_EX),
        " ": char_trans("·"),
        "@": char_trans(" "),
        "$": char_trans("$", Fore.LIGHTCYAN_EX)
    }
    return d[char] if char in d.keys() else char_trans(char)


def get_char(coord: Coord):  # Get the backend value at the specified position
    return class_data.map.map_data.data[::-1][coord.y][coord.x]


def remove_gpkg(ghost_id: int):  # Remove all packages with specified ghost id (ignores next package)
    pkg_next = list(filter(lambda pkg: pkg.ghost_id == ghost_id, class_data.SysData.move_q))[0]
    class_data.SysData.move_q = list(filter(lambda pkg: pkg.ghost_id != ghost_id or pkg == pkg_next, class_data.SysData.move_q))


# Check if a certain coordinate is a valid movement [ACCOUNTS FOR OFFSET]
def check(coord: class_data.Coord):  # Returns if move is valid or not [TRUE INDEX]
    """
    Check if a certain coordinate is a valid movement [ACCOUNTS FOR OFFSET]

    :param coord: The coordinate to check
    :return: True or False
    """
    x_off = class_data.map.map_x_off
    y_off = class_data.map.map_y_off
    return class_data.map.map_data.data[::-1][coord.y + y_off][coord.x + x_off] not in class_data.map.blocking_char


def path_op(_path: list, op_div=3):
    x_off = class_data.map.map_x_off  # Map X Offset
    y_off = class_data.map.map_y_off  # Map Y Offset
    path = [(m[0] - x_off, m[1] - y_off) for m in _path]  # Adjust for map offset
    return path[:-round(len(path) // op_div)]  # Optimize and return


def map_comp(map):  # DEBUG, Remove in production
    return '\n'.join([''.join(y) for y in [[str(p) for p in z] for z in map]])


def debug_write(data: str, file):
    file.write(data)
    file.write("\n\n")


def queue_move(path: list, speed: float, ghost_id: int, _pos: Coord):
    for c in path:
        if class_data.map.movement_active is False: break  # Stop Movement Queueing on Collision

        adat = class_data.ai_data
        _pos = adat.heatseek_pos if ghost_id == 1 else adat.intercept_pos if ghost_id == 2 \
            else adat.ghost2_pos if ghost_id == 3 else adat.random_pos if ghost_id == 4 else None

        _last = adat.heatseek_last if ghost_id == 1 else adat.intercept_last if ghost_id == 2 \
            else adat.ghost2_last if ghost_id == 3 else adat.random_pos if ghost_id == 4 else None

        time.sleep(speed)
        _c = Coord(c[0], c[1])
        _ref = class_data.map.ref_coord  # Reference Coords

        """
        Old Coordinate Tile Setting (More soon?)
        $ -> Cherry
        """
        d_cherry = translate_char("$")
        t_cherry = d_cherry.colour + d_cherry.value + Fore.RESET

        # Old tile EVAL
        oc = t_cherry if _pos in _ref["$"] and _pos not in class_data.map.collected_coordinates \
            else "=" if _pos == class_data.map.ghost_gate else class_data.map.default_point if _pos not in \
            class_data.map.ghost_collected and _pos not in class_data.map.collected_coordinates else " "

        # Set new coordinates tile value
        _f = Coord(_c.x + 1, _c.y + 1)

        # oc = _last  # Use Last Old Tile from last iteration
        # n_pos = translate_char(get_char(_f)).value  # Converts offset back to true index
        class_data.SysData.move_q.append(movement(translate_char("1").value, _pos, _c, oc, ghost_id))

        # Set specified ghosts new position
        if ghost_id == 1:  # Couldn't find a better way of doing this.
            class_data.ai_data.heatseek_pos = _c
        elif ghost_id == 2:
            class_data.ai_data.intercept_pos = _c
        elif ghost_id == 3:
            class_data.ai_data.ghost2_pos = _c
        elif ghost_id == 4:
            class_data.ai_data.random_pos = _c


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
                map_out += Back.RED + Fore.LIGHTRED_EX + f"{f'■':^{local_spacing}}" + Fore.RESET + Back.RESET
            elif tile == " ":
                map_out += f"{'·':^{local_spacing}}"
            elif tile == "0":
                map_out += f"{class_data.player_data.starting_tile:^{local_spacing}}"
            elif tile == "@":
                map_out += f"{' ':^{local_spacing}}"
            elif tile == "$":
                char_data = translate_char("$")
                map_out += char_data.colour + f"{char_data.value:^{local_spacing}}" + Fore.RESET
            else:
                map_out += f"{tile:^{local_spacing}}"  # Return Exact tile
        map_out += "\n"

    # Panel Printing
    print(f"{map_in.name:^{_l * local_spacing}}")
    print(map_out, flush=True)


# Key Watcher
def press_process(key):
    try:
        if key.char == "w":
            class_data.player_data.active_direction = "up"
        elif key.char == "a":
            class_data.player_data.active_direction = "left"
        elif key.char == "s":
            class_data.player_data.active_direction = "down"
        elif key.char == "d":
            class_data.player_data.active_direction = "right"
    except Exception:
        pass
