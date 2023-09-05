from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QMouseEvent, QResizeEvent, QWheelEvent, QPainter, QCursor
from PyQt6.QtWidgets import QWidget, QMainWindow

from pygis.state import Context
from pygis.tile_cache import Tile_Cache
from pygis.point import Point


WIDTH = 800
HEIGHT = 600
ORIGIN_X = -100
ORIGIN_Y = -350
ZOOM = 3

POINT_RADIUS = 10


def is_left_button(e: QMouseEvent):
    return e.button().name == "LeftButton"


def get_pos_from_mouse_event(e: QMouseEvent):
    x = e.position().x()
    y = e.position().y()
    return int(x), int(y)


class MapWidget(QWidget):

    def paintEvent(self, _):
        painter = QPainter()
        painter.begin(self)

        london = Point.from_angular_coords(-0.1275, 51.507222)
        paris = Point.from_angular_coords(2.352222, 48.856667)
        berlin = Point.from_angular_coords(13.405, 52.52)
        capitals = [london, paris, berlin]

        points = []

        for tp, tile, _points in self.map.get_displayed_tiles(capitals):
            rect = QRect(tp.x, tp.y, tp.side, tp.side)

            t = self.tile_cache.get(tile)
            if t.fetched:
                img = t.img.toqimage()
                painter.drawImage(rect, img)
            else:
                painter.drawRect(rect)

            for dx, dy in _points:
                points.append((tp.x + dx, tp.y + dy))

        painter.setBrush(Qt.GlobalColor.red)
        for x, y in points:
            painter.drawEllipse(
                x - POINT_RADIUS // 2,
                y - POINT_RADIUS // 2,
                POINT_RADIUS,
                POINT_RADIUS
            )

        painter.end()

    def poll_tiles(self):
        self.update()
        self.tile_cache.update_many(self.map.displayed_tiles, self.update)

    def mousePressEvent(self, e: QMouseEvent):
        if is_left_button(e):
            x, y = get_pos_from_mouse_event(e)
            self.map.mouse_down(x, y)

    def mouseMoveEvent(self, e: QMouseEvent):
        x, y = get_pos_from_mouse_event(e)
        self.map.mouse_move(x, y)
        self.poll_tiles()

    def mouseReleaseEvent(self, e: QMouseEvent):
        self.poll_tiles()
        if is_left_button(e):
            self.map.mouse_up()

    def resizeEvent(self, e: QResizeEvent):
        w = e.size().width()
        h = e.size().height()
        self.map.resize(w, h)
        self.poll_tiles()

    def wheelEvent(self, e: QWheelEvent):
        screen_cursor_pos = QCursor.pos()
        window_cursor_pos = self.mapFromGlobal(screen_cursor_pos)
        x = window_cursor_pos.x()
        y = window_cursor_pos.y()

        if e.angleDelta().y() > 0:
            self.map.zoom_in(x, y)
        else:
            self.map.zoom_out(x, y)

        self.poll_tiles()
        self.update()

    def init_ui(self):
        self.resize(WIDTH, HEIGHT)
        self.move(100, 100)
        self.setWindowTitle("pygis")
        self.setStyleSheet('background-color:white')
        self.show()

    def __init__(self):
        super().__init__()

        self.tile_cache = Tile_Cache()
        self.map = Context(WIDTH, HEIGHT, ORIGIN_X, ORIGIN_Y, ZOOM)

        self.init_ui()
        self.poll_tiles()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        mapWidget = MapWidget()
        self.setCentralWidget(mapWidget)

        self.showMaximized()
        self.setWindowTitle("pygis")
        self.setStyleSheet("background-color:white")
