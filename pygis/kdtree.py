from dataclasses import dataclass
from typing_extensions import Self

from pygis.point import Point
from pygis.shape import Shape


def split(points: list[Point]) -> tuple[list[Point], Point, list[Point]]:
    head = []
    tail = []

    lo = 0
    hi = len(points) - 1

    while True:
        if lo == hi:
            return (head, points[lo], tail)

        if lo + 1 == hi:
            return (head, points[lo], tail + [points[hi]])

        head.append(points[lo])
        tail.append(points[hi])

        lo += 1
        hi -= 1


@dataclass
class KDTree:
    value: Point
    left: Self
    right: Self

    def check_left(self, shape: Shape):
        raise NotImplementedError()

    def check_right(self, shape: Shape):
        raise NotImplementedError()

    @staticmethod
    def from_points(points: list[Point]):
        return X_Node.from_points(points)

    def intersect(self, shape: Shape):
        if shape.contains(self.value):
            yield self.value

        if self.left and self.check_left(shape):
            yield from self.left.intersect(shape)

        if self.right and self.check_right(shape):
            yield from self.right.intersect(shape)

    @property
    def points(self):
        yield self.value

        if self.left:
            yield from self.left.points

        if self.right:
            yield from self.right.points

    @property
    def extent(self):
        xmin = min(p.x for p in self.points)
        ymin = min(p.y for p in self.points)
        xmax = max(p.x for p in self.points)
        ymax = max(p.y for p in self.points)

        sw = Point.from_planar_coords(xmin, ymin)
        ne = Point.from_planar_coords(xmax, ymax)

        return Shape.rectangle(sw, ne)


@dataclass
class X_Node(KDTree):

    def check_left(self, shape: Shape):
        return shape.bbox.sw.x <= self.value.x

    def check_right(self, shape: Shape):
        return shape.bbox.ne.x >= self.value.x

    @staticmethod
    def from_points(points: list[Point]):
        if not points:
            return None

        s = sorted(points, key=lambda p: p.x)

        west, mid, east = split(s)

        left_tree = Y_Node.from_points(west)
        right_tree = Y_Node.from_points(east)

        return X_Node(mid, left_tree, right_tree)


@dataclass
class Y_Node(KDTree):

    def check_left(self, shape: Shape):
        return shape.bbox.sw.y <= self.value.y

    def check_right(self, shape: Shape):
        return shape.bbox.ne.y >= self.value.y

    @staticmethod
    def from_points(points: list[Point]):
        if not points:
            return None

        s = sorted(points, key=lambda p: p.y)

        south, mid, north = split(s)

        left_tree = X_Node.from_points(south)
        right_tree = Y_Node.from_points(north)

        return Y_Node(mid, left_tree, right_tree)
