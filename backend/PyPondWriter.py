from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer
from pypond.PondFile import PondDoc, PondRender
from pypond.PondCommand import PondHeader, PondPaper
from backend.pypond_extensions import LilypondScripts
from backend.TasteComposer import MainComposer
from os import path


class PyPondWriter(QObject):
    file_completed = pyqtSignal(int)

    def __init__(self, beat_duration):
        super().__init__()
        self.render = PondRender()
        self.pond_doc = PondDoc()
        self.main_document = MainDoc()
        self.composer = MainComposer(path.join('backend', "data.json"))
        self.advance_bar = False
        self.timer = QTimer(parent=self)
        self.measure_number = 0
        self.beat_duration = beat_duration

        self.init_doc()

    def init_doc(self):
        self.pond_doc.header = PondHeader()
        for name, function in LilypondScripts.commands_dict().items():
            self.pond_doc.add_function(name, function)
        self.timer.timeout.connect(self.render_image)
        self.timer.setInterval(self.measure_duration(6))

    @pyqtSlot()
    def begin(self):
        self.timer.start()

    def measure_duration(self, beat_number):
        return self.beat_duration * beat_number

    def render_image(self, render=True):
        score = self.composer.compose()[0]
        if render:
            time = self.composer.current_time
            self.timer.setInterval(self.measure_duration(time))
            print(f"Rendering measure {self.measure_number}\n"
                  f"    Volume: {self.composer.volume}\n"
                  f"    Stage: {self.composer.stage}-{self.composer.direction}")
            self.measure_number += 1
            self.pond_doc.score = score
            self.render.update(self.pond_doc.create_file())
            self.render.write()
            self.render.render()
            self.file_completed.emit(time)

    @pyqtSlot(dict)
    def update_values(self, values):
        volume = values['VOLUME']
        self.composer.volume = volume
        direction = values['DIRECTION']
        self.composer.direction += direction

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
