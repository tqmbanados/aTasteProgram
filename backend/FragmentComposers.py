from pypond.PondFile import PondDoc, PondRender
from pypond.PondCommand import PondHeader
from pypond import PondScore
from pypond.PondMarks import Articulations, Dynamics, MiscMarks
from pypond.PondMusic import PondMelody, PondNote, PondFragment, PondPhrase, PondTuplet
from random import choices, randint, choice


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
        self.dynamic = Dynamics.pianissimo

    def compose_fragment(self, pitch_universe, duration=3, trill=False,
                         dynamic_climax=False):
        tuplet_type = self.get_tuplet_type()
        note_number = int(tuplet_type) * duration
        middle_note = note_number // 2
        index_route = self.build_index_route(note_number, len(pitch_universe))
        if tuplet_type == '4':
            melody = PondPhrase()
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
            if i == 1:
                new_note.expressions = Dynamics.crescendo_hairpin
            if i == middle_note and not dynamic_climax:
                new_note.expressions = Dynamics.diminuendo_hairpin
            if i == note_number - 1:
                if dynamic_climax:
                    new_note.articulation = Articulations.staccato
                    new_note.dynamic = Dynamics.sforzando
                else:
                    new_note.expressions = MiscMarks.end_tag
            melody.append_fragment(new_note)
        return melody

    def compose(self, pitch_universe):
        return self.compose_fragment(pitch_universe)

    def get_tuplet_type(self):
        types, weights = zip(*self.tuplet_weights.items())
        return choices(types, weights=weights)[0]

    def build_index_route(self, note_amount, max_index):
        route_fragments = ((1, 1, 1, -2, 1),
                           (1, 1, -1, 1, 1),
                           (-2, 1, 1, 1, 1),
                           (-1, -1, -1, 1, 1),
                           (1, -2, -1, 1, 1),
                           (2, -2, 1, 1, 1),
                           (2, -1, 1, 1, -1),
                           (-1, -1, -1, -1, 1),
                           (2, -1, -1, -1, -1))
        current = randint(0, 1)
        index_route = []
        route_fragment = iter(choice(list(route_fragments)))
        for _ in range(note_amount):
            index_route.append(current)
            try:
                addition = next(route_fragment)

            except StopIteration:
                route_fragment = iter(choice(route_fragments))
                addition = next(route_fragment)
            current = self.next_index_number(current, addition, max_index)
        return index_route

    @staticmethod
    def next_index_number(current, addition, max_index):
        if not 0 < current + addition <= max_index:
            print(current, addition)
            return current - addition
        else:
            return current + addition
