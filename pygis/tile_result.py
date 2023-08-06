from dataclasses import dataclass

from PIL import Image


@dataclass
class Tile_Result:

    @property
    def fetched(self):
        raise NotImplementedError()

    @property
    def img(self):
        raise NotImplementedError()

    def ok(img: Image):
        return Tile_Result_Ok(img)

    def missing():
        return Tile_Result_Missing()


@dataclass
class Tile_Result_Ok(Tile_Result):
    _img: Image

    @property
    def fetched(self):
        return True

    @property
    def img(self):
        return self._img


@dataclass
class Tile_Result_Missing(Tile_Result):

    @property
    def fetched(self):
        return False

    @property
    def img(self):
        raise NotImplementedError()
