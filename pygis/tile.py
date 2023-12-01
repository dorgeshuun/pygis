from dataclasses import dataclass
import math
from enum import Enum

from pygis.point import Point
from pygis.shape import Shape


class Quarter(Enum):
    NW = 0
    NE = 1
    SW = 2
    SE = 3


@dataclass(frozen=True)
class Tile:
    x: int
    y: int
    z: int

    @property
    def nw(self):
        n = 1 << self.z
        lon_deg = self.x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * self.y / n)))
        lat_deg = math.degrees(lat_rad)
        return Point.from_angular_coords(lon_deg, lat_deg)

    @property
    def ne(self):
        return Tile(self.x + 1, self.y, self.z).nw

    @property
    def sw(self):
        return Tile(self.x, self.y + 1, self.z).nw

    @property
    def se(self):
        return Tile(self.x + 1, self.y + 1, self.z).nw

    @property
    def top_left(self):
        return Tile(self.x * 2, self.y * 2, self.z + 1)

    @property
    def top_right(self):
        return Tile(self.x * 2 + 1, self.y * 2, self.z + 1)

    @property
    def bottom_left(self):
        return Tile(self.x * 2, self.y * 2 + 1, self.z + 1)

    @property
    def bottom_right(self):
        return Tile(self.x * 2 + 1, self.y * 2 + 1, self.z + 1)

    @property
    def parent(self):
        t = Tile(self.x // 2, self.y // 2, self.z - 1)

        if self.x % 2 == 0 and self.y % 2 == 0:
            return t, Quarter.NW

        if self.x % 2 == 1 and self.y % 2 == 1:
            return t, Quarter.SE

        if self.x % 2 == 1 and self.y % 2 == 0:
            return t, Quarter.NE

        if self.x % 2 == 0 and self.y % 2 == 1:
            return t, Quarter.SW

        raise Exception()

    @property
    def rect(self):
        return Shape.rectangle(self.sw, self.ne)

    @staticmethod
    def from_point(lng: float, lat: float, zoom: int):
        lat_rad = math.radians(lat)
        n = 1 << zoom
        x = int((lng + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return Tile(x, y, zoom)

@dataclass
class Tile_Range:
    top_left: Tile
    bottom_right: Tile

    def __iter__(self):
        if self.top_left.z != self.bottom_right.z:
            raise ValueError()

        for i in range(self.top_left.x, self.bottom_right.x):
            for j in range(self.top_left.y, self.bottom_right.y):
                yield Tile(i, j, self.top_left.z)

    @property
    def zoom(self):
        return self.top_left.z

    @property
    def width(self):
        return self.bottom_right.x - self.top_left.x + 1

    @property
    def height(self):
        return self.bottom_right.y - self.top_left.y + 1
