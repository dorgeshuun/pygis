from dataclasses import dataclass

from pygis.point import Point
from pygis.tile import Tile


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

    @staticmethod
    def from_points(sw: Point, ne: Point, zoom: int):
        nw_tile = Tile.from_point(sw.lng, ne.lat, zoom)
        se_tile = Tile.from_point(ne.lng, sw.lat, zoom)
        return Tile_Range(nw_tile, se_tile)

    @property
    def zoom(self):
        return self.top_left.z

    @property
    def width(self):
        return self.bottom_right.x - self.top_left.x + 1

    @property
    def height(self):
        return self.bottom_right.y - self.top_left.y + 1
