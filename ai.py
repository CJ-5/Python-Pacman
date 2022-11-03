import class_data
import time

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
            _plpos = Coord(_P.x - 1, _P.y - 1)  # Player Position
            _dist = get_distance(_pos, _plpos)

            _path = find_path(class_data.ai_data.heatseek_pos, Coord(_plpos.x + 1, _plpos.y + 1))  # Do some black magic
            # path = [(m[0] - x_off, m[1] - y_off) for m in _path]
            # path = path[:-round(len(path)/3)]
            path = lib.path_op(_path)

            # Queue movements to go towards player
            last_dist = _dist
            speed = 0.075
            # for c in path:
            #     # _pos = class_data.ai_data.heatseek_pos  # Ghost Position
            #     # _P = class_data.player_data.pos
            #     # _plpos = Coord(_P.x - 1, _P.y - 1)  # Player Position
            #     # dist = get_distance(_pos, _plpos)
            #     _pos = class_data.ai_data.heatseek_pos
            #
            #     time.sleep(speed)
            #     _c = Coord(c[0], c[1])
            #     # char = get_char(_pos)
            #     oc = class_data.map.default_point if _pos not in class_data.map.ghost_collected \
            #         and _c not in class_data.map.collected_coordinates else " "
            #     class_data.SysData.move_q.append(movement("1", class_data.ai_data.heatseek_pos, _c, oc, 1))
            #     class_data.ai_data.heatseek_pos = _c
            class_data.ai_data.heatseek_pos = lib.queue_move(path, speed, 1, _pos)
        except Exception:
            continue

        remove_gpkg(1)  # Remove all old packages for ghost type


def intercept_ai():  # Version 1.1 Intercept ai
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
                    class_data.ai_data.intercept_pos = lib.queue_move(path, class_data.ai_data.intercept_speed, 2, intercept)  # Queue Path


        except:
            pass
        time.sleep(4)
        lib.remove_gpkg(2)
