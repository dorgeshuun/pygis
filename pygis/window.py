from PyQt6.QtCore import QRect, QPoint
from PyQt6.QtGui import QMouseEvent, QResizeEvent, QPainter
from PyQt6.QtWidgets import QWidget

from pygis.state import Context
from pygis.tile_cache import Tile_Cache


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


class MyWindow(QWidget):

    def paintEvent(self, _):
        painter = QPainter()
        painter.begin(self)

        for tp, tile in self.map.displayed_tiles:
            rect = QRect(tp.x, tp.y, tp.side, tp.side)

            t = self.tile_cache.get(tile)
            if t.fetched:
                img = t.img.toqimage()
                painter.drawImage(rect, img)
            else:
                painter.drawRect(rect)

            pos = QPoint(tp.x + tp.side // 2, tp.y + tp.side // 2)
            txt = "{}, {}".format(tile.x, tile.y)
            painter.drawText(pos, txt)

        painter.end()

    def poll_tiles(self):
        self.update()
        tiles = (t for _, t in self.map.displayed_tiles)
        self.tile_cache.update_many(tiles, self.update)

    def mousePressEvent(self, e: QMouseEvent):
        if is_left_button(e):
            x, y = get_pos_from_mouse_event(e)
            self.map.mouse_down(x, y)

    def mouseMoveEvent(self, e: QMouseEvent):
        x, y = get_pos_from_mouse_event(e)
        self.map.mouse_move(x, y)
        self.update()

    def mouseReleaseEvent(self, e: QMouseEvent):
        self.poll_tiles()
        if is_left_button(e):
            self.map.mouse_up()

    def resizeEvent(self, e: QResizeEvent):
        w = e.size().width()
        h = e.size().height()
        self.map.resize(w, h)
        self.poll_tiles()

    def init_ui(self):
        self.resize(WIDTH, HEIGHT)
        self.move(100, 100)
        self.setWindowTitle("pygis")
        self.setStyleSheet('background-color:white')
        self.show()

    def __init__(self):
        super().__init__()

        self.tile_cache = Tile_Cache()
        self.map = Context(WIDTH, HEIGHT, ORIGIN_X, ORIGIN_Y, TILE_SIDE)

        self.init_ui()
        self.poll_tiles()
