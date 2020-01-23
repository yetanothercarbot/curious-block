from raylibpy import *
from math import sqrt
from constants import *


class Block(Rectangle):
    """Represents a single block of the world"""
    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x*40, grid_y*40, 40, 40)


class Entity(Rectangle):
    """Represents the player"""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._health = 20
        self._dx = 0
        self._dy = 0

    def update_gravity(self, world):
        if self._collision(world, pos.DOWN):
            self._dy = min(self._dy, 0)
        else:
            self._dy += 0.3
        # set a maximum player speed
        self._dx = max(-8, min(8, self._dx))
        # Reduce player x-speed
        self._dx *= 0.9
        # A maximum fall speed but no maximum upwards speed
        self._dy = min(5, self._dy)

        self.x += self._dx
        self.y += self._dy

        print(self.y)

    def _collision(self, world, direction):
        collision = False

        if direction == pos.UP:
            selected_point = Vector2(self.x + self.width/2, self.y)
        elif direction == pos.RIGHT:
            selected_point = Vector2(self.x + self.width, self.y + self.height/2)
        elif direction == pos.DOWN:
            selected_point = Vector2(self.x + self.width/2, self.y + self.height)
        else: # Left
            selected_point = Vector2(self.x, self.y + self.height/2)

        for block in world:
            if check_collision_point_rec(selected_point, block):
                collision = True
        return collision

    def jump(self, world):
        if self._collision(world):
            self._dy = -8

class Player(Entity):
    def update_gravity(self, world, camera):
        super().update_gravity(world)
        camera.x = self.x
        camera.y = self.y

class Bot(Entity):
    def can_see_player(self, player_pos):
        diff_x = abs(player_pos[0] - self._x)
        diff_y = abs(player_pos[1] - self._y)
        distance = sqrt(diff_x**2 + diff_y**2)

        return True if distance < 20 else False

    def is_aggressive(self):
        raise NotImplementedError("Must be implemented by subclass.")



def main():
    state = {
        'screen_width': 1600,
        'screen_height': 800,
        'camera': Camera2D(),
        'player': Player(400, 280, 40, 40),
        'world': [Block(10, 10)]
    }

    init_window(state['screen_width'], state['screen_height'], "Curious Block")

    state['camera'].offset = Vector2(0, 0)
    state['camera'].target = Vector2(state['player'].x + 20, state['player'].y + 20)
    state['camera'].rotation = 0.0
    state['camera'].zoom = 1.0

    set_target_fps(60)

    while not window_should_close():
        update_gravity(state)
        redraw(state);


    close_window()

def update_gravity(state):
    if is_gamepad_available(0):
        state['player']._dx = 1.2 * get_gamepad_axis_movement(0, 2)
        state['player']._dy = 1.2 * get_gamepad_axis_movement(0, 3)
        if is_gamepad_button_pressed(0):
            state['player'].jump(state['world'])
    else:
        if is_key_down(KEY_D):
            state['player']._dx += 1.2
        if is_key_down(KEY_A):
            state['player']._dx -= 1.2
    if is_key_down(KEY_W):
        state['player'].jump(state['world'])

    state['player'].update_gravity(state['world'], state['camera'])


def redraw(state):
    begin_drawing()
    clear_background(RAYWHITE)
    begin_mode2d(state['camera'])

    draw_rectangle_rec(state['player'], RED)

    for block in state['world']:
        print(block)
        draw_rectangle_rec(block, GREEN)

    end_mode2d()

    draw_text(str(get_fps()), 10, 10, 30, DARKGRAY)

    end_drawing()


if __name__ == '__main__':
    main()
