from pypond.PondMarks import Articulations, Dynamics, MiscMarks
from pypond.PondMusic import PondMelody, PondNote, PondFragment, PondPhrase, PondTuplet, PondPitch
from random import choices, randint, choice, uniform
from backend.pypond_extensions import DurationInterface, GlissandiCreator
from abc import ABC
from math import sqrt, modf


class ComposerBase(ABC):
    tuplet_initializers = {'3': (3, 2),
                           '4': None,
                           '5': (5, 4),
                           '6': (6, 4),
                           '7': (7, 4)
                           }

    @classmethod
    def compose_silence(cls, duration=4.):
        fragment = PondFragment()
        if duration == 0:
            return fragment
        duration_list = DurationInterface.get_duration_list(duration)
        for silence in duration_list:
            fragment.append_fragment(PondNote.create_rest(silence))
        return fragment


class ComposerEmpty(ComposerBase):
    def __init__(self, instruments=None):
        self.instruments = instruments or []

    def compose_instrument(self):
        pass


class ComposerA(ComposerBase):
    def __init__(self, instruments=None):
        self.instruments = instruments or []
        self.tuplet_weights = {'3': 10,
                               '4': 5,
                               '5': 3,
                               '6': 0
                               }
        self.tuplet_silences = {'3': (0, 1),
                                '4': (0, 0.25, 0.5, 0.75, 1, 1.5),
                                '5': (0, 1),
                                '6': (0, 0.5, 1, 1.5)}
        self.dynamic = Dynamics.pianissimo

    def compose(self, pitch_universe, direction, volume):
        evolution = randint(0, direction)
        duration = randint(2, 2 + volume)
        fragments = []
        used_tuplets = []
        used_silences = []
        for _ in range(3):
            empty = not randint(0, direction)
            trill = bool(randint(0, 1))
            climax = True if volume > 4 else False
            tuplet_type = self.tuplet_type(used_tuplets)
            silence = self.silence_type(tuplet_type, used_silences)
            new_fragment = self.compose_instrument(pitch_universe, evolution,
                                                   duration, empty, silence,
                                                   trill, climax, tuplet_type)
            if not trill and not empty:
                used_tuplets.append(tuplet_type)
            used_silences.append(silence)
            fragments.append(new_fragment)

        return fragments

    def tuplet_type(self, used):
        def tuplet_filter(tuplet):
            if tuplet[0] in used:
                return False
            return True

        filtered = filter(tuplet_filter, self.tuplet_weights.items())
        types, weights = zip(*filtered)
        return choices(types, weights=weights)[0]

    def silence_type(self, tuplet_type, used):
        def silence_filter(silence):
            print(silence)
            if silence in used and not silence == 0:
                return False
            return True

        possible = self.tuplet_silences[tuplet_type] + (0,)
        print(possible, used)
        return choice(tuple(filter(silence_filter, possible)))

    def compose_instrument(self, pitch_universe, evolution, duration,
                           empty=False, silence=0, trill=False, climax=False,
                           tuplet_type="4"):
        if empty:
            return self.compose_silence(duration)
        remaining_duration = duration - silence
        new_fragment = PondFragment()
        if trill:
            music_fragment = self.compose_trill_fragment(pitch_universe,
                                                         evolution=evolution,
                                                         duration=remaining_duration)
        else:
            music_fragment = self.compose_melodic_fragment(pitch_universe,
                                                           duration=remaining_duration,
                                                           dynamic_climax=climax,
                                                           tuplet_type=tuplet_type)
        music_fragment.transpose(12)
        if not silence:
            return music_fragment
        silence_fragment = self.compose_silence(silence)
        new_fragment.append_fragment(silence_fragment)
        new_fragment.append_fragment(music_fragment)
        return new_fragment

    def compose_melodic_fragment(self, pitch_universe, duration=3,
                                 dynamic_climax=False, tuplet_type="4"):
        note_number = int(tuplet_type) * int(duration)
        middle_note = note_number // 2
        index_route = self.build_index_route(note_number, len(pitch_universe))
        if tuplet_type == '4':
            melody = PondFragment()
            note_duration = 16
        else:
            melody = PondTuplet(*self.tuplet_initializers[tuplet_type],
                                duration=4)
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
                               evolution=2, tuplet_type=4):
        max_index = min(evolution + 1, len(pitch_universe) - 2)
        start_idx = randint(1, max_index)
        trill_idx = start_idx + 1
        start_pitch, trill_pitch = pitch_universe[start_idx], pitch_universe[trill_idx]
        fragment = PondFragment()
        start_phrase = PondFragment()
        if start_idx >= tuplet_type - 1:
            notes_fragment = PondPhrase()
            start_phrase.append_fragment(PondNote.create_rest(16))
            for idx in range(start_idx):
                note_duration = 8 if tuplet_type == 3 else 16
                new_note = PondNote(pitch_universe[idx], duration=note_duration)
                notes_fragment.append_fragment(new_note)
            start_phrase.append_fragment(notes_fragment)
            start_phrase.ordered_notes()[0].dynamic = Dynamics.crescendo_hairpin
        fragment.append_fragment(start_phrase)

        remaining_duration = duration - (len(start_phrase) // tuplet_type)
        note_durations = DurationInterface.get_duration_list(remaining_duration)
        main_note = PondNote(start_pitch,
                             duration=note_durations[0],
                             dynamic=self.dynamic)
        main_note.trill_marks(pitched=trill_pitch, relative=False)
        fragment.append_fragment(main_note)
        if len(note_durations) > 1:
            main_note.make_tie()
            for note_part_duration in note_durations[1:]:
                new_note = PondNote(start_pitch, duration=note_part_duration,
                                    tie=True)
                fragment.append_fragment(new_note)
            fragment.ordered_notes()[-1].make_tie(False)
        return fragment


class ComposerB(ComposerBase):
    repeat_durations = (2 / 7, 0.2, 0.4, 0.25,
                        1 / 3, 0.5, 0.75, 2 / 3)

    def __init__(self, instruments=None):
        self.instruments = instruments or []
        self.tuplet_data = {1 / 3: ('3', 8, False),
                            2 / 3: ('3', 4, True),
                            0.2: ('5', 16, False),
                            0.4: ('5', 8, True),
                            1 / 6: ('6', 16, False),
                            1 / 7: ('7', 16, False),
                            2 / 7: ('7', 8, True)}
        self.dynamic = Dynamics.forte

    @staticmethod
    def evolution_calculator(volume):
        return (sqrt(volume) / 3) - 0.5

    def compose(self, pitch_universe, direction, volume):
        lines = []
        duration = min(4, randint(1, volume + 1))
        evolution = self.evolution_calculator(volume)
        extended = randint(5, 10) < direction

        for _ in range(3):
            repeated = choice([1, 0, 0])
            new_fragment = self.compose_instrument(pitch_universe, duration,
                                                   repeated, evolution, extended)
            lines.append(new_fragment)

        return lines

    def compose_instrument(self, pitch_universe, duration, repeated=False,
                           evolution=0., extended=False):
        if repeated:
            max_index = min(len(pitch_universe) - 3, abs(int(evolution * len(pitch_universe)))) + 2
            main_pitch = choice(pitch_universe[:max_index])
            note_duration_idx = randint(0, min(6, duration + 1))
            note_duration = self.repeat_durations[note_duration_idx]
            new_fragment = self.compose_repeated(main_pitch, duration,
                                                 note_duration, evolution,
                                                 extended)
        else:
            gliss_duration = min(duration, 2)
            silence_duration = choice([0, 0.25, 0.5, 0.75, 1]) + (duration - gliss_duration)
            silence = self.compose_silence(silence_duration)
            middle_point = len(pitch_universe) // 2
            main_pitch = choice(pitch_universe[-middle_point:-1])
            new_fragment = self.compose_glissando(main_pitch, gliss_duration,
                                                  evolution, silence_duration % 1,
                                                  extended)
            new_fragment.insert_fragment(0, silence)
        new_fragment.transpose(12)
        return new_fragment

    def compose_repeated(self, repeated_pitch, duration,
                         note_duration,
                         evolution=0., extended=False):
        note_number = int(duration // note_duration)
        fragment = PondFragment()
        try:
            pond_duration = DurationInterface.get_pond_duration(note_duration)

            for _ in range(note_number):
                new_note = PondNote(repeated_pitch, duration=pond_duration,
                                    articulation=Articulations.staccato)
                if uniform(0, 1) < evolution:
                    GlissandiCreator.add_simple_glissando(new_note, -2)
                fragment.append_fragment(new_note)
            fragment_duration = DurationInterface.get_fragment_duration(fragment)
            result = modf(fragment_duration)
            silence_duration = 1 - result[0]
            silence_duration = modf(silence_duration)[0]
            if silence_duration != 0.:
                silence = self.compose_silence(silence_duration)
                fragment.insert_fragment(0, silence)

        except ValueError:
            tuplet_data = self.tuplet_data[note_duration]
            tuplet_type = tuplet_data[0]
            pond_duration = int(tuplet_data[1])
            tuplet = PondTuplet(*self.tuplet_initializers[tuplet_type[0]], 4)
            if tuplet_data[2]:
                target = (int(tuplet_type) // 2) * 2
                current = target // 2
                for i in range(note_number):
                    """if current == target:
                        current = 0"""
                    new_note = PondNote(repeated_pitch, duration=pond_duration * 2,
                                        articulation=Articulations.staccato)
                    tuplet.append_fragment(new_note)
                    tuplet.append_fragment(PondNote.create_rest(pond_duration * 2))
                    """else:
                        new_note = PondNote(repeated_pitch, duration=pond_duration,
                                            articulation=Articulations.staccato)
                        tuplet.append_fragment(new_note)
                        current += 1"""

            else:
                for _ in range(note_number):
                    new_note = PondNote(repeated_pitch, duration=pond_duration,
                                        articulation=Articulations.staccato)
                    tuplet.append_fragment(new_note)
            remaining, base_duration = DurationInterface.get_remainig_tuplet_time(tuplet)
            if remaining:
                for _ in range(remaining):
                    new_silence = self.compose_silence(base_duration)
                    tuplet.insert_fragment(0, new_silence)
            fragment.append_fragment(tuplet)

        if extended:
            glissando = self.long_glissando(repeated_pitch, 2)
            fragment.append_fragment(glissando)
        else:
            new_note = PondNote(repeated_pitch, 8, articulation=Articulations.accent)
            fragment.append_fragment(new_note)

        return fragment

    def compose_glissando(self, start_pitch, duration, evolution=0.,
                          start_position=0, extended=False):
        fragment = self.long_glissando(start_pitch, duration, start_position)
        fragment.ordered_notes()[0].dynamic = self.dynamic
        if extended:
            duration = DurationInterface.get_fragment_duration(fragment)
            new_start = (duration + start_position + 0.5) % 1
            fragment.append_fragment(self.compose_silence(0.5))
            jump = randint(1, 2 + int(evolution) * 3)
            new_glissando = self.long_glissando(start_pitch + jump, duration, new_start)
            fragment.append_fragment(new_glissando)

        return fragment

    @classmethod
    def long_glissando(cls, start_pitch, duration=3, start_position=0):
        initial_duration = 1 - start_position
        if start_position:
            end_pond_duration = DurationInterface.get_pond_duration(start_position)
        else:
            end_pond_duration = "4"
        pond_duration = DurationInterface.get_pond_duration(initial_duration)
        start_note = PondNote(start_pitch, duration=pond_duration)
        start_note.post_marks.append(GlissandiCreator.glissandoSkipOn)

        fragment = PondFragment()
        fragment.append_fragment(start_note)
        beat_amount = int(duration - start_position)
        end_pitch = PondPitch.from_absolute_int(start_pitch - 2)

        for i in range(beat_amount):
            new_note = PondNote(start_pitch)
            fragment.append_fragment(new_note)
        if start_position:
            new_note = PondNote(end_pitch, duration=end_pond_duration)
            fragment.append_fragment(new_note)
        else:
            fragment.ordered_notes()[-1].pitch = end_pitch
        last_note = fragment.ordered_notes()[-1]
        last_note.pre_marks.append(GlissandiCreator.glissandoSkipOff)
        last_note.set_ignore_accidental(True)
        last_note.hide_notehead()
        return fragment
