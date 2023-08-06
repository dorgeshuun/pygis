from dataclasses import dataclass
import math

from pygis.tile import Tile, Tile_Range


@dataclass
class Tile_Position:
    x: int
    y: int
    side: int


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

    def resize(self, width: int, height: int):
        return Map(width, height, self.origin_x, self.origin_y, self.tile_side)

    def get_tile_origin(self, tile: Tile):
        x = self.origin_x + tile.x * self.tile_side
        y = self.origin_y + tile.y * self.tile_side
        return x, y

    @property
    def top_left_tile(self):
        i = -math.ceil(self.origin_x / self.tile_side)
        j = -math.ceil(self.origin_y / self.tile_side)
        return Tile(i, j, 0)

    @property
    def bottom_right_tile(self):
        i = math.ceil((self.width - self.origin_x) / self.tile_side)
        j = math.ceil((self.height - self.origin_y) / self.tile_side)
        return Tile(i, j, 0)

    @property
    def tiles(self):
        for t in Tile_Range(self.top_left_tile, self.bottom_right_tile):
            x, y = self.get_tile_origin(t)
            tile_position = Tile_Position(x, y, self.tile_side)
            yield tile_position, t
