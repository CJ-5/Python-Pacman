from dataclasses import dataclass
import json
from colorama import Fore

# DEBUG FUNCTION
class Object:
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)


class debug:
    ignore_file_check = True  # Ignore environment file check
    coord_printout = True  # Print Coordinate Printout
    map_backend_view = False  # Print backend view of mapping
    ai_printout = False  # Print pathfinding runs for each ai


@dataclass()
class MQ:
    messages: list


@dataclass()
class Coord:
    x: int
    y: int

@dataclass()
class map_obj:
    name: str = None  # The map name
    in_diff: int = 1  # The innate difficulty
    data: list = None  # The actual map data


@dataclass()
class char_trans:
    value: str
    colour: Fore = Fore.WHITE


class ai_data:
    """
    Notes:
        - Positioning: NOT RELATIVE, POSITIONING IS TRUE INDEX
        - [ai_name]_last: The last tile they were on (for reprint)
        - [ai_name]_speed: The offset speed for how fast the path movements are added to the queue
    """
    scatter = False

    heatseek_pos: Coord = None  # ID: 1
    heatseek_last: str = None
    heatseek_speed: float = 0.075

    intercept_pos: Coord = None    # ID: 2
    intercept_last: str = None
    intercept_speed: float = 0.1  # Adjust this?

    ghost2_pos: Coord = None    # ID: 3
    ghost2_last: str = None
    ghoat2_speed: float = 0  # Adjust this

    random_pos: Coord = None    # ID: 4
    random_last: str = None
    random_speed: float = 0  # Adjust this


class map:  # Core Map Data
    map_data: map_obj = None  # Core map data object, holds live copy of all map data (Override by map loader)
    map_size: int = 0  # Map size x by y (Override by map loader)
    map_name: str = None  # Map name (Override by map loader)
    map_x_off: int = 0  # Map x offset (Override by map loader)
    map_y_off: int = 0  # Map y offset (Override by map loader)
    initial_y_off = 2  # Initial y offset
    char_spacing = 2  # Map character spacing
    movement_active = True  # If movement should be active
    blocking_char = ['X']  # List of characters that are not passable e.g a wall (Override by map loader)
    # default_tile = "·"  # Point default tile (Override by map loader)
    default_tile = " "  # Point default tile (Override by map loader)
    default_point = "·"
    collected_coordinates = []
    ghost_house = []
    ghost_collected = []
    collision_tiles = []


@dataclass()
class movement:
    tile_char: str  # The value of the tile / tile character
    old_pos: Coord  # Position the tile is currently / old position
    new_pos: Coord  # Where tile is being moved / new position
    old_char: str = map.default_tile
    ghost_id: int = 0  # Specifies if the package is a movement for a ghost, use 0 if it is a player


@dataclass()
class Item:
    name: str
    desc: str = None
    qty: int = 1
    max_qty: int = 1
    type: int = 0  # Item type [Boost, Life, Ghost Orb]


class player_data:
    starting_tile = "○"
    spawned = False
    active_direction = "up"
    lives = 3  # Current life count
    points = 0
    pos = Coord(0, 0)  # Current pacman coordinate / Starting pos [TRUE INDEX?]
    starting_pos: Coord = None
    inv = []  # Various items that have been picked up


class SysData:  # System Data
    kb_listen = None
    i_move_q = True
    move_q = []  # Movement package queue
    path_find_map = []
    global_err = 0

