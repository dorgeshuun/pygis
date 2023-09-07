from dataclasses import dataclass

from pygis.point import Point


@dataclass
class Rectangle:
    sw: Point
    ne: Point

    def contains(self, point: Point):

        if point.x < self.sw.x:
            return False

        if point.x > self.ne.x:
            return False

        if point.y < self.sw.y:
            return False

        if point.y > self.ne.y:
            return False

        return True

    @property
    def bbox(self):
        return self

    @property
    def x_side(self):
        return self.ne.x - self.sw.x

    @property
    def y_side(self):
        return self.ne.y - self.sw.y

    @property
    def is_square(self):
        return self.x_side == self.y_side

    @property
    def side(self):
        if not self.is_square:
            raise ValueError("not a square")
        return self.x_side
