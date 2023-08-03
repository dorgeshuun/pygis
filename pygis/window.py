from PyQt6.QtCore import QRect, QPoint, QThreadPool
from PyQt6.QtGui import QMouseEvent, QPainter, QPaintEvent, QImage
from PyQt6.QtWidgets import QWidget

from PIL import JpegImagePlugin

from pygis.state import State
from pygis.map import Tile
from pygis.tile_cache import Tile_Cache
from pygis.worker import Worker

WIDTH = 800
HEIGHT = 600
ORIGIN_X = 250
ORIGIN_Y = 250
TILE_SIDE = 100


def is_left_button(e: QMouseEvent):
    return e.button().name == "LeftButton"


def get_pos_from_mouse_event(e: QMouseEvent):
    x = e.position().x()
    y = e.position().y()
    return int(x), int(y)


def draw_tile(painter: QPainter, x: int, y: int, img: QImage | None):
    rect = QRect(x, y, TILE_SIDE, TILE_SIDE)
    if img is None:
        painter.drawRect(rect)
    else:
        painter.drawImage(rect, img)


def draw_label(painter: QPainter, x: int, y: int, tile):
    pos = QPoint(x + TILE_SIDE // 2, y + TILE_SIDE // 2)
    txt = "{}, {}".format(tile.x, tile.y)
    painter.drawText(pos, txt)


class MyWindow(QWidget):

    def paintEvent(self, _: QPaintEvent):
        painter = QPainter()
        painter.begin(self)

        for point, tile in self.state.displayed_tiles:
            img = self.tile_cache.get_tile(tile)
            draw_tile(painter, point.x, point.y, img)
            draw_label(painter, point.x, point.y, tile)

        painter.end()

    def on_success(self, tile: Tile, img: JpegImagePlugin.JpegImageFile):
        self.tile_cache.update_tile(tile, img.toqimage())
        self.update()

    def poll_tiles(self):
        displayed_tiles = [t for _, t in self.state.displayed_tiles]
        missing_tiles = self.tile_cache.poll_tiles(displayed_tiles)
        for tile in missing_tiles:
            worker = Worker.make(tile, self.on_success)
            self.thread_pool.start(worker)

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
