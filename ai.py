import class_data
import time
from lib import get_distance, find_path, remove_gpkg
from class_data import Coord, movement


def heat_seek_ai():  # Version 1.0 Heat-seeker ai
    x_off = class_data.map.map_x_off  # Map X Offset
    y_off = class_data.map.map_y_off  # Map Y Offset
    while class_data.map.movement_active:
        _pos = class_data.ai_data.heatseek_pos  # Ghost Position
        _P = class_data.player_data.pos
        _plpos = Coord(_P.x - 1, _P.y - 1)  # Player Position
        _dist = get_distance(_pos, _plpos)

        _path = find_path(class_data.ai_data.heatseek_pos, Coord(_plpos.x + 1, _plpos.y + 1))  # Do some black magic
        path = [(x[0] - x_off, x[1] - y_off) for x in _path]
        path = path[:-round(len(path)/3)]

        # Queue movements to go towards player
        last_dist = _dist
        speed = 0.075
        for c in path:
            # _pos = class_data.ai_data.heatseek_pos  # Ghost Position
            # _P = class_data.player_data.pos
            # _plpos = Coord(_P.x - 1, _P.y - 1)  # Player Position
            # dist = get_distance(_pos, _plpos)


            time.sleep(speed)
            _c = Coord(c[0], c[1])
            class_data.SysData.move_q.append(movement("1", class_data.ai_data.heatseek_pos, _c, ghost_id=1))
            class_data.ai_data.heatseek_pos = _c
        remove_gpkg(1)  # Remove all old packages for ghost type