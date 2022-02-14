class PondInstrument:
    def __init__(self, lower_range, higher_range, transposition=0,
                 increased_range=0):
        self.range = [lower_range, higher_range,
                      higher_range + increased_range]
        self.transposition = transposition

    def validate_melody(self, melody):
        if min(melody, key=lambda x: x.absolute_int) < self.range[0]:
            return False, "lower"
        elif max(melody, key=lambda x: x.absolute_int) > self.range[2]:
            return False, "higher"
        elif max(melody, key=lambda x: x.absolute_int) > self.range[1]:
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

