class PondInstrument:
    def __init__(self, lower_range, higher_range, transposition=0,
                 increased_range=0):
        self.range = [lower_range, higher_range,
                      higher_range + increased_range]
        self.transposition = transposition

    def validate_melody(self, melody):
        if min(melody.ordered_notes(), key=lambda x: x.absolute_int) < self.range[0]:
            return False, "lower"
        elif max(melody.ordered_notes(), key=lambda x: x.absolute_int) > self.range[2]:
            return False, "higher"
        elif max(melody.ordered_notes(), key=lambda x: x.absolute_int) > self.range[1]:
            return True, "increased"
        return True, "normal"

    def fit_melody(self, melody):
        fits, cause = self.validate_melody(melody)
        if fits:
            return melody
        if cause == "lower":
            pass

    def transpose(self, melody):
        melody.transpose(self.transposition)


class DurationConverter:
    simple_durations = {0.125: "32",
                        0.25: "16",
                        0.375: "16.",
                        0.5: "8",
                        0.75: "8.",
                        1: "4",
                        1.5: "4.",
                        2: "2",
                        3: "2.",
                        4: "1",
                        6: "1."
                        }

    @classmethod
    def get_duration_list(cls, duration):
        if duration % 0.125 or duration > 6:
            raise ValueError("DurationConverter currently only accepts "
                             "values up to the semiquaver and dotted whole note")
        duration_list = []
        current_value = duration
        next_value = 0
        while current_value > 0:
            if current_value in cls.simple_durations:
                duration_list.append(cls.simple_durations[current_value])
                current_value = next_value
                next_value = 0
            else:
                current_value -= 0.125
                next_value += 0.125
        return duration_list

    @classmethod
    def get_duration(cls, duration):
        try:
            return cls.simple_durations[duration]
        except KeyError:
            raise ValueError("DurationConverter currently only accepts "
                             "values up to the semiquaver")
