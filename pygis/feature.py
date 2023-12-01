from dataclasses import dataclass

from pygis.point import Point

@dataclass
class Attribute:
    field: str
    value: str


@dataclass
class Feature:
    point: Point
    attributes: list[Attribute]

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y