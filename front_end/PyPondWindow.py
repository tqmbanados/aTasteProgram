from os import path
from random import uniform

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy,
                             QGridLayout, QLabel)
from PyQt5.QtGui import QFont

from front_end.QPondWidgets import ScoreLabel, Metronome
from parameters import SCORE_IMAGE_PATH, WINDOW_GEOMETRY
from time import sleep


class PyPondWindow(QWidget):
    signal_get_next = pyqtSignal(bool)
    signal_write_score = pyqtSignal()
    signal_update_value = pyqtSignal(dict)

    def __init__(self, beat_duration, image_path, *args, **kwargs):
        super().__init__()
        self.setGeometry(*WINDOW_GEOMETRY)
        self.music_labels = {}
        self.image_path = image_path
        self.next = QPushButton("Next", self)
        self.advance = QPushButton("Advance", self)
        self.end = QPushButton("End", self)
        self.auto = QPushButton("Auto-generate", self)
        self.acting = QLabel("", self)
        self.acting_script = QLabel("", self)
        self.metronome = Metronome(beat_duration, parent=self)
        self.grid_based = True
        self.use_metronome = False
        self.hide_score_label = False
        self.init_gui()
        self.__next = 0

    def next_label(self):
        max_idx = 3 if self.grid_based else 1
        current = self.__next
        self.__next += 1
        if self.__next > max_idx:
            self.__next = 0
        return current

    def hide_label_idx(self):
        to_delete = self.__next - 3
        if to_delete < 0:
            to_delete = 4 + to_delete
        return to_delete

    def init_gui(self):
        # Code for Grid based score_layout
        """score_layout = QGridLayout()
        for idx, x, y in [(0, 0, 0), (1, 0, 1), (2, 1, 0), (3, 1, 1)]:
            new_music_label = ScoreLabel(idx, parent=self)
            size_policy = QSizePolicy()
            size_policy.setRetainSizeWhenHidden(True)
            new_music_label.setSizePolicy(size_policy)
            self.music_labels[idx] = new_music_label
            score_layout.addWidget(new_music_label, x, y)"""
        # Code for Vertical based score_layout
        score_layout = QVBoxLayout()
        self.grid_based = False
        for idx in range(2):
            new_music_label = ScoreLabel(idx, parent=self)
            if self.hide_score_label:
                new_music_label.hide()
            self.music_labels[idx] = new_music_label
            score_layout.addWidget(new_music_label, 2)
            score_layout.addStretch(1)

        if not self.use_metronome:
            self.metronome.hide()

        if self.hide_score_label:
            a, b, size = 0, 5, 100
        else:
            a, b, size = 5, 1, 20

        font = QFont()
        font.setPointSize(size)
        self.acting.setFont(font)
        self.acting_script.setFont(font)

        h_box_button = QVBoxLayout()
        h_box_button.addStretch()
        h_box_button.addWidget(self.metronome)
        h_box_button.addStretch()
        h_box_button.addWidget(self.acting_script)
        h_box_button.addWidget(self.acting)
        h_box_button.addWidget(self.next)
        h_box_button.addWidget(self.advance)
        h_box_button.addWidget(self.end)
        h_box_button.addWidget(self.auto)
        h_box_button.addStretch()

        hbox_main = QHBoxLayout()
        hbox_main.addLayout(score_layout, a)
        hbox_main.addLayout(h_box_button, b)

        self.setLayout(hbox_main)
        self.setStyleSheet("background-color: white")
        self.next.clicked.connect(self.get_next)
        self.end.clicked.connect(self.write_score)
        self.auto.clicked.connect(self.automatic_score)
        self.advance.clicked.connect(self.next_direction)

    @pyqtSlot()
    def next_direction(self):
        data = {'VOLUME': 0,
                'DIRECTION': 1}
        self.signal_update_value.emit(data)

    @pyqtSlot()
    def get_next(self):
        command = self.acting.text()
        self.signal_update_value.emit({'VOLUME': uniform(0.05, 6),
                                       'DIRECTION': 0,
                                       'COMMAND': command})
        self.signal_get_next.emit(True)

    @pyqtSlot()
    def start(self):
        if self.use_metronome:
            self.metronome.init_gui()
        else:
            self.metronome.hide()

    @pyqtSlot(int, tuple)
    def update_label(self, measure_time, acting_data):
        if self.grid_based:
            idx_hide = self.hide_label_idx()
            label_hide = self.music_labels[idx_hide]
            label_hide.hide()

        action, stage = acting_data
        self.acting_script.setText(stage)
        self.acting.setText(action)
        idx_update = self.next_label()
        label_update = self.music_labels[idx_update]
        image_path = self.image_path
        label_update.update_label(image_path)
        self.metronome.new_measure(measure_time)
        if not self.hide_score_label:
            label_update.show()

    def write_score(self):
        self.signal_write_score.emit()

    def automatic_score(self):
        new_thread = Generator(self.signal_get_next, self.signal_write_score,
                               self.signal_update_value, self)
        new_thread.start()


class Generator(QThread):
    def __init__(self, signal_next, signal_write,
                 signal_update, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signal_next = signal_next
        self.signal_write = signal_write
        self.signal_update = signal_update

    def run(self):
        volume_list = [uniform(0.05, 5) for _ in range(250)]
        increase_direction = -1
        for volume in volume_list:
            direction = not increase_direction
            increase_direction += 1
            if increase_direction > 4:
                increase_direction = 0
            self.signal_update.emit({'VOLUME': volume,
                                     'DIRECTION': direction,
                                     'COMMAND': "mirar_al_frente"})
            self.signal_next.emit(False)
            sleep(5)

        self.signal_write.emit()
