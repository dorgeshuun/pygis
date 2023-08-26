from dataclasses import dataclass
import math
from pyproj import Transformer
from enum import Enum

transformer = Transformer.from_crs(4326, 3857)


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
    def nw_lng_lat(self):
        n = 1 << self.z
        lon_deg = self.x / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * self.y / n)))
        lat_deg = math.degrees(lat_rad)
        return lat_deg, lon_deg

    @property
    def nw(self):
        x, y = transformer.transform(*self.nw_lng_lat)
        return int(x), int(y)

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
