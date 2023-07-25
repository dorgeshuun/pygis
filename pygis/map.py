from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass
class Tile:
    x: int
    y: int


@dataclass
class Map:
    width: int
    height: int
    origin_x: int
    origin_y: int
    tile_side: int

    def move(self, dx: int, dy: int):
        x = self.origin_x + dx
        y = self.origin_y + dy
        return Map(self.width, self.height, x, y, self.tile_side)

    @property
    def tiles(self):
        imin = -math.ceil(self.origin_x / self.tile_side)
        jmin = -math.ceil(self.origin_y / self.tile_side)

        imax = math.ceil((self.width - self.origin_x) / self.tile_side)
        jmax = math.ceil((self.height - self.origin_y) / self.tile_side)

        result = {}

        for i in range(imin, imax):
            for j in range(jmin, jmax):
                x = self.origin_x + i * self.tile_side
                y = self.origin_y + j * self.tile_side

                p = Point(x, y)
                t = Tile(i, j)

                result[p] = t

        return result
