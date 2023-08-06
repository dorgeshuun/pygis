from dataclasses import dataclass

from PIL import Image


@dataclass
class Cached_Tile:
    img: Image
    ttl: int

    @staticmethod
    def create(img: Image):
        return Cached_Tile(img, 0)

    @property
    def increase_ttl(self):
        return Cached_Tile(self.img, self.ttl + 1)

    @property
    def reset_ttl(self):
        return Cached_Tile(self.img, 0)

    def __eq__(self, other):
        return self.ttl == other.ttl

    def __gt__(self, other):
        return self.ttl > other.ttl
