from raylibpy import *
from math import sqrt, floor
from constants import *
import time, random


class Block(Rectangle):
    """Represents a single block of the world"""
    def __init__(self, grid_x, grid_y, collidable=True, colour=GREEN):
        super().__init__(grid_x*40, grid_y*40, 40, 40)
        self.colour = colour

class Entity(Rectangle):
    """Represents any entity"""
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self._health = 20
        self._dx = 0
        self._dy = 0
        self._double_jump = True

    def update_gravity(self, world):
        self._dy += 0.3
        # set a maximum player speed
        self._dx = max(-8, min(8, self._dx))
        # Reduce player x-speed
        self._dx *= 0.9
        # A maximum fall speed but no maximum upwards speed
        self._dy = min(5, self._dy)

        # self.x += self._dx
        #self.y += self._dy

        # Check that the player won't phase into the box
        new_pos = (self.x + self._dx, self.y + self._dy)

        if self._dx > 0:
            if self._collision(world, dir.RIGHT, new_pos):
                self.x = floor(self.x/40) * 40 + 10
                self._dx = 0
            else:
                self.x += self._dx
        elif self._dx < 0:
            if self._collision(world, dir.LEFT, new_pos):
                self.x = (1 + floor(self.x/40)) * 40
                self._dx - 0
            else:
                self.x += self._dx

        if self._dy > 0:
            if self._collision(world, dir.DOWN, new_pos):
                self.y = floor(self.y/40) * 40 + 10
                self._double_jump = True
                self._dy = 0
            else:
                self.y += self._dy
        elif self._dy < 0:
            if self._collision(world, dir.UP, new_pos):
                self.y = (1 + floor(self.y/40)) * 40
                self._dy = 0
            else:
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


    def _collision(self, world, direction, pos=None):
        if pos == None:
            pos = (self.x, self.y)
        points = []

        if direction == dir.UP:
            points = [(self.x + 1,              self.y - 1),
                      (self.x + self.width - 1, self.y - 1)]
        elif direction == dir.RIGHT:
            points = [(self.x + self.width + 1, self.y + 1),
                      (self.x + self.width + 1, self.y + self.height - 1)]
        elif direction == dir.DOWN:
            points = [(self.x + 1,              self.y + self.height + 1),
                      (self.x + self.width - 1, self.y + self.height + 1)]
        elif direction == dir.LEFT:
            points = [(self.x - 1, self.y + 1),
                      (self.x - 1, self.y + self.height - 1)]
        else:
            raise ValueError("No valid direction specified.")

        collision = False

        for block in world:
            if utility.calc_distance(self.x, self.y, block.x, block.y) < 40:
                for point in points:
                    if check_collision_point_rec(point, block):
                        collision = True
        return collision

    def jump(self, world):
        if self._collision(world, dir.DOWN):
            self._dy = -12
        elif self._double_jump:
            self._double_jump = False
            self._dy = -12

class Player(Entity):
    def update_gravity(self, world, camera):
        super().update_gravity(world)
        # camera.offset.x -= self._dx
        camera.offset.x = -self.x + 785
        camera.offset.y = -self.y + 385

class Bot(Entity):
    def can_see_player(self, player_pos):
        diff_x = abs(player_pos[0] - self._x)
        diff_y = abs(player_pos[1] - self._y)
        distance = sqrt(diff_x**2 + diff_y**2)

        return True if distance < 20 else False

    def is_aggressive(self):
        raise NotImplementedError("Must be implemented by subclass.")
class TriangleBot(Bot):
    def __init__(self, x, y):
        super().__init__()
class World():
    def __init__(self, width=90, height=50, border=True, seed=time.time()):
        super().__init__()
        self._width, self._height = width, height
        self._blocks = []

        if border:
            for i in range(width + 1):
                self._blocks.append(Block(i,0))
                self._blocks.append(Block(i, height))
            for i in range(1, height):
                self._blocks.append(Block(0, i))
                self._blocks.append(Block(width, i))
        self._generate(seed)
    def _generate(self, seed):
        random.seed(seed)
        centre_spots = []
        for row in range(20):
            centre_spots += [(10 * i + random.randint(-8,8),
                         5 + 3 * row + random.randint(-8,8)) for i in range(20)]

        for block in centre_spots:
            island_height = random.randint(1,3)
            for layer in range(island_height):
                island_width = random.randint(-(10-2*layer), 10 - 2*layer)
                for x in range(int(block[0]-island_width/2), int(block[0]+island_width/2)):
                    if (0 < x < self._width) and \
                       (0 < block[1] + layer < self._height):
                      self._blocks.append(Block(x, block[1] + layer))

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
    state['camera'].target = Vector2(state['player'].x, state['player'].y)
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
    if is_key_pressed(KEY_W):
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

if __name__ == '__main__':
    main()
