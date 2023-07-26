from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QMouseEvent, QPainter, QPaintEvent
from PyQt6.QtCore import QRect, QPoint, QThreadPool, QRunnable, QObject, pyqtSignal

import requests
from io import BytesIO
from PIL import Image, JpegImagePlugin

from pygis.state import State
from pygis.map import Tile
from pygis.tile_cache import Tile_Cache

SQR_X_START = 250
SQR_Y_START = 250

WIDTH = 800
HEIGHT = 600

TILE_SIDE = 100


class WorkerSignals(QObject):
    finished = pyqtSignal(Tile, JpegImagePlugin.JpegImageFile)


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        tile = self.args[0]
        img = self.fn(*self.args, **self.kwargs)
        self.signals.finished.emit(tile, img)


def is_left_button(e: QMouseEvent):
    return e.button().name == "LeftButton"


def get_pos_from_mouse_event(e: QMouseEvent):
    x = e.position().x()
    y = e.position().y()
    return int(x), int(y)


class MyWindow(QWidget):
    def paintEvent(self, _: QPaintEvent):
        painter = QPainter()
        painter.begin(self)

        for point, tile in self.state.map.tiles.items():
            rect = QRect(point.x, point.y, TILE_SIDE, TILE_SIDE)

            img = self.displayed_tiles.get(tile)

            if img is None:
                painter.drawRect(rect)
            else:
                painter.drawImage(rect, img.toqimage())

            label_pos_x = point.x + TILE_SIDE // 2
            label_pos_y = point.y + TILE_SIDE // 2
            label_pos = QPoint(label_pos_x, label_pos_y)

            label_txt = "{}, {}".format(tile.x, tile.y)

            painter.drawText(label_pos, label_txt)

        painter.end()

    def mousePressEvent(self, e: QMouseEvent):
        if is_left_button(e):
            x, y = get_pos_from_mouse_event(e)
            self.state = self.state.to_drag_state(x, y)

    def fetch_tile(self, tile: Tile):
        r = requests.get(
            "http://localhost:8000/tile?x={}&y={}&z={}".format(tile.x, tile.y, tile.z))
        return Image.open((BytesIO(r.content)))

    def on_success(self, tile: Tile, img: JpegImagePlugin.JpegImageFile):
        self.tile_cache.update_tile(tile, img)
        self.displayed_tiles[tile] = img
        self.update()

    def enqueue_tile(self, tile: Tile):
        worker = Worker(self.fetch_tile, tile)
        worker.signals.finished.connect(self.on_success)
        self.thread_pool.start(worker)

    def mouseMoveEvent(self, e: QMouseEvent):
        x, y = get_pos_from_mouse_event(e)
        self.state = self.state.move_to(x, y)

        self.update()

    def mouseReleaseEvent(self, e: QMouseEvent):
        if is_left_button(e):
            self.state = self.state.to_idle_state()

        tiles_in_extent = list(self.state.map.tiles.values())
        for missing_tile in self.tile_cache.request_tiles(tiles_in_extent):
            self.enqueue_tile(missing_tile)

    def __init__(self):
        super().__init__()
        self.isLeftButtonPressed = False

        self.tile_cache = Tile_Cache()
        self.displayed_tiles = {}
        self.thread_pool = QThreadPool()

        self.resize(WIDTH, HEIGHT)
        self.move(100, 100)
        self.setWindowTitle("pygis")
        self.setStyleSheet('background-color:white')

        self.state = State.init(
            WIDTH, HEIGHT, SQR_X_START, SQR_Y_START, TILE_SIDE)

        self.show()
