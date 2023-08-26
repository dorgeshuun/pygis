from dataclasses import dataclass
import math

from pygis.tile import Tile, Tile_Range, Quarter

TILE_SIDE = 256


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
    zoom_lvl: int

    def move(self, dx: int, dy: int):
        x = self.origin_x + dx
        y = self.origin_y + dy
        return Map(self.width, self.height, x, y, self.zoom_lvl)

    def resize(self, width: int, height: int):
        return Map(width, height, self.origin_x, self.origin_y, self.zoom_lvl)

    def get_tile_origin(self, tile: Tile):
        x = self.origin_x + tile.x * TILE_SIDE
        y = self.origin_y + tile.y * TILE_SIDE
        return x, y

    def get_map_coord(self, x: int, y: int):
        i = (x - self.origin_x) // TILE_SIDE
        j = (y - self.origin_y) // TILE_SIDE

        x_pix = (x - self.origin_x) % TILE_SIDE
        y_pix = (y - self.origin_y) % TILE_SIDE

        return Tile(i, j, self.zoom_lvl).get_map_coord(x_pix, y_pix)

    def get_tile_from_coord(self, x: int, y: int):
        i = (x - self.origin_x) // TILE_SIDE
        j = (y - self.origin_y) // TILE_SIDE
        t = Tile(i, j, self.zoom_lvl)

        x_pix = (x - self.origin_x) % TILE_SIDE
        y_pix = (y - self.origin_y) % TILE_SIDE

        return t, x_pix, y_pix

    def get_child_tile(self, t: Tile, x: int, y: int):
        if x < TILE_SIDE // 2 and y < TILE_SIDE // 2:
            return t.top_left, x * 2, y * 2

        if x >= TILE_SIDE // 2 and y < TILE_SIDE // 2:
            return t.top_right, x * 2 - TILE_SIDE, y * 2

        if x < TILE_SIDE // 2 and y >= TILE_SIDE // 2:
            return t.bottom_left, x * 2, y * 2 - TILE_SIDE

        if x >= TILE_SIDE // 2 and y >= TILE_SIDE // 2:
            return t.bottom_right, x * 2 - TILE_SIDE, y * 2 - TILE_SIDE

        raise Exception()

    def get_parent_tile(self, t: Tile, x: int, y: int):
        parent, quarter = t.parent

        match quarter:
            case Quarter.NW:
                return parent, x // 2, y // 2

            case Quarter.SE:
                return parent, (x + TILE_SIDE) // 2, (y + TILE_SIDE) // 2

            case Quarter.NE:
                return parent, (x + TILE_SIDE) // 2, y // 2

            case Quarter.SW:
                return parent, x // 2, (y + TILE_SIDE) // 2

    def zoom_in(self, x: int, y: int):
        t1, t1_x, t1_y = self.get_tile_from_coord(x, y)
        t2, t2_x, t2_y = self.get_child_tile(t1, t1_x, t1_y)
        t3 = Tile(t1.x, t1.y, t1.z + 1)

        dx = t2_x + TILE_SIDE - t1_x + (t2.x - t3.x - 1) * TILE_SIDE
        dy = t2_y + TILE_SIDE - t1_y + (t2.y - t3.y - 1) * TILE_SIDE

        return Map(
            self.width,
            self.height,
            self.origin_x - dx,
            self.origin_y - dy,
            self.zoom_lvl + 1
        )

    def zoom_out(self, x: int, y: int):
        t1, t1_x, t1_y = self.get_tile_from_coord(x, y)
        t2, t2_x, t2_y = self.get_parent_tile(t1, t1_x, t1_y)
        t3 = Tile(t1.x, t1.y, t1.z - 1)

        dx = t2_x + TILE_SIDE - t1_x + (t2.x - t3.x - 1) * TILE_SIDE
        dy = t2_y + TILE_SIDE - t1_y + (t2.y - t3.y - 1) * TILE_SIDE

        return Map(
            self.width,
            self.height,
            self.origin_x - dx,
            self.origin_y - dy,
            self.zoom_lvl - 1
        )

    @property
    def top_left_tile(self):
        i = -math.ceil(self.origin_x / TILE_SIDE)
        j = -math.ceil(self.origin_y / TILE_SIDE)
        return Tile(i, j, self.zoom_lvl)

    @property
    def bottom_right_tile(self):
        i = math.ceil((self.width - self.origin_x) / TILE_SIDE)
        j = math.ceil((self.height - self.origin_y) / TILE_SIDE)
        return Tile(i, j, self.zoom_lvl)

    @property
    def tiles(self):
        for t in Tile_Range(self.top_left_tile, self.bottom_right_tile):
            x, y = self.get_tile_origin(t)
            tile_position = Tile_Position(x, y, TILE_SIDE)
            yield tile_position, t
