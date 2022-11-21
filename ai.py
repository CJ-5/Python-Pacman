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
            _P = class_data.player_data.pos
            _plpos = Coord(_P.x - 1, _P.y - 1)  # Player Position [OFFSET]
            _dist = get_distance(_pos, _plpos)

            # _path = find_path(class_data.ai_data.heatseek_pos, Coord(_plpos.x + 1, _plpos.y + 1))  # Do some black magic
            _path = find_path(class_data.ai_data.heatseek_pos, _P)  # Do some black magic [TRUE INDEX]
            # path = [(m[0] - x_off, m[1] - y_off) for m in _path]
            # path = path[:-round(len(path)/3)]
            path = lib.path_op(_path)  # Optimise path (basically just take 33% of the path lol)

            # Queue movements to go towards player
            last_dist = _dist
            speed = 0.075
            lib.queue_move(path, speed, 1, _pos)
        except Exception:
            class_data.SysData.global_err += 1
            continue

        remove_gpkg(1)  # Remove all old packages for ghost type


def intercept_ai_v2():
    # debug_file = open("./debug.txt", "a")
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
        # x_off = class_data.map.map_x_off  # Map X Offset
        # y_off = class_data.map.map_y_off  # Map Y Offset

        # x_off = 1
        # y_off = 1

        mx_off = 1 if dire == "right" else -1 if dire == "left" else 0  # Move X Offset
        my_off = 1 if dire == "up" else -1 if dire == "down" else 0  # Move Y Offset

        s_pos = Coord(s_pos.x + x_off, s_pos.y + y_off)  # TRUE INDEX
        e_pos = Coord(e_pos.x + x_off, e_pos.y + y_off)  # TRUE INDEX
        player_pos = Coord(player_pos.x + x_off, player_pos.y + y_off)  # TRUE INDEX
        player_pos_r = class_data.player_data.pos  # RELATIVE PULL

        # Generate map from global
        file_global = open("./debug.txt", "a")  # DEBUG, REMOVE IN PRODUCTION
        map = copy.deepcopy(class_data.SysData.path_find_map)  # Create Deep Copy of Map

        """
        Generate invalid characters in the opposite direction of the player and use that
        map for intercept processing. This will theoretically avoid the issue of the intercept
        ai following the same path as heatseek.
        """
        itera = 0

        if mx_off != 0:  # X-Axis Processing
            # x_trigger = player_pos.x - mx_off  # Invert mx_off to check opposite direction
            # lib.debug_write("Horizontal Processing", file_global)
            # lib.debug_write("x_trigger " + str(x_trigger), file_global)
            map[player_pos.y][player_pos.x - mx_off] = 0

        elif my_off != 0:  # Y-Axis Processing
            # y_trigger = player_pos.y - my_off  # Invert my_off to check opposite direction
            # lib.debug_write(f"y_trigger {y_trigger}", file_global)

            map[player_pos.y - my_off][player_pos.x] = 0

        else:
            pass

        # Write Compiled map to file  >DEBUG<
        lib.debug_write(f"Finished Edit: {itera}: Player_POS_R {player_pos_r} Player_POS_T {player_pos} Dir: {class_data.player_data.active_direction}", file_global)
        d = lib.map_comp(map)
        lib.debug_write(str(d), file_global)
        class_data.SysData.global_err += 1
        lib.debug_write("Returning Path", file_global)

        # Find Path
        grid = Grid(matrix=map)
        start = grid.node(s_pos.x, s_pos.y)
        end = grid.node(e_pos.x, e_pos.y)
        finder = AStarFinder()
        path, _ = finder.find_path(start, end, grid)
        file_global.close()
        return path

    while class_data.map.movement_active:
        try:
            player_dir = class_data.player_data.active_direction  # The player's active direction
            ai_pos = class_data.ai_data.intercept_pos  # The AI's current position [TRUE INDEX]
            ppos_true = class_data.player_data.pos  # The Player's Current position [TRUE INDEX]
            dist = get_distance(ai_pos, ppos_true)  # absolute distance from the ghost to the player [TRUE INDEX]
            speed = class_data.ai_data.intercept_speed

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
                class_data.SysData.global_err += 1

            # Remove and re-calculate
            lib.remove_gpkg(2)


        except Exception:
            class_data.SysData.global_err += 1
