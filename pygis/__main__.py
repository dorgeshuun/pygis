import sys
import click
from typing import TextIO
from PyQt6.QtWidgets import QApplication, QMainWindow

from pygis.point import Point
from pygis.feature import Feature, Attribute
from pygis.map_widget import MapWidget

WIDTH = 800
HEIGHT = 600


def get_pts_from_file(file: TextIO):
    field_names = file.readline().strip().split(";")[2:]

    for line in file:
        fields = line.strip().split(";")
        point = Point.from_angular_coords(float(fields[0]), float(fields[1]))
        attributes = [Attribute(field_names[i], x)
                      for i, x in enumerate(fields[2:])]
        yield Feature(point, attributes)


@click.command()
@click.argument('file', type=click.File('r'), default=sys.stdin)
def main(file: TextIO):
    app = QApplication([])

    window = QMainWindow()
    window.resize(WIDTH, HEIGHT)
    window.setWindowTitle("pygis")
    window.setStyleSheet("background-color:white")
    map_widget = MapWidget(WIDTH, HEIGHT, get_pts_from_file(file))
    window.setCentralWidget(map_widget)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
