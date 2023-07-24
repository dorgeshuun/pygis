from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QMouseEvent, QPainter, QColor, QPaintEvent
from PyQt6.QtCore import QRect

SQR_X_START = 250
SQR_Y_START = 250


def is_left_button(e: QMouseEvent):
    return e.button().name == "LeftButton"


def get_pos_from_mouse_event(e: QMouseEvent):
    x = e.position().x()
    y = e.position().y()
    return int(x), int(y)


class MyWindow(QWidget):
    def paintEvent(self, _: QPaintEvent):
        red = QColor.fromString("red")
        rect = QRect(self.sqr_x, self.sqr_y, 100, 100)
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(red)
        painter.drawRect(rect)
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
        if is_left_button(e) and self.isLeftButtonPressed:
            self.isLeftButtonPressed = False

    def __init__(self):
        super().__init__()
        self.isLeftButtonPressed = False

        self.sqr_x = SQR_X_START
        self.sqr_y = SQR_Y_START

        self.resize(800, 600)
        self.setWindowTitle("pygis")
        self.setStyleSheet('background-color:white')

        self.mousePressEvent = self.handleMousePress
        self.mouseMoveEvent = self.handleMouseMove
        self.mouseReleaseEvent = self.handleMouseRelease

        self.show()
