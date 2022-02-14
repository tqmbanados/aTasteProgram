from pypond.PondFile import PondDoc, PondRender
from pypond.PondCommand import PondHeader
from pypond import PondScore
from pypond.PondMarks import Articulations, Dynamics, MiscMarks
from pypond.PondMusic import PondMelody, PondNote, PondFragment, PondPhrase, PondTuplet
from random import choices, randint, choice


class ComposerEmpty:
    pass


class ComposerA:
    def __init__(self, instruments=None):
        self.instruments = instruments or []
        self.tuplet_weights = {'3': 10,
                               '4': 5,
                               '5': 3,
                               '6': 0
                               }
        self.tuplet_initializers = {'3': (3, 2),
                                    '4': None,
                                    '5': (5, 4),
                                    '6': (6, 4)
                                    }
        self.duration_converter = {0.5: "8",
                                   1: "4",
                                   2: "2",
                                   3: "2.",
                                   4: "1",
                                   6: "1."
                                   }
        self.dynamic = Dynamics.pianissimo

    def compose(self, pitch_universe):
        evolution = randint(3, 8)
        return self.compose_trill_fragment(pitch_universe, evolution=evolution)

    def compose_melodic_fragment(self, pitch_universe, duration=3,
                                 dynamic_climax=False):
        tuplet_type = self.get_tuplet_type()
        note_number = int(tuplet_type) * duration
        middle_note = note_number // 2
        index_route = self.build_index_route(note_number, len(pitch_universe))
        if tuplet_type == '4':
            melody = PondFragment()
            note_duration = 16
        else:
            melody = PondTuplet(*self.tuplet_initializers[tuplet_type],
                                duration=4,
                                add_phrasing=True)
            note_duration = 8 if tuplet_type == '3' else 16

        for i in range(note_number):
            idx = index_route[i]
            new_note = PondNote(pitch_universe[idx],
                                duration=note_duration)
            if i == 0:
                new_note.dynamic = self.dynamic
                new_note.phrase_data('begin')
            if i == 1:
                new_note.expressions = Dynamics.crescendo_hairpin
            if i == middle_note and not dynamic_climax:
                new_note.expressions = Dynamics.diminuendo_hairpin
            if i == note_number - 1:
                new_note.phrase_data('end')
                if dynamic_climax:
                    new_note.articulation = Articulations.staccato
                    new_note.dynamic = Dynamics.sforzando
                else:
                    new_note.expressions = MiscMarks.end_tag
            melody.append_fragment(new_note)
        return melody

    def get_tuplet_type(self):
        types, weights = zip(*self.tuplet_weights.items())
        return choices(types, weights=weights)[0]

    @classmethod
    def build_index_route(cls, note_amount, max_index):
        route_fragments = ((1, 1, 1, -2, 1),
                           (1, 1, -1, 1, 1),
                           (-2, 1, 1, 1, 1),
                           (-1, -1, -1, 1, 1),
                           (1, -2, -1, 1, 1),
                           (2, -2, 1, 1, 1),
                           (2, -1, 1, 1, -1),
                           (2, -1, -1, -1, -1))
        current = randint(0, 1)
        index_route = []
        route_fragment = iter(choice(route_fragments))
        for _ in range(note_amount):
            index_route.append(current)
            try:
                addition = next(route_fragment)

            except StopIteration:
                route_fragment = iter(choice(route_fragments))
                addition = next(route_fragment)
            current = cls.next_index_number(current, addition, max_index)
        return index_route

    @staticmethod
    def next_index_number(current, addition, max_index):
        if 0 <= current + addition < max_index:
            return current + addition
        else:
            return current - addition

    def compose_trill_fragment(self, pitch_universe, duration=4,
                               dynamic_climax=False, evolution=2, tuplet_type=4):
        max_index = min(evolution, len(pitch_universe) - 2)
        start_idx = randint(0, max_index)
        trill_idx = start_idx + 1
        start_pitch, trill_pitch = pitch_universe[start_idx], pitch_universe[trill_idx]
        start_phrase = PondFragment()
        if start_idx >= tuplet_type:
            rest_fragment = PondFragment()
            rest_amount = start_idx % tuplet_type
            for _ in range(rest_amount):
                rest = PondNote(-1, duration=8)
                rest.make_rest()
                rest_fragment.append_fragment(rest)
            note_fragment = PondPhrase()
            for idx in range(start_idx):
                note_duration= 8 if tuplet_type == 3 else 16
                new_note = PondNote(pitch_universe[idx], duration=note_duration)
                note_fragment.append_fragment(new_note)
            start_phrase.append_fragment(rest_fragment)
            start_phrase.append_fragment(note_fragment)
        remaining_duration = duration - (len(start_phrase) // tuplet_type)

        trill = PondNote(start_pitch,
                         duration=self.duration_converter[remaining_duration])
        pitched_trill = PondNote(trill_pitch)
        trill.trill_marks(pitched=pitched_trill, relative=False)
        fragment = PondFragment()
        fragment.append_fragment(start_phrase)
        fragment.append_fragment(trill)
        return fragment
