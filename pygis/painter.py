from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QRect, Qt

from pygis.state import Point_Position
from pygis.map import Tile_Position
from pygis.tile_cache import Tile_Cache
from pygis.tile_result import Tile_Result


class Painter:
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.painter = QPainter()

    def __enter__(self):
        self.painter.begin(self.widget)
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.painter.end()

    def draw_tile(self, rect: QRect, tile: Tile_Result):
        if tile.fetched:
            img = tile.img.toqimage()
            self.painter.drawImage(rect, img)
        else:
            self.painter.drawRect(rect)

    def paint_tiles(self, tiles: list[Tile_Position], tile_cache: Tile_Cache):
        for tile, pos in tiles:
            rect = QRect(pos.x, pos.y, pos.side, pos.side)
            t = tile_cache.get(tile)
            self.draw_tile(rect, t)

    def paint_points(self, points: list[Point_Position], radius: int):
        self.painter.setBrush(Qt.GlobalColor.red)
        for p in points:
            x = p.map_pos.x - radius // 2
            y = p.map_pos.y - radius // 2
            self.painter.drawEllipse(x, y, radius, radius)
