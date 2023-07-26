
import requests
from io import BytesIO
from PIL import Image, JpegImagePlugin

from PyQt6.QtCore import QRunnable, QObject, pyqtSignal

from pygis.map import Tile

TILE_URL = "http://localhost:8000/tile"


def fetch_tile(t: Tile):
    url = "{}?x={}&y={}&z={}".format(TILE_URL, t.x, t.y, t.z)
    r = requests.get(url)
    b_img = BytesIO(r.content)
    return Image.open(b_img)


class WorkerSignals(QObject):
    finished = pyqtSignal(Tile, JpegImagePlugin.JpegImageFile)


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @staticmethod
    def make(tile: Tile, on_success):
        worker = Worker(fetch_tile, tile)
        worker.signals.finished.connect(on_success)
        return worker

    def run(self):
        tile = self.args[0]
        img = self.fn(*self.args, **self.kwargs)
        self.signals.finished.emit(tile, img)
