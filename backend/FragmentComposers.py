from abc import ABC
from math import sqrt, modf
from random import choices, randint, choice, uniform, shuffle

from backend.pypond_extensions import GlissandiCreator
from pypond.PondMarks import Articulations, Dynamics, MiscMarks
from pypond.PondMusic import PondNote, PondFragment, PondPhrase, PondTuplet, PondPitch
from pypond.PondCore import DurationInterface
from pypond.PondCommand import PondMarkup


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
        duration_list = DurationInterface.get_duration_list(duration, True)
        for silence in duration_list:
            fragment.append_fragment(PondNote.create_rest(silence))
        return fragment

    @classmethod
    def complete_silence(cls, fragment, stop_trill=False):
        final_fragment = PondFragment()
        final_fragment.append_fragment(fragment)
        duration = fragment.real_duration
        remaining = 6 - duration
        start, rest = modf(remaining)
        silence_fragment = PondFragment()
        silence_fragment.append_fragment(cls.compose_silence(start))
        silence_fragment.append_fragment(cls.compose_silence(rest))
        first = silence_fragment.get_note(0)
        first.post_marks.append(MiscMarks.end_tag)
        if stop_trill and silence_fragment.ordered_notes():
            first.trill_marks(False)
        final_fragment.append_fragment(silence_fragment)
        return final_fragment


class ComposerEmpty(ComposerBase):
    instructions = {'english': '"Breathe naturally. '
                               'Expel air with force through instrument."',
                    'español': '"Respira naturalmente. '
                               'Expulsa el aire con fuerza a través del instrumento."'}

    def __init__(self, instruments=None, language='english'):
        self.instruments = instruments or []
        self.language = language

    def compose(self, *args, **kwargs):
        lines = []
        for _ in range(3):
            new_line = self.compose_instrument(self.language)
            lines.append(new_line)
        return lines

    @classmethod
    def compose_instrument(cls, language):
        instructions = cls.instructions[language]
        smaller = PondMarkup.small
        markup = PondMarkup(instructions, smaller, smaller)
        markup_string = markup.add_to_note()
        fragment = PondFragment()
        rest = PondNote(-1, "1.")
        rest.post_marks.append(markup_string)
        rest.hide_note()
        fragment.append_fragment(rest)
        return fragment


class ComposerA(ComposerBase):
    def __init__(self, instruments=None):
        self.instruments = instruments or []
        self.dynamic = Dynamics.pianissimo
        self.language = "english"

    @staticmethod
    def evolution_calculator(volume):
        return sqrt(volume) / 4

    @classmethod
    def get_tuplet_weights(cls, volume):
        tuplet_weights = {'3': 1 - volume,
                          '4': 0.8 - (volume * 0.8),
                          '5': 0.2 + (volume * 0.8),
                          '6': 0 + volume
                          }

        return tuplet_weights

    def compose(self, pitch_universe, direction, volume, voice_data):
        duration = min(5, randint(2, 2 + direction))
        fragments = []
        used_tuplets = []
        for voice_type, silence in voice_data:
            extended = randint(2, 5) < direction
            climax = True if direction > 3 else False
            tuplet_type = self.tuplet_type(used_tuplets, volume)
            new_fragment = self.compose_instrument(pitch_universe, volume,
                                                   duration, voice_type,
                                                   silence, climax, tuplet_type,
                                                   extended=extended)
            if voice_type == 2:
                used_tuplets.append(tuplet_type)
            fragments.append(new_fragment)

        return fragments

    def tuplet_type(self, used, volume):
        def tuplet_filter(tuplet):
            if tuplet[0] in used:
                return False
            return True

        filtered = filter(tuplet_filter, self.get_tuplet_weights(volume).items())
        types, weights = zip(*filtered)
        return choices(types, weights=weights)[0]

    def compose_instrument(self, pitch_universe, evolution, duration,
                           voice_type=1, silence=0, climax=False,
                           tuplet_type="4", extended=False):
        if voice_type == 0:
            if not extended:
                return ComposerEmpty.compose_instrument(self.language)
            else:
                return self.compose_silence(6.)
        remaining_duration = max(duration - silence, 1)
        if voice_type == 2:
            music_fragment = self.compose_trill_fragment(pitch_universe,
                                                         evolution=evolution,
                                                         duration=remaining_duration,
                                                         extended=extended)
        else:
            music_fragment = self.compose_melodic_fragment(pitch_universe,
                                                           duration=remaining_duration,
                                                           climax=climax,
                                                           tuplet_type=tuplet_type,
                                                           extended=extended,
                                                           evolution=evolution)
        music_fragment.transpose(12)
        if silence:
            silence_fragment = self.compose_silence(silence)
            music_fragment.insert_fragment(0, silence_fragment)

        assert isinstance(music_fragment, (PondFragment, PondPhrase)), f"{type(music_fragment)}"
        return self.complete_silence(music_fragment, True)

    def compose_melodic_fragment(self, pitch_universe, duration=3,
                                 climax=False, tuplet_type="4",
                                 extended=False, evolution=0):
        note_number = int(tuplet_type) * int(duration)
        silent_beat = randint(0, 1)
        silence_number = int((0.6 - uniform(0, evolution)) * int(tuplet_type))
        print(evolution, silence_number)
        fragment = PondFragment()
        if silent_beat:
            fragment.append_fragment(self.compose_silence(1))
        note_number -= silence_number
        middle_note = note_number // 2
        index_route = self.build_index_route(note_number + 1, len(pitch_universe))
        if tuplet_type == '4':
            main_fragment = PondFragment()
            note_duration = 16
        else:
            main_fragment = PondTuplet(*self.tuplet_initializers[tuplet_type],
                                       group_duration=4)
            note_duration = 8 if tuplet_type == '3' else 16
        for i in range(silence_number):
            new_silence = PondNote(-1, note_duration)
            new_silence.make_rest()
            main_fragment.append_fragment(new_silence)
        for i in range(note_number):
            idx = index_route[i]
            new_note = PondNote(pitch_universe[idx],
                                duration=note_duration)
            if i == 0:
                new_note.dynamic = self.dynamic
                new_note.phrase_data('begin')
            if i == 1:
                new_note.expressions = Dynamics.crescendo_hairpin
            if i == middle_note and not (climax or extended):
                new_note.expressions = Dynamics.diminuendo_hairpin
            if i == note_number - 1:
                new_note.phrase_data('end')
                if not climax:
                    new_note.expressions = MiscMarks.end_tag
            main_fragment.append_fragment(new_note)
        fragment.append_fragment(main_fragment)
        last_pitch = pitch_universe[index_route[-1]]
        if extended and climax:
            note_duration = choice((0.2, 0.25, 1 / 3, 0.5, 0.75))
            repeated = ComposerB.compose_repeated(last_pitch, 1, note_duration)
            first_note = repeated.ordered_notes()[0]
            first_note.dynamic = Dynamics.sforzando
            first_note.expressions = Dynamics.diminuendo_hairpin
            fragment.append_fragment(repeated)
        elif climax:
            new_note = PondNote(last_pitch, duration=8, dynamic=Dynamics.sforzando)
            new_note.articulation = Articulations.accent
            fragment.append_fragment(new_note)

        return fragment

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
                               evolution=2., tuplet_type=4, extended=False, silence=0):
        max_index = 1 + 3 * int(evolution * (len(pitch_universe) - 1)) // 2
        start_idx = randint(0, max_index)
        trill_idx = start_idx + 1
        start_pitch, trill_pitch = pitch_universe[start_idx], pitch_universe[trill_idx]
        fragment = PondFragment()
        start_phrase = PondFragment()
        if start_idx >= tuplet_type + 1:
            notes_fragment = PondPhrase()
            start_phrase.append_fragment(PondNote.create_rest(16))
            for idx in range(start_idx // 2, start_idx):
                note_duration = 8 if tuplet_type == 3 else 16
                new_note = PondNote(pitch_universe[idx], duration=note_duration)
                notes_fragment.append_fragment(new_note)

            start_phrase.append_fragment(notes_fragment)
            start_phrase.ordered_notes()[0].dynamic = Dynamics.crescendo_hairpin
        fragment.append_fragment(start_phrase)
        start_position = (silence + start_phrase.real_duration) % 1
        start_duration = 1 - start_position
        remaining_duration = max(0.5, duration - (len(start_phrase) // tuplet_type))
        note_durations = DurationInterface.get_duration_list(remaining_duration, True,
                                                             start_duration)
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
            last_note = fragment.get_note(-1)
            last_note.make_tie(False)

        if extended:
            extended_fragment = PondPhrase()
            total_duration = fragment.real_duration + silence
            remaining_duration = 1 - (total_duration % 1)
            if remaining_duration == 0:
                remaining_duration = 1
            note_amount = int(remaining_duration / 0.125)
            end = False
            for idx in range(start_idx, start_idx + note_amount + 1):
                try:
                    pitch = pitch_universe[idx]
                except IndexError:
                    if end:
                        pitch = pitch_universe[-2]
                    else:
                        pitch = pitch_universe[-1]
                    end = not end
                new_note = PondNote(pitch, 32)
                extended_fragment.append_fragment(new_note)
            first_note = extended_fragment.get_note(0)
            first_note.expressions = Dynamics.crescendo_hairpin
            first_note.trill_marks(False)
            last_note = extended_fragment.get_note(-1)
            last_note.dynamic = Dynamics.sforzando
            last_note.articulation = Articulations.staccato

        return fragment


class ComposerB(ComposerBase):
    repeat_durations = (2 / 7, 0.2, 0.4, 0.25,
                        1 / 3, 0.5, 0.75, 2 / 3)
    tuplet_data = {1 / 3: ('3', 8, False),
                   2 / 3: ('3', 4, True),
                   0.2: ('5', 16, False),
                   0.4: ('5', 8, True),
                   1 / 6: ('6', 16, False),
                   1 / 7: ('7', 16, False),
                   2 / 7: ('7', 8, True)}

    def __init__(self, instruments=None):
        self.instruments = instruments or []
        self.dynamic = Dynamics.forte

    @staticmethod
    def evolution_calculator(volume):
        return (sqrt(volume) / 3) - 0.5

    def compose(self, pitch_universe, direction, volume, voice_data):
        lines = []
        duration = min(4, randint(1, direction + 1))
        evolution = volume
        extended = randint(5, 10) < direction

        for voice_type, silence in voice_data:
            new_fragment = self.compose_instrument(pitch_universe, duration,
                                                   voice_type, silence, evolution,
                                                   extended)
            lines.append(new_fragment)

        return lines

    def compose_instrument(self, pitch_universe, duration, voice_type,
                           silence, evolution=0., extended=False):
        if voice_type == 0:
            return self.compose_silence(6.)
        if silence:
            start_silence = self.compose_silence(silence)
        else:
            start_silence = PondFragment()
        if voice_type == 1:
            max_index = min(len(pitch_universe) - 3, abs(int(evolution * len(pitch_universe)))) + 2
            main_pitch = choice(pitch_universe[:max_index])
            note_duration_idx = randint(0, min(6, duration + 1))
            note_duration = self.repeat_durations[note_duration_idx]
            new_fragment = self.compose_repeated(main_pitch, duration,
                                                 note_duration, evolution,
                                                 extended)
        else:
            gliss_duration = min(duration, 2)
            silence_duration = choice([0, 0.25, 0.5, 0.75]) + (duration - gliss_duration)
            middle_point = len(pitch_universe) // 2
            main_pitch = choice(pitch_universe[-middle_point:-1])
            new_fragment = self.compose_glissando(main_pitch, gliss_duration,
                                                  evolution, silence_duration,
                                                  extended)
            if silence_duration > 0:
                start_silence.append_fragment(self.compose_silence(silence_duration))

        new_fragment.insert_fragment(0, start_silence)
        new_fragment.transpose(12)
        return self.complete_silence(new_fragment)

    @classmethod
    def compose_repeated(cls, repeated_pitch, duration,
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
            fragment_duration = fragment.real_duration
            result = modf(fragment_duration)
            silence_duration = 1 - result[0]
            silence_duration = modf(silence_duration)[0]
            if silence_duration != 0.:
                silence = cls.compose_silence(silence_duration)
                fragment.insert_fragment(0, silence)

        except ValueError:
            tuplet_data = cls.tuplet_data[note_duration]
            tuplet_type = tuplet_data[0]
            pond_duration = int(tuplet_data[1])
            tuplet = PondTuplet(*cls.tuplet_initializers[tuplet_type[0]], 4)
            silence_number, silence_duration = cls.get_tuplet_start_silence(tuplet_data,
                                                                            note_number)
            for _ in range(silence_number):
                new_silence = PondNote(0, silence_duration)
                new_silence.make_rest()
                tuplet.append_fragment(new_silence)
            if tuplet_data[2]:
                target = int(tuplet_type)
                current = silence_number
                rest = False
                for i in range(note_number):
                    if rest:
                        tuplet.append_fragment(PondNote.create_rest(pond_duration * 2))
                        rest = False
                        current += 1
                    if current + 1 == target:
                        new_note = PondNote(repeated_pitch, duration=pond_duration * 2,
                                            articulation=Articulations.staccato)
                        tuplet.append_fragment(new_note)
                        rest = True
                        current += 1
                    else:
                        new_note = PondNote(repeated_pitch, duration=pond_duration,
                                            articulation=Articulations.staccato)
                        tuplet.append_fragment(new_note)
                        current += 2
                    if current == target:
                        current = 0

            else:
                for _ in range(note_number):
                    new_note = PondNote(repeated_pitch, duration=pond_duration,
                                        articulation=Articulations.staccato)
                    tuplet.append_fragment(new_note)
            fragment.append_fragment(tuplet)

        if extended:
            glissando = cls.long_glissando(repeated_pitch, 2)
            fragment.append_fragment(glissando)
        else:
            new_note = PondNote(repeated_pitch, 8, articulation=Articulations.accent)
            fragment.append_fragment(new_note)

        return fragment

    @staticmethod
    def get_tuplet_start_silence(tuplet_data, note_number):
        beat_number = note_number * 2 if tuplet_data[2] else note_number
        silence_duration = int(tuplet_data[1]) * 2 if tuplet_data[2] else int(tuplet_data[1])
        target = int(tuplet_data[0])
        silence = target - (beat_number % target)
        silence = 0 if silence == target else silence
        return silence, silence_duration

    def compose_glissando(self, start_pitch, duration, evolution=0.,
                          start_position=0, extended=False):
        fragment = self.long_glissando(start_pitch, duration, start_position)
        fragment.ordered_notes()[0].dynamic = self.dynamic
        if extended:
            duration = fragment.real_duration
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
