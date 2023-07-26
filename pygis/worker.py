from PyQt6.QtCore import QRunnable, QObject, pyqtSignal
from PIL import JpegImagePlugin

from pygis.map import Tile


class WorkerSignals(QObject):
    finished = pyqtSignal(Tile, JpegImagePlugin.JpegImageFile)


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        tile = self.args[0]
        img = self.fn(*self.args, **self.kwargs)
        self.signals.finished.emit(tile, img)
