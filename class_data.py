from dataclasses import dataclass


class debug:
    ignore_file_check = True
    coord_printout = True


@dataclass()
class MQ:
    messages: list


@dataclass()
class Coord:
    x: int
    y: int


@dataclass()
class movement:
    tile_char: str
    old_pos: Coord
    new_pos: Coord
    old_char: str = " "


@dataclass()
class Item:
    name: str
    desc: str = None
    qty: int = 1
    max_qty: int = 1
    type: int = 0  # Item type [Boost, Life, Ghost Orb]


@dataclass()
class map_obj:
    name: str = None  # The map name
    in_diff: int = 1  # The innate difficulty
    data: list = None  # The actual map data


class player_data:
    spawned = False
    lives = 3  # Current life count
    pos = Coord(0, 0)  # Current pacman coordinate
    inv = []  # Various items that have been picked up


class map:
    map_data: map_obj = None
    map_size: int = 0
    map_name: str = None
    map_x_off: int = 0
    map_y_off: int = 0
    initial_y_off = 2 if debug.coord_printout else 1
    char_spacing = 2
    movement_active = True
    blocking_char = ['X']


class SysData:
    kb_listen = None
    i_move_q = True
    move_q = [movement("K", Coord(3, 1), Coord(3, 5))]  # Movement package queue

