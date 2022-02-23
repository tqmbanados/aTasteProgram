from PyQt5.QtWidgets import (QLabel, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy,
                             QGridLayout)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from os import path
from parameters import SCORE_IMAGE_PATH, window_geometry
from frontend.QPondScores import ScoreLabel
from time import sleep


class PyPondWindow(QWidget):
    signal_get_next = pyqtSignal()
    signal_write_score = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setGeometry(*window_geometry)
        self.music_labels = {}
        self.next = QPushButton("Next", self)
        self.end = QPushButton("End", self)
        self.init_gui()
        self.__next = 0

    def next_label(self):
        current = self.__next
        self.__next += 1
        if self.__next > 3:
            self.__next = 0
        return current

    def hide_label_idx(self):
        to_delete = self.__next - 3
        if to_delete < 0:
            to_delete = 4 + to_delete
        return to_delete

    def init_gui(self):
        score_layout = QGridLayout()
        for idx, x, y in [(0, 0, 0), (1, 0, 1), (2, 1, 0), (3, 1, 1)]:
            new_music_label = ScoreLabel(idx, parent=self)
            size_policy = QSizePolicy()
            size_policy.setRetainSizeWhenHidden(True)
            new_music_label.setSizePolicy(size_policy)
            self.music_labels[idx] = new_music_label
            score_layout.addWidget(new_music_label, x, y)

        h_box_button = QHBoxLayout()
        h_box_button.addStretch()
        h_box_button.addWidget(self.next)
        h_box_button.addWidget(self.end)
        h_box_button.addStretch()

        hbox_main = QHBoxLayout()
        hbox_main.addLayout(score_layout, 5)
        hbox_main.addLayout(h_box_button, 1)

        self.setLayout(hbox_main)
        self.setStyleSheet("background-color: white")
        self.next.clicked.connect(self.get_next)
        self.end.clicked.connect(self.write_score)

    @pyqtSlot()
    def get_next(self):
        self.signal_get_next.emit()

    @pyqtSlot()
    def update_label(self):
        idx_hide = self.hide_label_idx()
        idx_update = self.next_label()
        label_hide = self.music_labels[idx_hide]
        label_hide.hide()

        label_update = self.music_labels[idx_update]
        image_path = path.join(*SCORE_IMAGE_PATH)
        label_update.update_label(image_path)
        label_update.show()

    def write_score(self):
        self.signal_write_score.emit()
        self.close()
