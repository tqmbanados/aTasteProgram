from pypond.PondMusic import PondNote


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


class DurationInterface:
    simple_converter = {0.125: "32",
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

    reverse_simple_converter = {value: key for key, value in simple_converter.items()}

    @classmethod
    def get_duration_list(cls, duration):
        if duration % 0.125 or duration > 6:
            raise ValueError(f"DurationConverter currently only accepts "
                             f"values up to the semiquaver. Attempted value: {duration}")
        duration_list = []
        current_value = duration
        next_value = 0
        while current_value > 0:
            if current_value in cls.simple_converter:
                duration_list.append(cls.simple_converter[current_value])
                current_value = next_value
                next_value = 0
            else:
                current_value -= 0.125
                next_value += 0.125
        return duration_list

    @classmethod
    def get_fragment_duration(cls, fragment):
        """
        Warning: Does not provide correct duration of PondTuplets
        """
        mapped = map(lambda x: cls.get_real_duration(x.duration), fragment.ordered_notes())
        return sum(mapped)

    @classmethod
    def get_remainig_tuplet_time(cls, tuplet):
        target, base_value, duration = tuplet.data
        pond_duration = int(base_value) * int(duration)
        base_duration = cls.get_real_duration(pond_duration)
        total_duration = cls.get_fragment_duration(tuplet)
        remaining_beats = target - ((total_duration / base_duration) % target)
        if remaining_beats == target:
            remaining_beats = 0
        return int(remaining_beats), base_duration

    @classmethod
    def get_pond_duration(cls, duration):
        try:
            return cls.simple_converter[float(duration)]
        except KeyError:
            raise ValueError(f"DurationConverter currently only accepts "
                             f"values up to the semiquaver. Attempted value: {duration}")

    @classmethod
    def get_real_duration(cls, duration):
        try:
            return cls.reverse_simple_converter[str(duration)]
        except KeyError:
            raise ValueError(f"DurationConverter requires a valid Lilypond duration. "
                             f"Attempted value: {duration}")


class GlissandiCreator:
    glissandoSkipOn = """
    \\glissando
    \\override NoteColumn.glissando-skip =  ##t
    \\hide NoteHead
    \\override NoteHead.no-ledgers =  ##t
    """
    glissandoSkipOff = """
    \\revert NoteColumn.glissando-skip
    \\undo \\hide NoteHead
    \\revert NoteHead.no-ledgers
    """

    @classmethod
    def add_simple_glissando(cls, pond_note: PondNote, direction: int):
        pre_marks = "\\glissando \\cadenzaOn \\hideNotes \n"
        post_marks = "\\unHideNotes \\cadenzaOff \n"
        note_pitch = pond_note.absolute_int
        hidden_pitch = note_pitch + (2 * direction)
        hidden_note = PondNote(hidden_pitch)
        hidden_note.pre_marks.append(pre_marks)
        hidden_note.post_marks.append(post_marks)

        pond_note.auxiliary_pitches['glissando'] = hidden_note
        pond_note.post_marks.append(hidden_note)
