from dataclasses import dataclass
from pyproj import Transformer
import math

projecter = Transformer.from_crs(4326, 3857, always_xy=True)
unprojecter = Transformer.from_crs(3857, 4326, always_xy=True)


@dataclass
class Point:
    lng: float
    lat: float
    x: int
    y: int

    @staticmethod
    def from_angular_coords(lng: float, lat: float):
        fx, fy = projecter.transform(lng, lat)

        x = math.floor(fx)
        y = math.floor(fy)

        return Point(lng, lat, x, y)

    @staticmethod
    def from_planar_coords(x: int, y: int):
        lng, lat = unprojecter.transform(x, y)
        return Point(lng, lat, x, y)
