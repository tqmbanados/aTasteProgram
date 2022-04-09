from pypond.PondMusic import PondMelody
import json
from random import choice, shuffle

from .FragmentComposers import ComposerEmpty, ComposerA, ComposerB, ComposerC, ComposerD
from pypond import PondScore
from .pypond_extensions import PondInstrument, LilypondScripts


class MainComposer:
    def __init__(self, file_path):
        with open(file_path, 'r') as file:
            self.data = json.load(file)
        self.stage = 0
        self.__direction = 0
        self.__volume = 0.0
        empty = ComposerEmpty()
        self.instruments = {'flute': PondInstrument(0, 29, 5),
                            'oboe': PondInstrument(-1, 24, 3),
                            'clarinet': PondInstrument(-8, 24, 3, +2)}
        self.composers = {0: empty,
                          1: ComposerA(instruments=self.instruments),
                          2: ComposerB(instruments=self.instruments),
                          3: ComposerC(instruments=self.instruments),
                          4: empty,
                          5: ComposerD(instruments=self.instruments)}
        self.all_instruments = [PondMelody() for _ in range(3)]
        self.current_time = 6

    def render_complete_score(self):
        score = PondScore.PondScore()
        for line in self.all_instruments:
            staff = PondScore.PondStaff()
            staff.time_signature = PondScore.PondTimeSignature(6, 4)
            staff.top_level_text.extend(LilypondScripts.staff_marks)
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

    @property
    def volume(self):
        if self.direction < 2:
            multiplier = 0.5
        elif self.direction > 3:
            multiplier = 2
        else:
            multiplier = 1
        return min(max(0., self.__volume * multiplier), 1.)

    @volume.setter
    def volume(self, value):
        self.__volume = value

    def compose(self):
        stage = self.stage if self.stage < 6 else 0
        pitch_universe = self.get_composer_data(stage, "PITCH_UNIVERSE")

        score = PondScore.PondScore()
        time_signature_initializers = self.get_composer_data(stage, "TIME_SIGNATURE")
        time_signature = PondScore.PondTimeSignature(*time_signature_initializers)
        voice_data = self.get_voice_data(stage)
        composer = self.composers[stage]
        composer.set_dynamic(self.direction, self.volume)

        lines_by_instrument = composer.compose(pitch_universe,
                                               self.direction,
                                               self.volume,
                                               voice_data)
        target_duration = time_signature_initializers[0]

        for instrument, line in lines_by_instrument.items():
            if instrument == 'clarinet':
                self.instruments['clarinet'].transpose(line)

        lines = [lines_by_instrument['flute'],
                 lines_by_instrument['oboe'],
                 lines_by_instrument['clarinet']]

        for line in lines:
            line.transpose(12)
            try:
                assert line.real_duration == target_duration
            except AssertionError:
                error_string = (f"Duration: {line.real_duration}, "
                                f"Target Duration: {target_duration}, "
                                f"Stage/direction: "
                                f"{self.stage}/{self.direction}, "
                                f"Volume: {self.volume}, "
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

        self.current_time = target_duration
        return score, lines_by_instrument

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
