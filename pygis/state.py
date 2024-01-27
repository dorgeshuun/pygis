from dataclasses import dataclass

from pygis.map import Map
from pygis.point import Point
from pygis.feature import Feature
from pygis.kdtree import KDTree
from pygis.feature import Attribute


@dataclass
class _Point:
    x: int
    y: int


@dataclass
class Point_Position:
    coords: Point
    attributes: list[Attribute]
    map_pos: _Point


class Context:
    def __init__(self, features: list[Feature], width: int, height: int):
        self.tree = KDTree.from_points(features)
        extent = self.tree.extent
        map = Map.from_extent(width, height, extent.sw, extent.ne)
        self.state = Idle_State(self, map)

    def transition_to(self, state):
        self.state = state

    @property
    def displayed_tiles(self):
        return self.state.map.tiles

    @property
    def displayed_tiles_position(self):
        for t in self.displayed_tiles:
            yield t, self.state.map.get_tile_position(t)

    @property
    def displayed_points(self):
        for t in self.displayed_tiles:
            for p in self.tree.intersect(t.rect):
                t_pos = self.state.map.get_tile_position(t)
                dx, dy = self.state.map.point_in_tile(t, p)
                yield Point_Position(p.point, p.attributes, _Point(t_pos.x + dx, t_pos.y + dy))

    def mouse_move(self, x: int, y: int):
        self.state.mouse_move(x, y)

    def mouse_down(self, x: int, y: int):
        self.state.mouse_down(x, y)

    def mouse_up(self):
        return self.state.mouse_up()

    def resize(self, width: int, height: int):
        self.state.resize(width, height)

    def zoom_in(self, x: int, y: int):
        self.state.zoom_in(x, y)

    def zoom_out(self, x: int, y: int):
        self.state.zoom_out(x, y)


@dataclass
class State:
    context: Context
    _map: Map

    @property
    def map(self):
        raise NotImplementedError()

    def mouse_move(self, x: int, y: int):
        raise NotImplementedError()

    def mouse_down(self, x: int, y: int):
        raise NotImplementedError()

    def mouse_up(self):
        raise NotImplementedError()

    def resize(self, width: int, height: int):
        raise NotImplementedError()

    def zoom_in(self, x: int, y: int):
        raise NotImplementedError()

    def zoom_out(self, x: int, y: int):
        raise NotImplementedError()

    def get_map_point(self, x: int, y: int):
        self._map.get_map_point(x, y)


@dataclass
class Idle_State(State):

    @property
    def map(self):
        return self._map

    def mouse_move(self, x: int, y: int):
        pass

    def mouse_down(self, x: int, y: int):
        next_state = Drag_State(self.context, self._map, x, y, x, y)
        self.context.transition_to(next_state)

    def mouse_up(self):
        raise NotImplementedError()

    def resize(self, width, height):
        self._map = self._map.resize(width, height)

    def zoom_in(self, x: int, y: int):
        self._map = self._map.zoom_in(x, y)

    def zoom_out(self, x: int, y: int):
        self._map = self._map.zoom_out(x, y)


@dataclass
class Drag_Payload:
    x: int
    y: int


@dataclass
class Drag(Drag_Payload):

    @property
    def dragged(self):
        return True


@dataclass
class No_Drag(Drag_Payload):

    @property
    def dragged(self):
        return False


@dataclass
class Drag_State(State):
    click_x: int
    click_y: int
    hover_x: int
    hover_y: int
    update_count: int = 0

    @property
    def map(self):
        dx = self.hover_x - self.click_x
        dy = self.hover_y - self.click_y
        return self._map.move(dx, dy)

    def mouse_move(self, x: int, y: int):
        self.hover_x = x
        self.hover_y = y
        self.update_count += 1

    def mouse_down(self):
        raise NotImplementedError()

    def mouse_up(self):
        next_state = Idle_State(self.context, self.map)
        self.context.transition_to(next_state)
        return No_Drag(self.click_x, self.click_y) if not self.update_count else Drag(self.hover_x, self.hover_y)

    def resize(self, width: int, height: int):
        raise NotImplementedError()

    def zoom_in(self, x: int, y: int):
        pass

    def zoom_out(self, x: int, y: int):
        pass
