import sys
from PyQt6.QtWidgets import QApplication

from pygis.window import MyWindow

if __name__ == "__main__":
    app = QApplication([])
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
