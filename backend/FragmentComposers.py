from abc import ABC, abstractmethod
from math import sqrt, modf
from random import choices, randint, choice, uniform, shuffle

from backend.pypond_extensions import LilypondScripts
from pypond.PondMarks import Articulations, Dynamics, MiscMarks
from pypond.PondMusic import PondNote, PondFragment, PondPhrase, PondTuplet, PondPitch
from pypond.PondCore import DurationInterface
from statistics import mode
from functools import reduce


class ComposerBase(ABC):
    tuplet_initializers = {'3': (3, 2),
                           '4': None,
                           '5': (5, 4),
                           '6': (6, 4),
                           '7': (7, 4)
                           }
    repeat_durations = (2 / 7, 0.2, 0.4, 0.25,
                        1 / 3, 0.5, 0.75, 2 / 3)
    tuplet_data = {1 / 3: ('3', 8, False),
                   2 / 3: ('3', 4, True),
                   0.2: ('5', 16, False),
                   0.4: ('5', 8, True),
                   1 / 6: ('6', 16, False),
                   1 / 7: ('7', 16, False),
                   2 / 7: ('7', 8, True)}
    dynamics_data = {0: Dynamics.pianissimo,
                     1: Dynamics.piano,
                     2: Dynamics.mezzo_piano,
                     3: Dynamics.mezzo_forte,
                     4: Dynamics.forte,
                     5: Dynamics.fortissimo,
                     6: Dynamics.custom_dynamic("f", 3)}

    def __init__(self, instruments=None):
        self.instruments = instruments or {}
        self.dynamic = Dynamics.pianissimo

    @abstractmethod
    def set_dynamic(self, direction, volume):
        pass

    @abstractmethod
    def compose(self, pitch_universe, direction, volume, voice_data) -> dict:
        pass

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
    def complete_silence(cls, fragment, stop_trill=False, max_duration=6):
        final_fragment = PondFragment()
        final_fragment.append_fragment(fragment)
        duration = fragment.real_duration
        remaining = max_duration - duration
        start, rest = modf(remaining)
        silence_fragment = PondFragment()
        silence_fragment.append_fragment(cls.compose_silence(start))
        silence_fragment.append_fragment(cls.compose_silence(rest))
        if silence_fragment.ordered_notes():
            first = silence_fragment.get_note(0)
            first.post_marks.append(MiscMarks.end_tag)
            if stop_trill:
                first.trill_marks(False)
        final_fragment.append_fragment(silence_fragment)
        return final_fragment

    def instrument_order(self):
        instruments = [instrument for instrument in self.instruments]
        shuffle(instruments)
        return instruments

    def get_voice_pitch_universe(self, pitch_universe, instrument):
        instrument = self.instruments[instrument]
        return instrument.limit_pitch_universe(pitch_universe)

    def compose_melodic_fragment(self, pitch_universe, duration=3,
                                 climax=False, tuplet_type="4",
                                 extended=False, volume=0.,
                                 reverse=False):
        duration = duration - climax - extended
        assert duration > 1
        note_number = int(tuplet_type) * int(duration)
        silence_number = int(abs(0.7 - volume) * int(tuplet_type))
        note_number -= silence_number
        fragment = PondFragment()
        if extended:
            duration -= 2
        elif climax:
            duration -= 1
        middle_note = note_number // 2
        index_route = self.build_index_route(note_number + 1, len(pitch_universe))
        if reverse:
            index_route = index_route[::-1]
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
            repeated = self.compose_repeated(last_pitch, 1, note_duration)
            first_note = repeated.ordered_notes()[0]
            first_note.dynamic = Dynamics.sforzando
            first_note.expressions = Dynamics.diminuendo_hairpin
            fragment.append_fragment(repeated)
        elif climax:
            new_note = PondNote(last_pitch, duration=8, dynamic=Dynamics.sforzando)
            new_note.articulation = Articulations.accent
            fragment.append_fragment(new_note)

        return fragment

    def compose_target_melodic_fragment(self, pitch_universe, target_index,
                                        duration=3, tuplet_type="4", volume=0.0,
                                        extension_type=0):
        assert duration > 1
        assert target_index < len(pitch_universe), (f"target: {target_index}, "
                                                    f"max: {len(pitch_universe)}")
        note_number = int(tuplet_type) * int(duration)
        silence_number = int(abs(0.5 - volume) * int(tuplet_type))
        note_number -= silence_number
        fragment = PondFragment()
        index_route = self.build_index_route(note_number + 1,
                                             len(pitch_universe),
                                             target_index)
        if tuplet_type == '4':
            melodic_fragment = PondFragment()
            note_duration = 16
        else:
            melodic_fragment = PondTuplet(*self.tuplet_initializers[tuplet_type],
                                          group_duration=4)
            note_duration = 8 if tuplet_type == '3' else 16
        for i in range(silence_number):
            new_silence = PondNote(-1, note_duration)
            new_silence.make_rest()
            melodic_fragment.append_fragment(new_silence)
        for i in range(note_number):
            idx = index_route[i]
            new_note = PondNote(pitch_universe[idx],
                                duration=note_duration)
            if i == 0:
                new_note.dynamic = self.dynamic
                new_note.phrase_data('begin')
            if i == 1:
                new_note.expressions = Dynamics.crescendo_hairpin
            if i == note_number - 1:
                new_note.phrase_data('end')
            melodic_fragment.append_fragment(new_note)
        fragment.append_fragment(melodic_fragment)
        target_pitch = pitch_universe[target_index]
        if extension_type == 0:
            bonus_fragment = self.long_glissando(duration=2,
                                                 start_pitch=target_pitch)
        elif extension_type == 1:
            note_duration = choice(self.repeat_durations)
            bonus_fragment = self.compose_repeated(target_pitch, 2, note_duration, volume)
        else:
            bonus_fragment = PondNote(target_pitch, 6,
                                      articulation=Articulations.accent)
        if self.dynamic == Dynamics.fortissimo:
            dynamic = Dynamics.custom_dynamic("f", 3)
        else:
            dynamic = Dynamics.fortissimo
        bonus_fragment.get_note(0).dynamic = dynamic
        fragment.append_fragment(bonus_fragment)
        return fragment

    @classmethod
    def build_index_route(cls, note_amount, max_index, target_index=None):
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
        if target_index is not None and target_index != index_route[-1]:
            diff = target_index - index_route[-1]
            addition = diff // abs(diff)
            for idx in range(len(index_route)):
                index = index_route[idx]
                for _ in range(abs(diff)):
                    index = cls.next_index_number(index, addition,
                                                  max_index)
                index_route[idx] = index
        return index_route

    @staticmethod
    def next_index_number(current, addition, max_index):
        if 0 <= current + addition < max_index:
            return current + addition
        else:
            return current - addition

    def compose_trill_fragment(self, pitch_universe, duration=4,
                               volume=2., tuplet_type=4, extended=False,
                               start_pitch=None):
        duration -= int(extended)
        if not start_pitch:
            multiplier = volume + ((1 - volume) / 2)
            size = len(pitch_universe) - 2
            max_index = int(multiplier * size)
            start_idx = randint(0, max_index)
            trill_idx = start_idx + 1
            start_pitch, trill_pitch = pitch_universe[start_idx], pitch_universe[trill_idx]
        else:
            start_idx = pitch_universe.index(start_pitch)
            trill_idx = start_idx + 1
            trill_pitch = pitch_universe[trill_idx]
        fragment = PondFragment()
        start_phrase = PondFragment()
        if start_idx >= tuplet_type + 1 and duration > 2:
            notes_fragment = PondPhrase()
            start_phrase.append_fragment(PondNote.create_rest(16))
            phrase_idx = min(5, start_idx // 2)
            for idx in range(phrase_idx, start_idx):
                note_duration = 8 if tuplet_type == 3 else 16
                new_note = PondNote(pitch_universe[idx], duration=note_duration)
                notes_fragment.append_fragment(new_note)

            start_phrase.append_fragment(notes_fragment)
            start_phrase.ordered_notes()[0].dynamic = Dynamics.crescendo_hairpin
        fragment.append_fragment(start_phrase)
        start_position = start_phrase.real_duration % 1
        start_duration = 1 - start_position
        remaining_duration = duration - start_phrase.real_duration
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
            remaining_duration = 1 - (fragment.real_duration % 1)
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
        else:
            rest = PondNote.create_rest(4)
            rest.trill_marks(False)
            fragment.append_fragment(rest)
        return fragment

    @classmethod
    def compose_repeated(cls, repeated_pitch, duration,
                         note_duration,
                         volume=0., extended=False):
        note_number = int(duration // note_duration)
        fragment = PondFragment()
        duration -= int(extended)
        try:
            pond_duration = DurationInterface.get_pond_duration(note_duration)
            for _ in range(note_number):
                new_note = PondNote(repeated_pitch, duration=pond_duration,
                                    articulation=Articulations.staccato)
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

    def compose_glissando(self, start_pitch, duration, volume=0.,
                          extended=False):
        fragment = PondFragment()
        start_position = choice([0., 0.25, 0.5, 0.75])
        if extended:
            start_position %= 0.5
        silence = self.compose_silence(start_position)
        fragment.append_fragment(silence)
        gliss_fragment = self.long_glissando(start_pitch, duration, start_position)
        gliss_fragment.ordered_notes()[0].dynamic = self.dynamic
        fragment.append_fragment(gliss_fragment)
        if extended:
            duration = fragment.real_duration
            new_start = (duration + start_position + 0.5) % 1
            fragment.append_fragment(self.compose_silence(0.5))
            jump = randint(1, 2 + int(volume) * 3)
            new_glissando = self.long_glissando(start_pitch + jump, duration, new_start)
            fragment.append_fragment(new_glissando)

        assert fragment.real_duration < 6.1, f"{extended}, {start_position}"
        return fragment

    @classmethod
    def long_glissando(cls, start_pitch, duration=3, start_position=0):
        duration -= start_position
        initial_duration = 1 - start_position

        fragment = PondFragment()
        duration_list = DurationInterface.get_duration_list(duration,
                                                            start=initial_duration % 1,
                                                            max_duration=1)
        end_pitch = PondPitch.from_absolute_int(start_pitch - 2)
        for note_duration in duration_list:
            new_note = PondNote(start_pitch, duration=note_duration)
            fragment.append_fragment(new_note)

        LilypondScripts.glissando(fragment.get_note(0), True)
        last_note = fragment.ordered_notes()[-1]
        last_note.pitch = end_pitch
        last_note.hide_notehead()
        last_note.ignore_accidental()
        LilypondScripts.glissando(last_note, False)
        return fragment

    def compose_noise_note(self, duration, pitch):
        duration_list = DurationInterface.get_duration_list(duration,
                                                            simple=True,
                                                            max_duration=1)
        fragment = PondFragment()
        for duration in duration_list:
            new_note = PondNote(pitch, duration, tie=True)
            LilypondScripts.make_square(new_note)
            fragment.append_fragment(new_note)
        first = fragment.get_note(0)
        first.dynamic = self.dynamic
        first.expressions = Dynamics.crescendo_hairpin
        fragment.get_note(len(fragment) // 2).expressions = Dynamics.diminuendo_hairpin
        last = fragment.get_note(-1)
        last.make_tie(False)
        last.expressions = MiscMarks.end_tag
        return fragment


class ComposerEmpty(ComposerBase):
    instructions = {'english': '"Breathe naturally. '
                               'Expel air with force through instrument."',
                    'español': '"Respira naturalmente. '
                               'Expulsa el aire con fuerza a través del instrumento."'}

    def __init__(self, instruments=None, language='english'):
        super().__init__(instruments)
        self.language = language

    def set_dynamic(self, direction, volume):
        self.dynamic = Dynamics.mezzo_forte

    def compose(self, *args, **kwargs):
        lines = []
        for _ in range(3):
            new_line = self.compose_instrument()
            lines.append(new_line)
        return lines

    @classmethod
    def compose_instrument(cls, measure_length=6):
        fragment = PondFragment()
        silence_duration = DurationInterface.get_pond_duration((measure_length - 4) // 2)
        for _ in range(2):
            new_rest = PondNote.create_rest(silence_duration)
            new_rest.hide_note()
            fragment.append_fragment(new_rest)
        new_note = PondNote(11, "1")
        LilypondScripts.make_slash(new_note)
        fragment.insert_fragment(1, new_note)
        return fragment


class ComposerA(ComposerBase):
    def __init__(self, instruments=None):
        super().__init__(instruments)
        self.dynamic = Dynamics.pianissimo

    def set_dynamic(self, direction, volume):
        dyn_dict = {0: 0,
                    1: 0,
                    2: 1,
                    3: 2,
                    4: 3,
                    5: 4}
        dynamic = dyn_dict[direction]
        if volume > 0.6:
            dynamic += 1
        self.dynamic = self.dynamics_data[dynamic]

    @classmethod
    def get_tuplet_weights(cls, volume):
        tuplet_weights = {'3': 1 - volume,
                          '4': 0.8 - (volume * 0.8),
                          '5': 0.2 + (volume * 0.8),
                          '6': 0 + volume
                          }

        return tuplet_weights

    def compose(self, pitch_universe, direction, volume, voice_data) -> dict:
        lines = {}
        used_tuplets = []
        instrument_order = self.instrument_order()
        pitch = 0
        min_duration = max(2, direction)
        for voice_type, silence in voice_data:
            instrument = instrument_order.pop()
            temp_universe = self.get_voice_pitch_universe(pitch_universe,
                                                          instrument)
            voice_pitch_universe = self.get_pitch_universe(temp_universe, volume)
            extended = randint(3, 5) < direction
            climax = True if direction > 3 else False
            tuplet_type = self.tuplet_type(used_tuplets, volume)
            if voice_type == 1:
                used_tuplets.append(tuplet_type)
            elif voice_type == 2:
                mode_pitch = self.get_mode(lines)
                pitch = mode_pitch
                if pitch == voice_pitch_universe[-1]:
                    pitch = voice_pitch_universe[-2]
                if pitch not in voice_pitch_universe:
                    pitch = voice_pitch_universe[1]
            new_fragment = self.compose_instrument(voice_pitch_universe, volume, voice_type,
                                                   silence, min_duration, climax,
                                                   tuplet_type, pitch, extended)
            lines[instrument] = new_fragment

        return lines

    def tuplet_type(self, used, volume):
        def tuplet_filter(tuplet):
            if tuplet[0] in used:
                return False
            return True

        filtered = filter(tuplet_filter, self.get_tuplet_weights(volume).items())
        types, weights = zip(*filtered)
        return choices(types, weights=weights)[0]

    @classmethod
    def get_pitch_universe(cls, pitch_universe, volume):
        max_index = len(pitch_universe) - 1
        index_range = min(max(5,
                              int(max_index * volume * 1.5)),
                          max_index)
        max_start = min(max_index - index_range, int(max_index * volume) + 1)
        start = randint(0, max_start)
        return pitch_universe[start: start + index_range]

    @classmethod
    def get_mode(cls, lines):
        lines = list(map(lambda x: x.ordered_notes(), lines.values()))
        all_notes = filter(lambda x: not x.is_rest(),
                           lines[0] + lines[1])
        all_pitches = list(map(lambda x: x.absolute_int, all_notes))
        return mode(all_pitches)

    def compose_instrument(self, pitch_universe, volume,
                           voice_type=1, silence=0, min_duration=3, climax=False,
                           tuplet_type="4", pitch=0, extended=False):
        if voice_type == 0:
            if not extended:
                return ComposerEmpty.compose_instrument()
            else:
                return self.compose_silence(6.)
        remaining_duration = 6 - silence
        duration = randint(min_duration, remaining_duration)
        if voice_type == 2:
            duration = min(duration, 5 - silence)
            music_fragment = self.compose_trill_fragment(pitch_universe,
                                                         volume=volume,
                                                         duration=duration,
                                                         extended=extended,
                                                         start_pitch=pitch)
        else:
            music_fragment = self.compose_melodic_fragment(pitch_universe,
                                                           duration=duration,
                                                           climax=climax,
                                                           tuplet_type=tuplet_type,
                                                           extended=extended,
                                                           volume=volume)
        if silence:
            silence_fragment = self.compose_silence(silence)
            music_fragment.insert_fragment(0, silence_fragment)
        assert music_fragment.real_duration <= 6, (f"{duration}, {silence}, "
                                                   f"{volume}, {music_fragment.real_duration}")

        return self.complete_silence(music_fragment, True)


class ComposerB(ComposerBase):

    def __init__(self, instruments=None):
        super().__init__(instruments)
        self.dynamic = Dynamics.forte

    def set_dynamic(self, direction, volume):
        dyn_dict = {0: 4,
                    1: 4,
                    2: 2,
                    3: 2,
                    4: 3,
                    5: 4}
        dynamic = dyn_dict[direction]
        if volume > 0.6:
            dynamic += 1
        self.dynamic = self.dynamics_data[dynamic]

    @staticmethod
    def volume_calculator(volume):
        return (sqrt(volume) / 3) - 0.5

    def compose(self, pitch_universe, direction, volume, voice_data) -> dict:
        lines = {}
        instrument_order = self.instrument_order()

        duration = max(2, min(5, randint(1, direction + 1)))
        volume = volume
        extended = randint(2, 4) < direction

        for voice_type, silence in voice_data:
            instrument = instrument_order.pop()
            voice_pitch_universe = self.get_voice_pitch_universe(pitch_universe,
                                                                 instrument)
            new_fragment = self.compose_instrument(voice_pitch_universe, duration,
                                                   voice_type, silence, volume,
                                                   extended)
            lines[instrument] = new_fragment

        return lines

    def compose_instrument(self, pitch_universe, duration, voice_type,
                           silence, volume=0., extended=False):
        duration = min(6 - silence, duration)
        if voice_type == 0:
            if extended:
                tuplet_type = choice(["3", "4", "5"])
                duration = max(4, duration)
                fragment = self.compose_melodic_fragment(pitch_universe, duration - 1, True,
                                                         tuplet_type, False, volume)
                return self.complete_silence(fragment)
            return self.compose_silence(6.)
        if silence:
            start_silence = self.compose_silence(silence)
        else:
            start_silence = PondFragment()
        if voice_type == 1:
            max_index = min(len(pitch_universe) - 3, abs(int(volume * len(pitch_universe)))) + 2
            main_pitch = choice(pitch_universe[:max_index])
            note_duration_idx = randint(0, min(6, duration + 1))
            note_duration = self.repeat_durations[note_duration_idx]
            new_fragment = self.compose_repeated(main_pitch, duration - 1,
                                                 note_duration, volume,
                                                 extended)
        else:
            if extended:
                duration = 2
            middle_point = len(pitch_universe) // 2
            main_pitch = choice(pitch_universe[-middle_point:-1])
            new_fragment = self.compose_glissando(main_pitch, duration,
                                                  volume, extended)

        new_fragment.insert_fragment(0, start_silence)
        return self.complete_silence(new_fragment)


class ComposerC(ComposerBase):
    def __init__(self, instruments=None, language="english"):
        super().__init__(instruments)
        self.language = language

    def set_dynamic(self, direction, volume):
        dyn_dict = {0: 4,
                    1: 4,
                    2: 4,
                    3: 4,
                    4: 4,
                    5: 4}
        dynamic = dyn_dict[direction]
        if volume > 0.5:
            dynamic += 1
        self.dynamic = self.dynamics_data[dynamic]

    def compose(self, pitch_universe, direction, volume, voice_data) -> dict:
        lines = {}
        instrument_order = self.instrument_order()
        silence = 0
        shared_universe = self.shared_pitch_universe(pitch_universe,
                                                     self.instruments.values())
        max_index = len(shared_universe) - 1
        start_pitch_index = max_index - int(direction * 1.5)
        start_pitch = shared_universe[start_pitch_index]
        pitch_index = pitch_universe.index(start_pitch)
        for _, fragment_type in voice_data:
            instrument = instrument_order.pop()
            voice_pitch_universe = self.get_voice_pitch_universe(pitch_universe,
                                                                 instrument)
            new_fragment = self.compose_instrument(voice_pitch_universe, volume,
                                                   fragment_type, silence,
                                                   pitch_index)
            pitch_index -= 1
            silence += 1
            lines[instrument] = new_fragment
        return lines

    @classmethod
    def shared_pitch_universe(cls, pitch_universe, instruments):
        universe = pitch_universe.copy()
        for instrument in instruments:
            universe = instrument.limit_pitch_universe(universe)
        return universe

    def compose_instrument(self, pitch_universe, volume, fragment_type,
                           silence, main_index):
        fragment = PondFragment()
        silence_fragment = self.compose_silence(silence)
        duration = 3
        if fragment_type == 3:
            return ComposerEmpty.compose_instrument(8)
        tuplet_type = choice(["3", "4", "5", "6"])
        melodic_fragment = self.compose_target_melodic_fragment(pitch_universe, main_index,
                                                                duration, tuplet_type,
                                                                volume, fragment_type)
        fragment.append_fragment(silence_fragment)
        fragment.append_fragment(melodic_fragment)
        return self.complete_silence(fragment, max_duration=8)


class ComposerD(ComposerBase):
    noise_pitches = [0, 4, 7]

    def __init__(self, instruments=None):
        super().__init__(instruments)

    def set_dynamic(self, direction, volume):
        dyn_dict = {0: 1,
                    1: 1,
                    2: 1,
                    3: 0,
                    4: 0,
                    5: 0}
        dynamic = dyn_dict[direction]
        self.dynamic = self.dynamics_data[dynamic]

    def compose(self, pitch_universe, direction, volume, voice_data) -> dict:
        lines = {}
        instrument_order = self.instrument_order()
        max_duration = max(3, 7 - direction)
        max_index = max(4, int(len(pitch_universe) * volume))
        for voice_type, silence in voice_data:
            instrument = instrument_order.pop()
            voice_pitch_universe = self.get_voice_pitch_universe(pitch_universe,
                                                                 instrument)
            duration = randint(3, max_duration)
            new_fragment = self.compose_instrument(voice_pitch_universe[:max_index],
                                                   duration, volume,
                                                   silence, voice_type)
            lines[instrument] = new_fragment
        return lines

    def compose_instrument(self, pitch_universe, duration, volume,
                           silence, voice_type):
        fragment = PondFragment()
        if voice_type == 0:
            max_idx = min(3, 1 + int(3 * volume))
            available = self.noise_pitches[:max_idx]
            pitch = choice(available)
            melodic_fragment = self.compose_noise_note(duration, pitch)
        elif voice_type == 1:
            tuplet_type = choice(["4", "5", "6"])
            melodic_fragment = self.compose_melodic_fragment(pitch_universe,
                                                             duration,
                                                             tuplet_type=tuplet_type,
                                                             volume=volume,
                                                             reverse=True)
        else:
            return ComposerEmpty.compose_instrument(8)
        silence_fragment = self.compose_silence(silence)
        fragment.append_fragment(silence_fragment)
        fragment.append_fragment(melodic_fragment)

        return self.complete_silence(fragment, max_duration=8)
