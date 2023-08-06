from concurrent import futures

import requests
from io import BytesIO
from PIL import Image

from pygis.map import Tile
from pygis.tile_result import Tile_Result
from pygis.cached_tile import Cached_Tile

MAX_TILE_COUNT = 250

TILE_URL = "http://localhost:8000/tile"


def fetch_tile(t: Tile):
    url = "{}?x={}&y={}&z={}".format(TILE_URL, t.x, t.y, t.z)
    r = requests.get(url)
    b_img = BytesIO(r.content)
    return Image.open(b_img)


class Tile_Cache:
    def __init__(self):
        self.executor = futures.ThreadPoolExecutor()
        self.cached = {}
        self.fetching = set()

    def get(self, t: Tile):
        try:
            img = self.cached[t].img
            return Tile_Result.ok(img)
        except KeyError:
            return Tile_Result.missing()

    def update_all(self):
        ttl_increased = ((k, v.increase_ttl) for k, v in self.cached.items())
        ttl_ordered = sorted(ttl_increased, key=lambda x: x[1])
        sliced = ttl_ordered[:MAX_TILE_COUNT]
        self.cached = {t: ct for t, ct in sliced}

    def update_tile(self, tile, on_success):
        img = fetch_tile(tile)
        self.update_all()
        self.cached[tile] = Cached_Tile.create(img)
        self.fetching.remove(tile)
        on_success()

    def update_many(self, tiles, on_success):
        for t in tiles:
            if t in self.cached:
                self.cached[t] = self.cached[t].reset_ttl
                continue

            if t in self.fetching:
                continue

            self.fetching.add(t)
            self.executor.submit(self.update_tile, t, on_success)
