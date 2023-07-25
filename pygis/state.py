from dataclasses import dataclass

from pygis.map import Map


@dataclass
class State:
    @property
    def map(self):
        raise NotImplementedError()

    @property
    def to_drag_state(self):
        raise NotImplementedError()

    @property
    def to_idle_state(self):
        raise NotImplementedError()

    def move_to(self, x: int, y: int):
        raise NotImplementedError()

    def from_what(width: int, height: int, origin_x: int, origin_y: int, tile_side: int):
        map = Map(width, height, origin_x, origin_y, tile_side)
        return IdleState(map)


@dataclass
class DragState(State):
    saved_map: Map
    click_x: int
    click_y: int
    drag_x: int
    drag_y: int

    @property
    def map(self):
        dx = self.drag_x - self.click_x
        dy = self.drag_y - self.click_y
        return self.saved_map.move(dx, dy)

    def move_to(self, x: int, y: int):
        return DragState(self.saved_map, self.click_x, self.click_y, x, y)

    def to_drag_state(self, x: int, y: int):
        return self

    def to_idle_state(self):
        return IdleState(self.map)


@dataclass
class IdleState(State):
    _map: Map

    @property
    def map(self):
        return self._map

    def move_to(self, x: int, y: int):
        return self

    def to_drag_state(self, x: int, y: int):
        return DragState(self.map, x, y, x, y)

    def to_idle_state(self):
        return self
