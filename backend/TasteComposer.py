from pypond.PondMusic import PondMelody, PondNote, PondFragment, PondPhrase
from pypond import PondScore
from random import choices, randint
import json
from backend.FragmentComposers import ComposerEmpty, ComposerA, ComposerB


class MainComposer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.stage = 0
        self.direction = 0
        self.command_volume = 0
        self.composers = {'0': ComposerEmpty(),
                          'A': ComposerA(),
                          'B': ComposerB()}

    def compose(self):
        fragment = 'B'
        pitch_universe = [0, 1, 3, 4, 6, 8, 9, 11, 12, 13, 15, 16, 18, 20, 21, 23, 24]
        score = PondScore.PondScore()
        for line in self.composers[fragment].compose(pitch_universe,
                                                     self.direction // 2,
                                                     self.command_volume // 4):
            staff = PondScore.PondStaff()

            staff.add_voice(line)
            staff.add_with_command("omit", "TimeSignature")
            score.add_staff(staff)
        self.direction += 1
        self.command_volume += 1
        return score
