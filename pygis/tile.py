from dataclasses import dataclass


@dataclass(frozen=True)
class Tile:
    x: int
    y: int
    z: int


@dataclass
class Tile_Range:
    top_left: Tile
    bottom_right: Tile

    def __iter__(self):
        for i in range(self.top_left.x, self.bottom_right.x):
            for j in range(self.top_left.y, self.bottom_right.y):
                yield Tile(i, j, 0)
