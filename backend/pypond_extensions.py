from pypond.PondMusic import PondNote


class LilypondScripts:
    square_head = ('headSquare', '{\\once \\override NoteHead.stencil = #ly:text-interface::print\n'
                                 '\\once \\override NoteHead.text = '
                                 '#(markup #:musicglyph "noteheads.s2laWalker" )\n'
                                 '}')
    paper_settings = ("system-system-spacing =\n"
                      "  #'((basic-distance . 18)\n"
                      "  (minimum-distance . 14)\n"
                      "  (padding . 2)\n"
                      "  (stretchability . 60))\n"
                      "markup-system-spacing =\n"
                      "  #'((basic-distance . 25)\n"
                      "  (minimum-distance . 18))\n")
    slash_head = ('headSlash', '{\\once \\override NoteHead.stencil = #ly:text-interface::print\n'
                               '\\once \\override NoteHead.text = '
                               '#(markup #:musicglyph "noteheads.s0slash" )\n'
                               '}')

    gliss_on = ("glissOn", "{\\override NoteColumn.glissando-skip =  ##t\n"
                           "    \\hide NoteHead\n"
                           "    \\omit Accidental\n"
                           "    \\override NoteHead.no-ledgers =  ##t\n}")

    gliss_off = ("glissOff", "{\\revert NoteColumn.glissando-skip\n"
                             "    \\undo \\hide NoteHead\n"
                             "    \\undo \\omit Accidental\n"
                             "    \\revert NoteHead.no-ledgers\n}")

    staff_marks = ["\\override Hairpin.minimum-length =  # 7",
                   "\\override Glissando.minimum-length =  # 5",
                   "\\tempo 4 = 80"]

    @classmethod
    def make_square(cls, pond_note):
        pond_note.pre_marks.append("\\headSquare ")

    @classmethod
    def make_slash(cls, pond_note):
        pond_note.pre_marks.append("\\headSlash ")

    @classmethod
    def glissando(cls, pond_note, gliss_on=True):
        if gliss_on:
            pond_note.post_marks.append("\\glissando\\glissOn ")
        else:
            pond_note.pre_marks.append("\\glissOff ")

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
    def __init__(self, lower_range, higher_range,
                 increased_range=0, transposition=0):
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

    def limit_pitch_universe(self, pitch_universe: list):
        allowed_pitches = range(self.range[0], self.range[2] + 1)
        universe = []
        for pitch in pitch_universe:
            if pitch in allowed_pitches:
                universe.append(pitch)
        return universe

    def transpose(self, melody):
        melody.transpose(self.transposition)
