import time
import ai
import class_data
import lib
from lib import Coord, check
from os import system
from threading import Thread
from class_data import movement

def movewatch_start():
    Thread(target=lib.moveq_master).start()  # Start management for global movement package queue

def script_init(start_move=True):
    if start_move:
        movewatch_start()
    Thread(target=pacmand).start()  # Start management for pacman movement
    Thread(target=collision_watcher).start()  # Start Collision Watcher


def collision_watcher():
    """
    Independent Overwatch for ghost / pacman collision.
    :return:
    """
    x_off = class_data.map.map_x_off
    y_off = class_data.map.map_y_off

    while True:
        while not class_data.SysData.collision_pause:
            _p = class_data.player_data.pos  # Player Coordinate [OFFSET]
            _p_true = Coord(_p.x + x_off, _p.y + y_off)  # True Player Coordinate [TRUE INDEX]
            collision_thr = 1.2  # Collision threshold, equal to or less than will trigger collision event

            _ai = class_data.ai_data
            ghost_coord_null = [_ai.heatseek_pos, _ai.intercept_pos, _ai.ghost2_pos, _ai.random_pos]
            pl_collision = True in [round(lib.get_distance(_p_true, _pos), 2) <= collision_thr if _pos is not None else False for _pos in ghost_coord_null]  # Brain go brrr

            # Collision Checking
            if pl_collision:  # See if a collision has happened
                class_data.map.movement_active = False
                lives = class_data.player_data.lives
                if lives == 1:  # Player was already on their last life. Player is dead
                    # Player is dead, Re-initiate Level 1

                    time.sleep(1)
                    player_death()
                    return
                else:
                    class_data.player_data.lives -= 1
                    life_down()
                    return
            time.sleep(0.00000001)

        time.sleep(0.001)


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

            #_ai = class_data.ai_data
            #ghost_coord_null = [_ai.heatseek_pos, _ai.intercept_pos, _ai.ghost2_pos, _ai.random_pos]
            # ghost_coords = [(_pos if _pos is None else Coord(0, 0)) for _pos in ghost_coord_null]
            # pl_collision = True in [round(lib.get_distance(_p_true, _pos), 1) <= collision_thr if _pos is not None else False for _pos in ghost_coord_null]
            #
            # # Collision Checking
            # if pl_collision:  # See if a collision has happened
            #     class_data.map.movement_active = False
            #     lives = class_data.player_data.lives
            #     if lives == 1:  # Player was already on their last life. Player is dead
            #         # Player is dead, Re-initiate Level 1
            #
            #         time.sleep(1)
            #         playerdeath()
            #         return
            #     else:
            #         class_data.player_data.lives -= 1
            #         lifedown()
            #         return

            # Movement processing check
            if check(new_coord):
                class_data.SysData.move_q.append(movement(class_data.player_data.starting_tile, Coord(_p.x, _p.y), new_coord))

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


def player_death():  # Not Finished
    clear_cache(True)  # Full Cache Clear
    time.sleep(1)
    system("cls")  # Clear Full Screen
    time.sleep(1)
    lib.gprint(lib.MQ([lib.ck("Thou art Deadeth.")]))
    pass


def resume_points():
    """
    Clear all collected points from map so player can resume collection.

    Queues load packages into movement queue to clear space where coordinates have already been collected.

    :return: None
    """

    coord_list = class_data.map.collected_coordinates
    for c in coord_list:
        class_data.SysData.move_q.append(movement(" ", c, c, " "))  # Load package
    pass


def life_down():  # Player death event
    system("cls")  # Console Clear

    # Reload Initial Data
    lib.map_loader("main")  # Load initial map data
    lib.show_map()  # Re-initiate map display

    # Re-Initiate Ghost Data and movement
    class_data.map.movement_active = True  # Re-initiate movement lock
    clear_cache()  # Clear all cached old data
    resume_points()  # Queue movements for point resume
    movewatch_start()  # Start the floating collision watcher
    time.sleep(len(class_data.SysData.move_q) * 0.2)  # Dynamic wait, ensure all load packages are finished processing
    player_reset()  # Player data reset
    ai.ghost_init()  # Re-Initiate all ghost management threads
    script_init(False)  # Re-Initiate General Management Threads

