from PyQt6 import QtCore, QtWidgets

from pygis.feature import Feature


class IdentifyWigdet(QtWidgets.QWidget):

    def __init__(self, window_collection: set[QtWidgets.QWidget], feature: Feature):
        super().__init__()
        self.window_collection = window_collection
        self.setWindowFlag(QtCore.Qt.WindowType.Tool)
        self.move(100, 100)

        form = QtWidgets.QFormLayout(self)
        right_align = QtCore.Qt.AlignmentFlag.AlignRight
        form.setLabelAlignment(right_align)
        
        for i in feature.attributes:
            value = QtWidgets.QLabel(i.value)
            form.addRow(i.field, value)

    def closeEvent(self, event):
        self.window_collection.remove(self)