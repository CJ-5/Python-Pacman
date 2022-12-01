import class_data
import time
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import lib
from lib import get_distance, find_path, remove_gpkg, get_char
from class_data import Coord, movement
import copy


def heat_seek_ai():  # Version 1.3 Heat-seeker ai
    x_off = class_data.map.map_x_off  # Map X Offset
    y_off = class_data.map.map_y_off  # Map Y Offset
    while class_data.map.movement_active:
        try:
            _pos = class_data.ai_data.heatseek_pos  # Ghost Position
            _P = class_data.player_data.pos  # Current Player Position [OFFSET]
            _plpos = Coord(_P.x - x_off, _P.y - y_off)  # Player Position [TRUE INDEX]
            _dist = get_distance(_pos, _plpos)  # Distance from ghost to player
            speed = class_data.ai_data.heatseek_speed  # Queue Speed
            dist_thr = class_data.ai_data.heatseek_dist  # Distance check threshold

            def generic():  # Get Random Path
                lib.queue_move(lib.path_op(lib.gen_path(1), 1.4), speed, 1, _pos)

            if _dist <= dist_thr:
                generic()
            else:
                # Generate Path
                _path = find_path(class_data.ai_data.heatseek_pos, _P)  # Do some black magic [TRUE INDEX]
                path = lib.path_op(_path)  # Optimize path (basically just take 33% of the path lol)

                # Queue movements to go towards player
                lib.queue_move(path, speed, 1, _pos)
        except Exception:
            time.sleep(0.1)
            continue

        remove_gpkg(1)  # Remove all old packages for heatseek ghost


def intercept_ai_v2():
    x_off = class_data.map.map_x_off  # Map X Offset
    y_off = class_data.map.map_y_off  # Map Y Offset

    def intercept_path(s_pos: Coord, e_pos: Coord, player_pos: Coord, dire: str):  # [OFFSET] {UNTESTED}
        """
        This is a modified version of the lib.find_path algorithm, instead of finding a direct path
        this will regenerate a map everytime it runs and generate a tail behind the player of invalid
        space so that the ai will not follow the same path as heatseek.

        The tail is defined by the behind_pull arg, it will be the opposite of what the active_direction
        is, and it will generate a straight line of invalid space until an invalid character is hit.
        """

        mx_off = 1 if dire == "right" else -1 if dire == "left" else 0  # Move X Offset
        my_off = 1 if dire == "up" else -1 if dire == "down" else 0  # Move Y Offset

        s_pos = Coord(s_pos.x + x_off, s_pos.y + y_off)  # TRUE INDEX
        e_pos = Coord(e_pos.x + x_off, e_pos.y + y_off)  # TRUE INDEX
        player_pos = Coord(player_pos.x + x_off, player_pos.y + y_off)  # TRUE INDEX

        # Generate map from global
        map = copy.deepcopy(class_data.SysData.path_find_map)  # Create Deep Copy of Map

        """
        Generate invalid character in the opposite direction of the player and use that
        map for intercept processing. This solves the issue of intercept acting the same
        as heatseek
        """

        if mx_off != 0:  # X-Axis Processing
            map[player_pos.y][player_pos.x - mx_off] = 0
        elif my_off != 0:  # Y-Axis Processing
            map[player_pos.y - my_off][player_pos.x] = 0

        # Find Path
        grid = Grid(matrix=map)
        start = grid.node(s_pos.x, s_pos.y)
        end = grid.node(e_pos.x, e_pos.y)
        finder = AStarFinder()
        path, _ = finder.find_path(start, end, grid)
        return path

    while class_data.map.movement_active:
        try:
            player_dir = class_data.player_data.active_direction  # The player's active direction
            ai_pos = class_data.ai_data.intercept_pos  # The AI's current position [TRUE INDEX]
            ppos_true = class_data.player_data.pos  # The Player's Current position [TRUE INDEX]
            dist = round(get_distance(ai_pos, ppos_true))  # absolute distance from the ghost to the player
            dist_t = class_data.ai_data.intercept_dist  # Path_Gen switch distance threshold
            speed = class_data.ai_data.intercept_speed  # Speed dividend at which position changes are queued
            dist_chk = dist < dist_t  # Distance threshold check

            # DEBUG REMOVE THIS IN PRODUCTION
            class_data.debug.distance = dist
            class_data.debug.path_switch = dist_chk

            def generic():  # Get Random Path
                lib.queue_move(lib.path_op(lib.gen_path(2), 1.4), speed, 2, ai_pos)

            if dist_chk:
                # Get player direction offset
                mx_off = 1 if player_dir == "right" else -1 if player_dir == "left" else 0  # Move X Offset
                my_off = 1 if player_dir == "up" else -1 if player_dir == "down" else 0  # Move Y Offset

                # Get position that will intercept player's movement
                intercept_coord = Coord(ppos_true.x + mx_off, ppos_true.y + my_off)

                # Check if the move is valid
                if lib.check(intercept_coord):
                    # INTERCEPT PATH GEN _V2
                    path = lib.path_op(intercept_path(ai_pos, intercept_coord, ppos_true, player_dir), 2.7)

                    # Queue path for movement processing
                    lib.queue_move(path, speed, 2, ai_pos)
                else:
                    _path = lib.find_path(ai_pos, ppos_true)
                    if len(_path) < class_data.ai_data.intercept_override_thr:
                        lib.queue_move(lib.path_op(_path), speed, 2, ai_pos)
                    else:
                        generic()  # Run random path gen
            else:
                generic()  # Run random path gen

            # Remove ghost packages and re-calculate
            lib.remove_gpkg(2)

        except Exception:
            class_data.SysData.global_err += 1


def clyde_ai():
    pass
