from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from pypond.PondFile import PondDoc, PondRender
from pypond.PondCommand import PondHeader
from pypond import PondScore
from pypond.PondMusic import PondMelody, PondNote, PondFragment, PondPhrase, PondTuplet
from random import choices


class PyPondWriter(QObject):
    file_completed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.render = PondRender()
        self.pond_doc = PondDoc()

    @pyqtSlot()
    def render_image(self):
        melody = choices([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, -1], k=10)
        rhythm = choices([2, 4, 8], k=10)
        new_melody = PondMelody()
        fragment_1 = PondFragment()
        for note, duration in zip(melody, rhythm):
            fragment_1.fragments.append(PondNote(note, duration=duration))
        fragment_3 = PondPhrase([3, fragment_1])

        new_melody.fragments.append(fragment_1)
        new_melody.fragments.append(fragment_3)
        new_melody.transpose(8)

        header = PondHeader()
        score = PondScore.PondScore()
        staff = PondScore.PondStaff()

        staff.add_voice(new_melody)
        staff.add_with_command("omit", "TimeSignature")
        score.add_staff(staff)
        self.pond_doc.score = score
        self.pond_doc.header = header
        self.render.update(self.pond_doc.create_file())
        self.render.write()
        self.render.render()
        self.file_completed.emit()


