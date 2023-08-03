from pygis.map import Tile

MAX_TILE_COUNT = 250


class Tile_Cache:
    def __init__(self):
        self.fetching = set()
        self.cached = {}
        self.priority = []

    def fetch_tiles(self, tiles: list[Tile]):
        for t in tiles:
            if t in self.cached:
                continue

            if t in self.fetching:
                continue

            self.fetching.add(t)

            yield t

    def clean_cache(self, tiles: list[Tile]):
        _tiles = set(tiles)
        old_tiles = [t for t in self.priority if t not in _tiles]
        self.priority = old_tiles[-MAX_TILE_COUNT:] + tiles

        priority = set(self.priority)
        self.cached = {k: v for k, v in self.cached.items() if k in priority}
        self.fetching = {t for t in self.fetching if t in priority}

    def poll_tiles(self, tiles: list[Tile]):
        yield from self.fetch_tiles(tiles)
        self.clean_cache(tiles)

    def get_tile(self, t: Tile):
        return self.cached.get(t)

    def update_tile(self, tile: Tile, data: str):
        self.cached[tile] = data
