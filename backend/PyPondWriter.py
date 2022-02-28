from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from pypond.PondFile import PondDoc, PondRender
from pypond.PondCommand import PondHeader, PondPaper
from pypond import PondScore
from backend.pypond_extensions import LilypondScripts
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
        self.init_doc()
        self.advance_bar = False

    def init_doc(self):
        self.pond_doc.header = PondHeader()
        for name, function in LilypondScripts.commands_dict().items():
            self.pond_doc.add_function(name, function)
        print("|", " " * 107, "|")

    @pyqtSlot(bool)
    def render_image(self, render):
        score = self.composer.compose()
        if not render:
            if self.advance_bar:
                print("|", end="")
            self.advance_bar = not self.advance_bar
            return
        self.pond_doc.score = score
        self.render.update(self.pond_doc.create_file())
        self.render.write()
        self.render.render()
        self.file_completed.emit()

    @pyqtSlot()
    def write_score(self):
        print("\nWriting Complete Score")
        self.main_document.document.score = self.composer.render_complete_score()
        self.render.update(self.main_document.create_file())
        self.render.write()


class MainDoc:
    def __init__(self):
        self.document = PondDoc()
        self.custom_commands = LilypondScripts.commands_dict()
        self.init_doc()

    def init_doc(self):
        header = PondHeader(title='"A Taste of Control"',
                            composer='"Tom Bañados"')
        paper = PondPaper()
        paper.update_margins({"top-margin": 10,
                              "left-margin": 15,
                              "right-margin": 15})
        paper.additional_data.append(LilypondScripts.paper_settings)
        self.document.paper = paper
        self.document.header = header
        for name, function in self.custom_commands.items():
            self.document.add_function(name, function)

    def create_file(self):
        return self.document.create_file()
