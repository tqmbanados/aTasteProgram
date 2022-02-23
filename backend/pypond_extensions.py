from pypond.PondMusic import PondNote


class LilypondScripts:
    square_head = ('headSquare', '{\\once \\override NoteHead.stencil = #ly:text-interface::print\n'
                                 '\\once \\override NoteHead.text = '
                                 '#(markup #:musicglyph "noteheads.s2laWalker" )\n'
                                 '}')
    paper_settings = ("system-system-spacing =\n"
                      "  #'((basic-distance . 25)\n"
                      "  (minimum-distance . 18)\n"
                      "  (padding . 2)\n"
                      "  (stretchability . 60))\n"
                      "markup-system-spacing =\n"
                      "  #'((basic-distance . 40)\n"
                      "  (minimum-distance . 18))\n")
    slash_head = ('headSlash', '{\\once \\override NoteHead.stencil = #ly:text-interface::print\n'
                               '\\once \\override NoteHead.text = '
                               '#(markup #:musicglyph "noteheads.s0slash" )\n'
                               '}')

    gliss_on = ("glissOn", "\\override NoteColumn.glissando-skip =  ##t\n"
                           "    \\hide NoteHead\n"
                           "    \\override NoteHead.no-ledgers =  ##t\n")

    gliss_off = ("glissOff", "\\revert NoteColumn.glissando-skip\n"
                             "    \\undo \\hide NoteHead\n"
                             "    \\revert NoteHead.no-ledgers\n")

    @classmethod
    def make_square(cls, pond_note):
        pond_note.pre_marks.append("\\headSquare ")

    @classmethod
    def make_slash(cls, pond_note):
        pond_note.pre_marks.append("\\headSlash ")

    @classmethod
    def glissando(cls, pond_note, gliss_on=True):
        if gliss_on:
            pond_note.post_marks.append("\\glissOn")
        else:
            pond_note.pre_marks.append("\\glissOff")

    @classmethod
    def add_simple_glissando(cls, pond_note: PondNote, direction: int):
        pre_marks = "\\glissando \\cadenzaOn \\hideNotes \n"
        post_marks = "\\unHideNotes \\cadenzaOff \n"
        note_pitch = pond_note.absolute_int
        hidden_pitch = note_pitch + (2 * direction)
        duration = pond_note.duration
        hidden_note = PondNote(hidden_pitch, duration)
        hidden_note.pre_marks.append(pre_marks)
        hidden_note.post_marks.append(post_marks)
        pond_note.auxiliary_pitches['glissando'] = hidden_note
        pond_note.post_marks.append(hidden_note)

    @classmethod
    def commands_dict(cls):
        return {cls.square_head[0]: cls.square_head[1],
                cls.slash_head[0]: cls.slash_head[1],
                cls.gliss_on[0]: cls.gliss_on[1],
                cls.gliss_off[0]: cls.gliss_off[1]}


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
