from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer
from pypond.PondFile import PondDoc, PondRender
from pypond.PondCommand import PondHeader, PondPaper
from backend.pypond_extensions import LilypondScripts
from backend.TasteComposer import MainComposer
from backend.pond_request import put_score, put_actor
from parameters import COMMANDS_TEST
from random import choice
from os import path


class PyPondWriter(QObject):
    file_completed = pyqtSignal(int, tuple)
    stage_to_acting = '0ABCCD00'

    def __init__(self, beat_duration, use_api=False, url="localhost"):
        super().__init__()
        self.render = PondRender()
        self.pond_doc = PondDoc()
        self.main_document = MainDoc()
        self.composer = MainComposer(path.join('backend', "data.json"))
        self.advance_bar = False
        self.timer = QTimer(parent=self)
        self.measure_number = 0
        self.action_number = 0
        self.command = 'mirar al frente'
        self.beat_duration = beat_duration
        self.use_api = use_api
        self.api_url = url

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
        score, lines = self.composer.compose()
        actor_data = self.get_actor_data()
        self.measure_number += 1
        if self.use_api:
            self.post_lines(score, lines)
        if render:
            time = self.composer.current_time
            self.timer.setInterval(self.measure_duration(time))
            print(f"Rendering measure {self.measure_number}\n"
                  f"    Volume: {self.composer.volume}\n"
                  f"    Stage: {self.composer.stage}-{self.composer.direction}")
            self.pond_doc.score = score
            self.render.update(self.pond_doc.create_file())
            self.render.write()
            self.render.render()
            self.file_completed.emit(time, actor_data)

    def post_lines(self, score, lines):
        response = put_score(score.as_string(), 'score')
        print("Score posted with status code", response.status_code)
        zipped = zip(lines, ['Flute', 'Oboe', 'Clarinet'])
        for line, instrument in zipped:
            response = put_score(str(line), instrument,
                                 self.composer.current_time, self.measure_number)
            print(f"{instrument} posted with status code", response.status_code)
        stage = f"{self.composer.stage}-{self.composer.direction}"
        response = put_actor(self.command, stage, self.action_number)
        print(f"Actor posted with status code", response.status_code)

    def get_actor_data(self) -> tuple:
        stage = self.composer.stage
        act = self.stage_to_acting[stage]
        direction = self.composer.direction
        scene = '' if direction < 4 else '->'
        stage_data = act + scene
        action = choice(COMMANDS_TEST)
        return action, stage_data

    @pyqtSlot(dict)
    def update_values(self, values):
        volume = values['VOLUME']
        self.composer.volume = volume
        direction = values['DIRECTION']
        self.composer.direction += direction
        self.command = values['COMMAND']
        self.action_number += 1

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
