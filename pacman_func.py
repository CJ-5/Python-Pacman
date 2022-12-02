import time
import class_data
import lib
from lib import Coord, check

def pacmand():  # Pacman Logic Controller
    # Default Direction: Left
    """
    Cursor Movment Exit Codes
    \x1b[{n}A : Up
    \x1b[{n}B : Down
    \x1b[{n}C : Right
    \x1b[{n}D : Left
    """
    x_off = class_data.map.map_x_off
    y_off = class_data.map.map_y_off

    while class_data.map.movement_active:
        try:
            _active = class_data.player_data.active_direction  # Current direction of the player
            x_diff = 1 if _active == "right" else -1 if _active == "left" else 0  # X direction offset
            y_diff = 1 if _active == "up" else -1 if _active == "down" else 0  # Y direction offset
            _p = class_data.player_data.pos  # Player Coordinate [OFFSET]
            _p_true = Coord(_p.x + x_off, _p.y + y_off)  # True Player Coordinate [TRUE INDEX]
            new_coord = Coord(_p.x + x_diff, _p.y + y_diff)  # The next position of the player
            collision_thr = 1  # Collision threshold, equal to or less than will trigger collision event

            _ai = class_data.ai_data
            ghost_coord_null = [_ai.heatseek_pos, _ai.intercept_pos, _ai.ghost2_pos, _ai.random_pos]
            # ghost_coords = [(_pos if _pos is None else Coord(0, 0)) for _pos in ghost_coord_null]
            ghost_coords = ghost_coord_null
            pl_collision = True in [round(lib.get_distance(_p_true, _pos)) <= collision_thr if _pos is not None else False for _pos in ghost_coords]

            # Collision Checking
            if pl_collision:  # See if a collision has happened
                class_data.map.movement_active = False
                lives = class_data.player_data.lives
                if lives <= 0:
                    # Player is dead, Reinitiale Level 1
                    pass
                else:
                    lives -= 1

                # Player has been hit by ghost, re-initiate all data with life -1

            if check(new_coord):
                class_data.SysData.move_q.append(
                    class_data.movement(class_data.player_data.starting_tile, Coord(_p.x, _p.y), new_coord))

                class_data.player_data.pos = new_coord  # Update Player Coord

                # Add coordinate used list and add points
                if not new_coord in class_data.map.collected_coordinates:
                    class_data.player_data.points += 1
                    class_data.map.collected_coordinates.append(new_coord)
            time.sleep(0.100)  # Pacman Speed adjustment
        except Exception:
            class_data.SysData.global_err += 1
            continue
