class PondInstrument:
    def __init__(self, lower_range, higher_range, transposition=0, increased_range=0):
        self.range = [lower_range, higher_range, higher_range + increased_range]
        self.transposition = transposition

    