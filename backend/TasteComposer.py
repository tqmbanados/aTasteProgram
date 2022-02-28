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
        self.stage = 0
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
        self.current_time = 6
        self.__subsection = 500

    def render_complete_score(self):
        score = PondScore.PondScore()
        for line in self.all_instruments:
            staff = PondScore.PondStaff()
            staff.time_signature = PondScore.PondTimeSignature(6, 4)
            staff.top_level_text.extend(["\\override Hairpin.minimum-length =  # 7",
                                         "\\override Glissando.minimum-length =  # 5",
                                         "\\tempo 4 = 80"])
            staff.add_voice(line)
            staff.add_with_command("omit", "TimeSignature")
            score.add_staff(staff)
        return score

    @property
    def subsection(self):
        return self.__subsection

    @subsection.setter
    def subsection(self, value):
        if value <= self.direction or self.stage in (0, 4):
            self.direction += 1
            self.__subsection = 700
        else:
            self.__subsection = value

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
        if self.direction < 2:
            multiplier = 0.5
        elif self.direction > 3:
            multiplier = 2
        else:
            multiplier = 1
        return min(max(0., self.command_volume * multiplier), 1.)

    def compose(self):
        stage = self.stage if self.stage < 6 else 0
        self.timer.new_time()
        pitch_universe = self.get_composer_data(stage, "PITCH_UNIVERSE")
        score = PondScore.PondScore()
        time_signature_initializers = self.get_composer_data(stage, "TIME_SIGNATURE")
        time_signature = PondScore.PondTimeSignature(*time_signature_initializers)
        voice_data = self.get_voice_data(stage)
        composer = self.composers[stage]
        composer.set_dynamic(self.direction, self.get_volume())
        lines = composer.compose(pitch_universe,
                                 self.direction,
                                 self.get_volume(),
                                 voice_data)
        shuffle(lines)
        target_duration = time_signature_initializers[0]
        for line in lines:
            line.transpose(12)
            try:
                assert line.real_duration == target_duration
            except AssertionError:
                error_string = (f"Duration: {line.real_duration}, "
                                f"Target Duration: {target_duration}, "
                                f"Stage/direction: "
                                f"{self.stage}/{self.direction}, "
                                f"Volume: {self.get_volume()}, "
                                f"Voice_data:{voice_data}\n\n")
                print(error_string)
                with open("ERROR_LOG", "at") as file:
                    file.write(error_string)

            if self.current_time != target_duration:
                melody = PondMelody(time_string=time_signature.as_string())
                melody.append_fragment(line)
            else:
                melody = line
            line_idx = lines.index(line)
            self.all_instruments[line_idx].append_fragment(melody)

            staff = PondScore.PondStaff()
            staff.time_signature = time_signature
            staff.add_voice(line)
            staff.add_with_command("omit", "TimeSignature")
            score.add_staff(staff)

        self.subsection //= 2
        self.update_command_volume()
        self.current_time = target_duration
        return score

    def get_voice_data(self, composer):
        types = self.get_composer_data(composer, 'VOICE_TYPES')[str(self.direction)]
        shuffle_silence = self.get_composer_data(composer, 'SHUFFLE_SILENCE')
        voices = choice(types)

        all_silences = [[1, 2, 2], [1, 1, 2], [0, 1, 2],
                        [0, 1, 1], [0, 1, 1], [0, 0, 1], [0, 0, 1]]
        min_index = min(6, max(self.stage, self.direction))
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
