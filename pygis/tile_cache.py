import threading
import queue

import requests
from io import BytesIO
from PIL import Image

from pygis.map import Tile
from pygis.tile_result import Tile_Result
from pygis.cached_tile import Cached_Tile

MAX_TILE_COUNT = 250

TILE_URL = "https://tile.openstreetmap.org"


def fetch_tile(t: Tile):
    url = "{}/{}/{}/{}.png".format(TILE_URL, t.z, t.x, t.y)
    r = requests.get(url, headers={"user-agent": "pygis/0.1"}, timeout=1)
    b_img = BytesIO(r.content)
    return Image.open(b_img)


class Tile_Cache:
    def __init__(self, on_success):
        self.cached = {}
        self.fetching = set()
        self.fetching_queue = queue.Queue()
        self.on_success = on_success

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

    def worker(self):
        while True:
            t = self.fetching_queue.get()
            img = fetch_tile(t)
            self.update_all()
            self.cached[t] = Cached_Tile.create(img)
            try:
                self.fetching.remove(t)
            except KeyError:
                pass
            self.on_success()

    def start(self):
        threading.Thread(target=self.worker, daemon=True).start()

    def clear_fetching(self):
        self.fetching.clear()
        while not self.fetching_queue.empty():
            self.fetching_queue.get()

    def update_tile(self, t: Tile):
        self.cached[t] = self.cached[t].reset_ttl

    def submit_tile(self, t: Tile):
        self.fetching.add(t)
        self.fetching_queue.put(t)

    def update_many(self, tiles):
        '''called when map extent changed'''
        self.clear_fetching()
        for t in tiles:

            if t in self.cached:
                self.update_tile(t)
                continue

            if t in self.fetching:
                continue

            self.submit_tile(t)
