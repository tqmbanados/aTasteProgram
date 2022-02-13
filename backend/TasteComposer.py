from pypond.PondMusic import PondMelody, PondNote, PondFragment, PondPhrase
from random import choices
import json
from backend.FragmentComposers import ComposerA


class MainComposer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.stage = 0
        self.direction = 0
        self.command_volume = 0
        self.composers = {'A': ComposerA()}

    def compose(self):
        fragment = 'A'
        pitch_universe = [0, 1, 3, 4, 6, 8, 9, 11]
        return self.composers[fragment].compose(pitch_universe)

    @staticmethod
    def test_score():
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
        return new_melody

