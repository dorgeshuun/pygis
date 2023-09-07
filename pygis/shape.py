from dataclasses import dataclass

from pygis.point import Point
from pygis.rectangle import Rectangle
# from geometry.ellipse import Ellipse


@dataclass
class Shape:

    @staticmethod
    def rectangle(sw: Point, ne: Point):
        return Rectangle(sw, ne)

    @staticmethod
    def square(sw: Point, side: int):
        ne = sw.move(side, side)
        return Rectangle(sw, ne)

    # @staticmethod
    # def ellipse(center: Point, x_axis: int, y_axis: int):
    #    return Ellipse(center, x_axis, y_axis)

    # @staticmethod
    # def circle(center: Point, radius: int):
    #    return Ellipse(center, radius, radius)
