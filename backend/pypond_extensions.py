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
