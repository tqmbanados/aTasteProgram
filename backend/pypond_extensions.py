from pypond.PondMusic import PondNote


class LilypondScripts:
    square_head = ('headSquare', '{\\once \\override NoteHead.stencil = #ly:text-interface::print\n'
                                 '\\once \\override NoteHead.text = '
                                 '#(markup #:musicglyph "noteheads.s2laWalker" )\n'
                                 '}')
    paper_settings = """system-system-spacing =
    #'((basic-distance . 25) 
       (minimum-distance . 18)
       (padding . 2)
       (stretchability . 60)) 
markup-system-spacing = 
    #'((basic-distance . 40)
      (minimum-distance . 18))"""
    slash_head = ('headSlash', '{\\once \\override NoteHead.stencil = #ly:text-interface::print\n'
                               '\\once \\override NoteHead.text = '
                               '#(markup #:musicglyph "noteheads.s0slash" )\n'
                               '}')

    @classmethod
    def make_square(cls, pond_note):
        pond_note.pre_marks.append("\\headSquare ")

    @classmethod
    def make_slash(cls, pond_note):
        pond_note.pre_marks.append("\\headSlash ")

    @classmethod
    def commands_dict(cls):
        return {cls.square_head[0]: cls.square_head[1],
                cls.slash_head[0]: cls.slash_head[1]}


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
