from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from os import path
from parameters import SCORE_IMAGE_PATH, window_geometry


class PyPondWindow(QWidget):
    signal_get_next = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setGeometry(*window_geometry)
        self.music_label = QLabel(parent=self)
        self.next = QPushButton("Next", self)
        self.init_gui()

    def init_gui(self):
        h_box = QHBoxLayout()
        h_box.addStretch(1)
        h_box.addWidget(self.music_label, 2)
        h_box.addStretch(1)

        h_box_button = QHBoxLayout()
        h_box_button.addStretch()
        h_box_button.addWidget(self.next)
        h_box_button.addStretch()

        v_box = QVBoxLayout()
        v_box.addStretch()
        v_box.addLayout(h_box)
        v_box.addStretch()
        v_box.addLayout(h_box_button)
        v_box.addStretch()

        self.setLayout(v_box)
        self.setStyleSheet("background-color: white")
        self.next.clicked.connect(self.get_next)



    @pyqtSlot()
    def get_next(self):
        self.signal_get_next.emit()

    @pyqtSlot()
    def update_label(self):
        image_path = path.join(*SCORE_IMAGE_PATH)
        pixmap = QPixmap(image_path)
        self.music_label.setPixmap(pixmap)
