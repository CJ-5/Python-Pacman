import time
import ai
import class_data
import lib
from lib import Coord, check
from os import system
from threading import Thread


def script_init():
    Thread(target=lib.moveq_master).start()  # Start management for global movement package queue
    Thread(target=pacmand).start()  # Start management for pacman movement


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
            collision_thr = 1.2  # Collision threshold, equal to or less than will trigger collision event

            _ai = class_data.ai_data
            ghost_coord_null = [_ai.heatseek_pos, _ai.intercept_pos, _ai.ghost2_pos, _ai.random_pos]
            # ghost_coords = [(_pos if _pos is None else Coord(0, 0)) for _pos in ghost_coord_null]
            pl_collision = True in [round(lib.get_distance(_p_true, _pos), 1) <= collision_thr if _pos is not None else False for _pos in ghost_coord_null]

            # Collision Checking
            if pl_collision:  # See if a collision has happened
                class_data.map.movement_active = False
                lives = class_data.player_data.lives
                if lives == 1:  # Player was already on their last life. Player is dead
                    # Player is dead, Re-initiate Level 1

                    time.sleep(1)
                    playerdeath()
                    return
                else:
                    class_data.player_data.lives -= 1
                    lifedown()
                    return

            # Movement processing check
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


def player_reset():
    player_data = class_data.player_data
    player_data.active_direction = "up"
    player_data.pos = Coord(0, 0)


def clear_cache(full_clear=False):
    """
    Temp Data clearing for map resetting.
    :param full_clear:  Whether or not to clear collected point data
    :return: None
    """
    class_data.SysData.move_q.clear()  # Clear all active movements

    if full_clear:
        class_data.map.ghost_collected.clear()
        class_data.map.collected_coordinates.clear()


def playerdeath():  # Not Finished
    clear_cache(True)  # Full Cache Clear
    pass


def resume_points():
    """
    Clear all collected points from map so player can resume collection
    :return:
    """
    coord_list = class_data.map.collected_coordinates
    for c in coord_list:
        pass
    pass


def lifedown():  # Player death event
    system("cls")  # Console Clear

    # Reload Initial Data
    lib.map_loader("main")
    lib.show_map()

    # Re-Initiate Ghost Data and movement
    class_data.map.movement_active = True
    clear_cache()  # Clear all cached old data
    player_reset()  # Player data reset
    ai.ghost_init()  # Re-Initiate all ghost management threads
    script_init()  # Re-Initiate General Management Threads

