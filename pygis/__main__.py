import sys
import click
from typing import TextIO
from PyQt6.QtWidgets import QApplication, QMainWindow

from pygis.map_widget import MapWidget


@click.command()
@click.argument('file', type=click.File('r'))
def main(file: TextIO):
    app = QApplication([])

    window = QMainWindow()
    window.showMaximized()
    window.setWindowTitle("pygis")
    window.setStyleSheet("background-color:white")

    map_widget = MapWidget(file)
    window.setCentralWidget(map_widget)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
