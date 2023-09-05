from dataclasses import dataclass

from pygis.map import Map
from pygis.point import Point


class Context:
    def __init__(
        self,
        width: int,
        height: int,
        origin_x: int,
        origin_y: int,
        zoom: int
    ):
        map = Map(width, height, origin_x, origin_y, zoom)
        self.state = Idle_State(self, map)

    def transition_to(self, state):
        self.state = state

    @property
    def displayed_tiles(self):
        yield from (t for _tile_pos, t, _ in self.state.map.tiles([]))

    def get_displayed_tiles(self, points: list[Point]):
        return self.state.map.tiles(points)

    def mouse_move(self, x: int, y: int):
        self.state.mouse_move(x, y)

    def mouse_down(self, x: int, y: int):
        self.state.mouse_down(x, y)

    def mouse_up(self):
        self.state.mouse_up()

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
class Drag_State(State):
    click_x: int
    click_y: int
    hover_x: int
    hover_y: int

    @property
    def map(self):
        dx = self.hover_x - self.click_x
        dy = self.hover_y - self.click_y
        return self._map.move(dx, dy)

    def mouse_move(self, x: int, y: int):
        self.hover_x = x
        self.hover_y = y

    def mouse_down(self):
        raise NotImplementedError()

    def mouse_up(self):
        next_state = Idle_State(self.context, self.map)
        self.context.transition_to(next_state)

    def resize(self, width: int, height: int):
        raise NotImplementedError()

    def zoom_in(self, x: int, y: int):
        pass

    def zoom_out(self, x: int, y: int):
        pass
