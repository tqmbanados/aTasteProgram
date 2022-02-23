from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from pypond.PondFile import PondDoc, PondRender
from pypond.PondCommand import PondHeader, PondPaper
from pypond import PondScore
from backend.TasteComposer import MainComposer
from os import path


class PyPondWriter(QObject):
    file_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.render = PondRender()
        self.pond_doc = PondDoc()
        self.main_document = MainDoc()
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

    @pyqtSlot()
    def write_score(self):
        self.main_document.document.score = self.composer.render_complete_score()
        self.render.update(self.main_document.create_file())
        self.render.write()


class MainDoc:
    def __init__(self):
        self.document = PondDoc()
        self.custom_commands = {}
        self.init_doc()

    def init_doc(self):
        header = PondHeader(title='"A Taste of Control"',
                            composer='"Tom Bañados"')
        paper = PondPaper()
        paper.update_margins({"top-margin": 10,
                              "left-margin": 15,
                              "right-margin": 15})
        self.document.paper = paper
        self.document.header = header
        for name, function in self.custom_commands:
            self.document.add_function(name, function)

    def create_file(self):
        return self.document.create_file()
