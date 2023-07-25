from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QMouseEvent, QPainter, QColor, QPaintEvent
from PyQt6.QtCore import QRect, QPoint

from pygis.state import State

SQR_X_START = 250
SQR_Y_START = 250

WIDTH = 800
HEIGHT = 600

TILE_SIDE = 100


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

        for point, tile in self.state.map.tiles.items():
            rect = QRect(point.x, point.y, TILE_SIDE, TILE_SIDE)

            label_pos_x = point.x + TILE_SIDE // 2
            label_pos_y = point.y + TILE_SIDE // 2
            label_pos = QPoint(label_pos_x, label_pos_y)

            label_txt = "{}, {}".format(tile.x, tile.y)

            painter.drawRect(rect)
            painter.drawText(label_pos, label_txt)

        painter.end()

    def handleMousePress(self, e: QMouseEvent):
        if is_left_button(e):
            x, y = get_pos_from_mouse_event(e)
            self.state = self.state.to_drag_state(x, y)

    def handleMouseMove(self, e: QMouseEvent):
        x, y = get_pos_from_mouse_event(e)
        self.state = self.state.move_to(x, y)
        self.update()

    def handleMouseRelease(self, e: QMouseEvent):
        if is_left_button(e):
            self.state = self.state.to_idle_state()

    def __init__(self):
        super().__init__()
        self.isLeftButtonPressed = False

        self.resize(WIDTH, HEIGHT)
        self.setWindowTitle("pygis")
        self.setStyleSheet('background-color:white')

        self.mousePressEvent = self.handleMousePress
        self.mouseMoveEvent = self.handleMouseMove
        self.mouseReleaseEvent = self.handleMouseRelease

        self.state = State.from_what(
            WIDTH, HEIGHT, SQR_X_START, SQR_Y_START, TILE_SIDE)

        self.show()
