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
    gen_path = None  # Gen Path Blank data
    distance = None  # Player -> Ai Distance
    path_switch = None  # 2 Mode Path switch
    test_val = None


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
        - Positioning: RELATIVE
        - [ai_name]_last: The last tile they were on (for reprint)
        - [ai_name]_speed: The offset speed for how fast the path movements are added to the queue
        - [ai_dist]: The distance threshold that is checked before ai main path_get is used
    """
    scatter = False  # Scatter mode toggle (Use Scatter path gen [Try to stay away from player])
    _dist = 10.0  # Local distance setting for generic distance checking
    contact_pause = False  # If the player came in contact with the ghost and the threads should be paused
    ghost_spawn_pos: list[Coord] = []  # List of coordinates where ghosts can spawn

    heatseek_pos: Coord = None  # ID: 1
    heatseek_last: str = " "
    heatseek_speed: float = 0.13
    heatseek_dist: float = _dist
    heatseek_g_last: Coord = None

    intercept_pos: Coord = None    # ID: 2
    intercept_last: str = " "
    intercept_speed: float = 0.13  # Adjust this?
    intercept_dist: float = _dist
    intercept_override_thr: float = 5.0  # Overrides threshold and initiates heatseek path_gen
    intercept_g_last: Coord = None

    ghost2_pos: Coord = None    # ID: 3
    ghost2_last: str = " "
    ghost2_speed: float = 0  # Adjust this
    ghost2_dist: float = None

    random_pos: Coord = None    # ID: 4
    random_last: str = " "
    random_speed: float = 0  # Adjust this
    random_dist: float = None


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
    default_tile = " "  # Point default tile (Override by map loader)
    vp_coord: list[Coord] = []  # Coordinates that are valid for movement with path_gen_v1. (Override by map loader)
    default_point = "??"  # Point tile default char
    ghost_gate: Coord = None  # Coordinate of ghost house gate
    ref_coord = {"$": []}  # Referral tiles. (Specifies which tile have special tiles to print)
    points_avail: int = 0  # The total amount of points that are available for collection
    collected_coordinates = []  # Where the player has already been and collected points
    ghost_house = []  # Ghost house coordinates
    ghost_collected = []
    collision_tiles = []


@dataclass()
class movement:
    tile_char: str  # The value of the tile / tile character
    old_pos: Coord  # Position the tile is currently / old position
    new_pos: Coord  # Where tile is being moved / new position
    old_char: str = map.default_tile  # Movement old tile value
    ghost_id: int = 0  # Specifies if the package is a movement for a ghost, use 0 if it is a player


@dataclass()
class Item:
    name: str   # Item name
    desc: str = None  # Item Description
    qty: int = 1  # Item given quantity
    max_qty: int = 1  # Item Max Quantity
    type: int = 0  # Item type [Boost, Life, Ghost Orb]


class player_data:
    starting_tile = "???"  # Player's tile
    spawned = False
    active_direction = "up"
    lives = 3  # Current life count
    max_lives = 3  # Max life count
    points = 0
    pos = Coord(0, 0)  # Current pacman coordinate / Starting pos [TRUE INDEX?]
    starting_pos: Coord = None
    inv = []  # Various items that have been picked up
    ghost_contact = False


class SysData:  # System Data
    kb_listen = None
    i_move_q = True
    move_q = []  # Movement package queue
    path_find_map = []  # Path finding source map
    global_err = 0   # Global Error DEBUG
    collision_pause = False  # Collision check pause lock

