from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from pypond.PondFile import PondDoc, PondRender
from pypond.PondCommand import PondHeader
from pypond import PondScore
from backend.TasteComposer import MainComposer
from os import path


class PyPondWriter(QObject):
    file_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.render = PondRender()
        self.pond_doc = PondDoc()
        self.composer = MainComposer(path.join('backend', "data.json"))

    @pyqtSlot()
    def render_image(self):
        score = self.composer.compose()
        header = PondHeader()

        self.pond_doc.score = score
        self.pond_doc.header = header
        self.render.update(self.pond_doc.create_file())
        self.render.write()
        self.render.render()
        self.file_completed.emit()



