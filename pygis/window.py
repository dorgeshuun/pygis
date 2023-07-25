from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QMouseEvent, QPainter, QColor, QPaintEvent
from PyQt6.QtCore import QRect, QPoint

from dataclasses import dataclass

from pygis.map import Map

SQR_X_START = 250
SQR_Y_START = 250

WIDTH = 800
HEIGHT = 600

TILE_SIDE = 100


@dataclass
class Tile:
    side = 100
    x: int
    y: int


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

        black = QColor.fromString("black")
        painter.setPen(black)

        map = Map(WIDTH, HEIGHT, self.sqr_x, self.sqr_y, TILE_SIDE)

        for point, tile in map.tiles.items():
            rect = QRect(point.x, point.y, TILE_SIDE, TILE_SIDE)

            label_pos_x = point.x + TILE_SIDE // 2
            label_pos_y = point.y + TILE_SIDE // 2
            label_pos = QPoint(label_pos_x, label_pos_y)

            label_txt = "{}, {}".format(tile.x, tile.y)

            painter.drawRect(rect)
            painter.drawText(label_pos, label_txt)

        painter.end()

    def handleMousePress(self, e: QMouseEvent):
        if not is_left_button(e):
            return

        self.isLeftButtonPressed = True

        x, y = get_pos_from_mouse_event(e)

        self.origin_click_x = x
        self.origin_click_y = y

        self.origin_sqr_x = self.sqr_x
        self.origin_sqr_y = self.sqr_y

    def handleMouseMove(self, e: QMouseEvent):
        if not self.isLeftButtonPressed:
            return

        x, y = get_pos_from_mouse_event(e)

        dx = x - self.origin_click_x
        dy = y - self.origin_click_y

        self.sqr_x = self.origin_sqr_x + dx
        self.sqr_y = self.origin_sqr_y + dy

        self.update()

    def handleMouseRelease(self, e: QMouseEvent):
        if is_left_button(e):
            self.isLeftButtonPressed = False

    def __init__(self):
        super().__init__()
        self.isLeftButtonPressed = False

        self.sqr_x = SQR_X_START
        self.sqr_y = SQR_Y_START

        self.resize(WIDTH, HEIGHT)
        self.setWindowTitle("pygis")
        self.setStyleSheet('background-color:white')

        self.mousePressEvent = self.handleMousePress
        self.mouseMoveEvent = self.handleMouseMove
        self.mouseReleaseEvent = self.handleMouseRelease

        self.show()
