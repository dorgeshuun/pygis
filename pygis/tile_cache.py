from concurrent import futures

import requests
from io import BytesIO
from PIL import Image

from pygis.map import Tile
from pygis.tile_result import Tile_Result

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

    def get(self, t: Tile):
        try:
            img = self.cached[t]
            return Tile_Result.ok(img)
        except KeyError:
            return Tile_Result.missing()

    def update_tile(self, tile, on_success):
        img = fetch_tile(tile)
        self.cached[tile] = img
        on_success()

    def update_many(self, tiles, on_success):
        for t in tiles:
            if t in self.cached:
                continue
            self.executor.submit(self.update_tile, t, on_success)
