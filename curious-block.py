from raylibpy import *
from math import sqrt, floor
from constants import *


class Block(Rectangle):
    """Represents a single block of the world"""
    def __init__(self, grid_x, grid_y, collidable=True):
        super().__init__(grid_x*40, grid_y*40, 40, 40)

class Entity(Rectangle):
    """Represents the player"""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._health = 20
        self._dx = 0
        self._dy = 0

    def update_gravity(self, world):
        self._dy += 0.3
        # Only check if moving in that direction
        if self._dy >= 0:
            if self._collision(world, pos.DOWN):
                self._dy = 0
        else:
            if self._collision(world, pos.UP):
                self._dy = 0

        if self._dx != 0:
            if self._collision(world, pos.RIGHT if self._dx > 0 else pos.LEFT):
                self._dx *= -0.5
        # set a maximum player speed
        self._dx = max(-8, min(8, self._dx))
        # Reduce player x-speed
        self._dx *= 0.9
        # A maximum fall speed but no maximum upwards speed
        self._dy = min(5, self._dy)

        self.x += self._dx
        self.y += self._dy

    def _calculate_grid_check_positions(self):
        # Get bias to left or right of cell.
        bias_x = -1 if (self.x % 40 <= 5) else 1
        bias_y = -1 if (self.y % 40 <= 5) else 1
        print(bias_x, bias_y)
        # Get grid x position/s
        grid_x = (floor(self.x/40), floor(self.x/40) + bias_x)
        grid_y = (floor(self.y/40), floor(self.y/40) + bias_y)

        return (grid_x, grid_y)


    def _collision(self, world, direction):
        points = []

        if direction == pos.UP:
            points = [(self.x + 1,              self.y - 1),
                      (self.x + self.width - 1, self.y - 1)]
        elif direction == pos.RIGHT:
            points = [(self.x + self.width + 1, self.y + 1),
                      (self.x + self.width + 1, self.y + self.height - 1)]
        elif direction == pos.DOWN:
            points = [(self.x + 1,              self.y + self.height + 1),
                      (self.x + self.width - 1, self.y + self.height + 1)]
        elif direction == pos.LEFT:
            points = [(self.x - 1, self.y + 1),
                      (self.x - 1, self.y + self.height - 1)]
        else:
            raise ValueError("No valid direction specified.")

        collision = False

        for block in world:
            if calc_distance(self.x, self.y, block.x, block.y) < 50:
                for point in points:
                    if check_collision_point_rec(point, block):
                        collision = True
        return collision

    def jump(self, world):
        if self._collision(world, pos.DOWN):
            self._dy = -8

class Player(Entity):
    def update_gravity(self, world, camera):
        super().update_gravity(world)
        camera.offset.x -= self._dx
        camera.offset.y -= self._dy

class Bot(Entity):
    def can_see_player(self, player_pos):
        diff_x = abs(player_pos[0] - self._x)
        diff_y = abs(player_pos[1] - self._y)
        distance = sqrt(diff_x**2 + diff_y**2)

        return True if distance < 20 else False

    def is_aggressive(self):
        raise NotImplementedError("Must be implemented by subclass.")

class World():
    def __init__(self, width=40, height=30, border=True):
        super().__init__()
        self._width, self._height = width, height
        self._blocks = [Block(1, 10), Block(2,8), Block(2,10), Block(3,9)]

        if border:
            for i in range(width + 1):
                self._blocks.append(Block(i,0))
                self._blocks.append(Block(i, height))
            for i in range(1, height):
                self._blocks.append(Block(0, i))
                self._blocks.append(Block(width, i))
    def get_blocks(self):
        return self._blocks

def main():
    state = {
        'screen_width': 1600,
        'screen_height': 800,
        'camera': Camera2D(),
        'player': Player(40, 280, 30, 30),
        'world': World()
    }

    init_window(state['screen_width'], state['screen_height'], "Curious Block")

    state['camera'].offset = Vector2(0, 0)
    state['camera'].target = Vector2(state['player'].x + 15, state['player'].y + 15)
    state['camera'].rotation = 0.0
    state['camera'].zoom = 1.0

    set_target_fps(60)

    while not window_should_close():
        update_gravity(state)
        redraw(state);


    close_window()

def update_gravity(state):
    if is_key_down(KEY_D):
        state['player']._dx += 1.2
    if is_key_down(KEY_A):
        state['player']._dx -= 1.2
    if is_key_down(KEY_W):
        state['player'].jump(state['world'].get_blocks())

    state['player'].update_gravity(state['world'].get_blocks(), state['camera'])


def redraw(state):
    begin_drawing()
    clear_background(RAYWHITE)
    begin_mode2d(state['camera'])

    state['camera'].target = Vector2(state['player'].x + 15, state['player'].y + 15)

    draw_rectangle_rec(state['player'], RED)

    for block in state['world'].get_blocks():
        draw_rectangle_rec(block, GREEN)

    end_mode2d()

    draw_text(str(get_fps()), 10, 10, 30, DARKGRAY)

    end_drawing()

def calc_distance(x1, y1, x2, y2):
    return sqrt((x1-x2)**2 + (y1-y2)**2)

if __name__ == '__main__':
    main()
