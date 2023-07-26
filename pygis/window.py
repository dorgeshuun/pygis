import requests
from io import BytesIO
from PIL import Image, JpegImagePlugin

from PyQt6.QtCore import QRect, QPoint, QThreadPool
from PyQt6.QtGui import QMouseEvent, QPainter, QPaintEvent
from PyQt6.QtWidgets import QWidget

from pygis.state import State
from pygis.map import Tile
from pygis.tile_cache import Tile_Cache
from pygis.worker import Worker

WIDTH = 800
HEIGHT = 600
ORIGIN_X = 250
ORIGIN_Y = 250
TILE_SIDE = 100
TILE_URL = "http://localhost:8000/tile"


def is_left_button(e: QMouseEvent):
    return e.button().name == "LeftButton"


def get_pos_from_mouse_event(e: QMouseEvent):
    x = e.position().x()
    y = e.position().y()
    return int(x), int(y)


class MyWindow(QWidget):
    def draw_tile(self, painter: QPainter, x: int, y: int, tile: Tile):
        rect = QRect(x, y, TILE_SIDE, TILE_SIDE)
        img = self.tile_cache.get_tile(tile)

        if img is None:
            painter.drawRect(rect)
        else:
            painter.drawImage(rect, img.toqimage())

    def draw_label(self, painter: QPainter, x: int, y: int, tile):
        pos = QPoint(x + TILE_SIDE // 2, y + TILE_SIDE // 2)
        txt = "{}, {}".format(tile.x, tile.y)
        painter.drawText(pos, txt)

    def paintEvent(self, _: QPaintEvent):
        painter = QPainter()
        painter.begin(self)

        for point, tile in self.state.displayed_tiles.items():
            self.draw_tile(painter, point.x, point.y, tile)
            self.draw_label(painter, point.x, point.y, tile)

        painter.end()

    def fetch_tile(self, t: Tile):
        url = "{}?x={}&y={}&z={}".format(TILE_URL, t.x, t.y, t.z)
        r = requests.get(url)
        b_img = BytesIO(r.content)
        return Image.open(b_img)

    def on_success(self, tile: Tile, img: JpegImagePlugin.JpegImageFile):
        self.tile_cache.update_tile(tile, img)
        self.update()

    def enqueue_tile(self, tile: Tile):
        worker = Worker(self.fetch_tile, tile)
        worker.signals.finished.connect(self.on_success)
        self.thread_pool.start(worker)

    def poll_tiles(self):
        displayed_tiles = list(self.state.displayed_tiles.values())
        missing_tiles = self.tile_cache.poll_tiles(displayed_tiles)
        for tile in missing_tiles:
            self.enqueue_tile(tile)

    def mousePressEvent(self, e: QMouseEvent):
        if is_left_button(e):
            x, y = get_pos_from_mouse_event(e)
            self.state = self.state.to_drag_state(x, y)

    def mouseMoveEvent(self, e: QMouseEvent):
        x, y = get_pos_from_mouse_event(e)
        self.state = self.state.move_to(x, y)
        self.update()

    def mouseReleaseEvent(self, e: QMouseEvent):
        self.poll_tiles()
        if is_left_button(e):
            self.state = self.state.to_idle_state()

    def init_ui(self):
        self.resize(WIDTH, HEIGHT)
        self.move(100, 100)
        self.setWindowTitle("pygis")
        self.setStyleSheet('background-color:white')
        self.show()

    def __init__(self):
        super().__init__()

        self.thread_pool = QThreadPool()
        self.tile_cache = Tile_Cache()
        self.state = State.init(WIDTH, HEIGHT, ORIGIN_X, ORIGIN_Y, TILE_SIDE)

        self.init_ui()
        self.poll_tiles()
