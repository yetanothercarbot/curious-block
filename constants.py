from math import sqrt

class pos:
    NONE = -1
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class utility:
    def calc_distance(x1, y1, x2, y2):
        return sqrt((x1-x2)**2 + (y1-y2)**2)
    def boundary(num, minimum, maximum):
        return min(max(num, minimum), maximum)
