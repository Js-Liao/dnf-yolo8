import numpy as np


class Point:

    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y

    def __bool__(self):
        return self.x is not None and self.y is not None

    def __str__(self):
        if self.x is None and self.y is None:
            return "Empty Point()"
        return f"Point({self.x}, {self.y})"

    def __repr__(self) -> str:
        return self.__str__()

    def __sub__(self, other):
        if self.x is None or self.y is None or other.x is None or other.y is None:
            raise ValueError("Cannot subtract empty points")
        return Point(self.x - other.x, self.y - other.y)

    def distance_to(self, other):
        if self.x is None or self.y is None or other.x is None or other.y is None:
            raise ValueError("Cannot calculate distance between empty points")
        return int(((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5)


class IMGArea:

    def __init__(self, starting_point: Point, width: int, height: int):
        self.starting_point = starting_point
        self.width = width
        self.height = height

    def __str__(self):
        return f"IMGArea({self.starting_point}, {self.width}, {self.height})"

    def __repr__(self) -> str:
        return self.__str__()

    def rect(self):
        return (self.starting_point.x, self.starting_point.y,
                self.starting_point.x + self.width, self.starting_point.y + self.height)


def partial_img(frame, area: IMGArea):
    cut_img = frame[area.starting_point.y:area.starting_point.y + area.height,
              area.starting_point.x:area.starting_point.x + area.width]
    return cut_img


def get_available_skills(frame) -> int:
    sk_width = 31
    sk_height = 28
    sk_starting_point = Point(432, 565)
    for x in range(6):
        skill_area = IMGArea(Point(sk_starting_point.x + x * sk_width, sk_starting_point.y), sk_width, sk_height)
        img0 = partial_img(frame, skill_area)
        count = 0
        for i in range(img0.shape[0]):
            for j in range(img0.shape[1]):
                # >127表示像素点偏白色
                if any(np.where(img0[i, j] > 127, True, False)):
                    count += 1
        gray_scale = count / (img0.shape[0] * img0.shape[1])
        if gray_scale > 0.3:
            return x
    return -1


class MiniMaps:
    # SKILL = IMGArea(Point(432, 565), 187, 28)
    # SKILL_A = IMGArea(Point(432, 565), 31, 28)
    # SKILL_S = IMGArea(Point(463, 565), 31, 28)
    # SKILL_D = IMGArea(Point(494, 565), 31, 28)
    # SKILL_F = IMGArea(Point(525, 565), 31, 28)
    # SKILL_G = IMGArea(Point(556, 565), 31, 28)
    # SKILL_H = IMGArea(Point(587, 565), 31, 28)
    SWITCH = IMGArea(Point(1030, 120), 35, 28)
    CLEAR = IMGArea(Point(810, 495), 90, 30)
    CYGQ = IMGArea(Point(985, 45), 75, 55)
    CCZL = IMGArea(Point(985, 45), 75, 55)
    HJQD = IMGArea(Point(985, 45), 75, 55)
    WYZJ = IMGArea(Point(967, 45), 93, 55)
    CURRENT_PATH = r'imgs\current.png'
    CLEAR_PATH = r'imgs\clear.png'
    YET_VISIT_PATH = r'imgs\yet_visit.png'
    SWITCH_PATH = r'imgs\switch.png'
    MAPS_DIR = r'imgs\maps'


class CLS:

    def __init__(self):
        self.hero = 0
        self.enemy = 1
        self.boss = 2
        self.up = 3
        self.down = 4
        self.left = 5
        self.right = 6
        self.boss_gate = 7
        self.drop = 8


if __name__ == '__main__':
    pass
