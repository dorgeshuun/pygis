from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QMouseEvent, QPainter, QColor, QPaintEvent
from PyQt6.QtCore import QRect, QPoint

import math
from dataclasses import dataclass

SQR_X_START = 250
SQR_Y_START = 250

WIDTH = 800
HEIGHT = 600


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

        imin = -math.ceil(self.sqr_x / Tile.side)
        jmin = -math.ceil(self.sqr_y / Tile.side)

        imax = math.ceil((WIDTH - self.sqr_x) / Tile.side)
        jmax = math.ceil((HEIGHT - self.sqr_y) / Tile.side)

        for i in range(imin, imax):
            for j in range(jmin, jmax):
                t = Tile(i, j)

                x = self.sqr_x + i * t.side
                y = self.sqr_y + j * t.side

                rect = QRect(x, y, t.side, t.side)
                painter.drawRect(rect)

                label_pos = QPoint(x + t.side // 2, y + t.side // 2)
                label_txt = "{}, {}".format(i, j)
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
