from pypond.PondMusic import PondMelody
import json
from functools import reduce
from random import choice, shuffle
from time import time

from backend.FragmentComposers import ComposerEmpty, ComposerA, ComposerB, ComposerC, ComposerD
from pypond import PondScore


class MainComposer:
    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            self.data = json.load(file)
        self.stage = 2
        self.__direction = 0
        self.command_volume = 0.0
        empty = ComposerEmpty()
        self.composers = {0: empty,
                          1: ComposerA(),
                          2: ComposerB(),
                          3: ComposerC(),
                          4: empty,
                          5: ComposerD()}
        self.timer = Timer()
        self.timer.start()
        self.all_instruments = [PondMelody() for _ in range(3)]

    def render_complete_score(self):
        score = PondScore.PondScore()
        for line in self.all_instruments:
            staff = PondScore.PondStaff()
            staff.time_signature = PondScore.PondTimeSignature(6, 4)
            staff.add_voice(line)
            staff.add_with_command("omit", "TimeSignature")
            score.add_staff(staff)
        return score

    @property
    def direction(self):
        return abs(int(self.__direction))

    @direction.setter
    def direction(self, value):
        if value > 5 or self.stage in (0, 4):
            self.__direction = 0
            self.stage += 1
        else:
            self.__direction = value

    def update_command_volume(self):
        diffs = self.timer.last_values()
        if len(diffs) < 2:
            self.command_volume = 0.0
            return
        volume = reduce(lambda x, y: x / y, diffs, 0.8)
        self.command_volume = volume

    def get_volume(self):
        multiplier = (self.direction // 3) + 1
        return min(max(0., self.command_volume * multiplier), 1.)

    def compose(self):
        self.timer.new_time()
        pitch_universe = self.get_composer_data(self.stage, "PITCH_UNIVERSE")
        score = PondScore.PondScore()
        time_signature_initializers = self.get_composer_data(self.stage, "TIME_SIGNATURE")
        time_signature = PondScore.PondTimeSignature(*time_signature_initializers)
        voice_data = self.get_voice_data(self.stage)
        lines = self.composers[self.stage].compose(pitch_universe,
                                                   self.direction,
                                                   self.get_volume(),
                                                   voice_data)
        shuffle(lines)
        for line in lines:
            line_idx = lines.index(line)
            line.time_string = time_signature.as_string()
            self.all_instruments[line_idx].append_fragment(line)
            line.transpose(12)
            staff = PondScore.PondStaff()
            staff.time_signature = time_signature

            staff.add_voice(line)
            staff.add_with_command("omit", "TimeSignature")
            score.add_staff(staff)
        self.direction += choice([-1, -1, 0, 0,  1, 1, 1])
        self.update_command_volume()
        return score

    def get_voice_data(self, composer):
        types = self.get_composer_data(composer, 'VOICE_TYPES')[str(self.direction)]
        shuffle_silence = self.get_composer_data(composer, 'SHUFFLE_SILENCE')
        voices = choice(types)

        all_silences = [[1, 2, 2], [1, 1, 2], [0, 1, 2],
                        [0, 1, 1], [0, 1, 1], [0, 0, 1], [0, 0, 1]]
        min_index = max(self.stage, self.direction)
        silence_possibles = all_silences[min_index:]
        silences = choice(silence_possibles)
        if shuffle_silence:
            shuffle(silences)
        return list(zip(voices, silences))

    def get_composer_data(self, composer, data_needed='all'):
        if data_needed == 'all':
            return self.data['COMPOSER_DATA'][str(composer)]
        return self.data['COMPOSER_DATA'][str(composer)][data_needed]


class Timer:
    def __init__(self):
        self.last_time = 0
        self.time_list = []
        self.diff_list = []

    def start(self):
        self.last_time = time()
        self.time_list.append(self.last_time)

    def new_time(self):
        new = time()
        self.time_list.append(new)
        self.diff_list.append(new - self.last_time)
        self.last_time = new

    def last_values(self, idx=4):
        return self.diff_list[-idx:]
