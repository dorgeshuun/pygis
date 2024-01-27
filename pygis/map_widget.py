import math

from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QMouseEvent, QResizeEvent, QWheelEvent, QPainter, QCursor
from PyQt6.QtWidgets import QWidget

from pygis.state import Context
from pygis.tile_cache import Tile_Cache
from pygis.feature import Feature
from pygis.identify_widget import IdentifyWigdet

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

        for tile, position in self.map.displayed_tiles_position:
            rect = QRect(position.x, position.y, position.side, position.side)

            t = self.tile_cache.get(tile)
            if t.fetched:
                img = t.img.toqimage()
                painter.drawImage(rect, img)
            else:
                painter.drawRect(rect)

        painter.setBrush(Qt.GlobalColor.red)
        for p in self.map.displayed_points:
            x = p.map_pos.x - POINT_RADIUS // 2
            y = p.map_pos.y - POINT_RADIUS // 2
            r = POINT_RADIUS
            painter.drawEllipse(x, y, r, r)

        painter.end()

    def poll_tiles(self):
        self.update()
        self.tile_cache.update_many(self.map.displayed_tiles, self.update)

    def mousePressEvent(self, e: QMouseEvent):
        if is_left_button(e):
            x, y = get_pos_from_mouse_event(e)
            self.map.mouse_down(x, y)

    def get_pts_at_coords(self, click_x: int, click_y: int):
        for p in self.map.displayed_points:
            dx = p.map_pos.x - click_x
            dy = p.map_pos.y - click_y

            dist = math.sqrt(dx * dx + dy * dy)

            if dist * 2 < POINT_RADIUS:
                yield p

    def mouseMoveEvent(self, e: QMouseEvent):
        x, y = get_pos_from_mouse_event(e)
        self.map.mouse_move(x, y)
        self.poll_tiles()

    def create_secondary_window(self, feature: Feature):
        w = IdentifyWigdet(self.secondary_windows, feature)
        self.secondary_windows.add(w)
        w.show()

    def mouseReleaseEvent(self, e: QMouseEvent):
        if not is_left_button(e):
            return

        payload = self.map.mouse_up()

        if payload.dragged:
            return

        selected = None
        for p in self.get_pts_at_coords(payload.x, payload.y):
            selected = p

        if not selected:
            return

        self.create_secondary_window(selected)

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

    def __init__(self, width: int, height: int, features: list[Feature]):
        super().__init__()
        self.secondary_windows = set()
        self.tile_cache = Tile_Cache()
        self.map = Context(features, width, height)
        self.poll_tiles()
