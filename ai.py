import class_data
import time
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
import lib
from lib import get_distance, find_path, remove_gpkg, get_char
from class_data import Coord, movement


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


def intercept_ai_v1():  # Version 1.1 Intercept ai
    try:
        def pre_move():  # [Movement Prediction v1.0] Return Coord 1 in front of player (or until valid pos found)
            player_pos = class_data.player_data.pos
            player_dir = class_data.player_data.active_direction
            ai_data = class_data.ai_data
            intercept = ai_data.intercept_pos  # That's this ghost
            heatseek = ai_data.heatseek_pos  # Player should go in opposite direction of this

            mx_off = 1 if player_dir == "right" else -1 if player_dir == "left" else 0
            my_off = 1 if player_dir == "up" else -1 if player_dir == "down" else 0

            if (not mx_off and not my_off) or (mx_off and my_off):  # Calculation error
                raise Exception("Calculation error in Interception_AI mapping")  # Debug Code, Remove in production

            atmpt_coord = Coord(player_pos.x + mx_off, player_pos.y + my_off)
            if lib.check(atmpt_coord):
                atmpt_path = lib.find_path(intercept, player_pos)
                if len(atmpt_path > 0):
                    return atmpt_path
                else:
                    return predict(player_pos, intercept, heatseek)
            else:
                return predict(player_pos, intercept, heatseek)

        # Find neighbouring Coord to get path
        def predict(player_pos: Coord, intercept: Coord, heatseek: Coord):

            """
            check surrounding coordinates around player and look at where they are most likely to go next
            attempt to not intercept heatseek_ai
            """

            # Get list of valid neighbours
            ch_c = [
                Coord(player_pos.x + 1, player_pos.y),
                Coord(player_pos.x - 1, player_pos.y),
                Coord(player_pos.x, player_pos.y + 1),
                Coord(player_pos.x, player_pos.y - 1),
            ]  # Check Coord List

            # Filter down possible coordinates
            valid_coord = list(filter(lambda x: lib.check(x) is True, ch_c))  # List of total valid moves
            heatseek_list = list(filter(lambda x: x.ghost_id == 1, class_data.SysData.move_q))  # Heatseek ai move list
            non_intercept = list(filter(lambda x: x not in heatseek_list, valid_coord))  # Non Heatseek intercept coord list

            # Try to find non-intercepting path
            path = None
            for i in non_intercept:
                path = lib.find_path(intercept, i)
                if len(path):
                    break  # Path found

            path = None if not len(path) else path  # Null reset if no path was found.

            # Try to use coord not in list for heatseek. If not possible use any available coord
            if path is None:
                # No non-intercept path is available, use first available path
                for i in valid_coord:
                    path = lib.find_path(intercept, i)
                    if len(path):
                        return path  # Path found
                return None  # No path found

            return None  # No path was ever found

        # Get position in front of player
        while class_data.map.movement_active:
            try:
                pd = class_data.player_data.active_direction  # Player Direction
                ppos = class_data.player_data.pos  # Player Position
                intercept = class_data.ai_data.intercept_pos

                x_off = -1 if pd == "left" else 1 if pd == "right" else 0  # Active +1 x offset
                y_off = -1 if pd == "down" else 1 if pd == "up" else 0  # Active +1 y offset

                intercept_coord = Coord(ppos.x + x_off, ppos.y + y_off)  # Coordinate where ghost will intercept
                valid = lib.check(intercept_coord)  # Check if intercept coordinate is valid.

                if valid:
                    # get path and add to queue
                    _path = lib.find_path(intercept, intercept_coord)
                    path = lib.path_op(_path)
                    class_data.ai_data.intercept_pos = lib.queue_move(path, class_data.ai_data.heatseek_speed, 2, intercept)
                else:
                    # Run path prediction
                    _path = pre_move()  # raw path data
                    path = lib.path_op(_path)  # Get optimized path

                    if path is None or not len(path):  # No path was found and / or is invalid
                        continue  # No viable path was found, continue to next run
                    else:  # Path is valid
                        lib.queue_move(path, class_data.ai_data.intercept_speed, 2, intercept)  # Queue Path

                time.sleep(4)
                lib.remove_gpkg(2)  # Remove all ghost packages for recalculation
            except:
                class_data.SysData.global_err += 1
    except Exception:
        class_data.SysData.global_err += 1


def intercept_ai_v2():
    debug_file = open("./debug.txt", "a")
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

        x_off = 1
        y_off = 1

        mx_off = 1 if dire == "right" else -1 if dire == "left" else 0  # Move X Offset
        my_off = 1 if dire == "up" else -1 if dire == "down" else 0  # Move Y Offset

        s_pos = Coord(s_pos.x + x_off, s_pos.y + y_off)
        e_pos = Coord(e_pos.x + x_off, e_pos.y + y_off)
        player_pos = Coord(player_pos.x + x_off, player_pos.y + y_off)

        # Generate map from global
        map = class_data.SysData.path_find_map
        char_stop = False
        file_global = open("./debug.txt", "a")  # DEBUG

        """
        Generate invalid characters in the opposite direction of the player and use that
        map for intercept processing. This will theoretically avoid the issue of the intercept
        ai following the same path as heatseek.
        """
        itera = 0
        while not char_stop:  # Maybe optimize this?
            map = class_data.SysData.path_find_map  # get fresh map
            itera += 1
            # x-axis / y-axis processing switch
            if mx_off != 0:
                lib.debug_write("Horizontal Processing", file_global)
                # Run x-axis processing
                map_row = []
                for x, tile in enumerate(map[player_pos.y][::mx_off]):  # Get row that the player is in (flip if left)
                    if tile == 0:
                        lib.debug_write("Found exit char H", file_global)
                        char_stop = True  # break processing after iteration
                    elif x > player_pos.x and not char_stop:
                        tile = 0  # invalidate tile
                    map_row.append(tile[::mx_off])  # Add tile to modified row

                map[player_pos.y] = map_row  # Overwrite original row with modified one
            else:
                lib.debug_write("Vertical Processing", file_global)
                # Run y-axis processing
                map_new = []
                for x, row in enumerate(map[::my_off]):
                    if row[player_pos.x] == 0:
                        lib.debug_write("Found exit char V", file_global)
                        char_stop = True
                    elif x > player_pos.y:
                        lib.debug_write("No Exit char", file_global)
                        row[player_pos.x] = 0
                    map_new.append(row)
                map = map_new

            # Write Compiled map to file
            # lib.debug_write('\n'.join([''.join(x) for x in map]), debug_file)
            lib.debug_write(f"Finished Edit: {itera}: Player_POS {class_data.player_data.pos} Dir: {class_data.player_data.active_direction}", file_global)
            d = '\n'.join([''.join(y) for y in [[str(p) for p in z] for z in map]])
            lib.debug_write(str(d), file_global)
            class_data.SysData.global_err += 1
            file_global.flush()
            time.sleep(0.1)
        lib.debug_write("Return Path", file_global)


        grid = Grid(matrix=map)
        start = grid.node(s_pos.x, s_pos.y)
        end = grid.node(e_pos.x, e_pos.y)
        finder = AStarFinder()
        path, runs = finder.find_path(start, end, grid)
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
                # Generate path & Optimize
                #path = lib.path_op(lib.find_path(ai_pos, intercept_coord))
                # INTERCEPT PATH GEN _V2
                path = lib.path_op(intercept_path(ai_pos, intercept_coord, ppos_true, player_dir))
                # Queue path for movement processing
                lib.queue_move(path, speed, 2, ai_pos)
            else:
                class_data.SysData.global_err += 1

            # Remove and re-calculate
            time.sleep(0.001)
            lib.remove_gpkg(2)


        except Exception:
            class_data.SysData.global_err += 1
