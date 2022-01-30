from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap


class ScoreLabel(QWidget):
    def __init__(self, id_, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_ = id_
        self.score_label = QLabel(parent=self)
        self.init_gui()

    def init_gui(self):
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.score_label, 3)
        hbox.addStretch(1)
        self.setLayout(hbox)

    def update_label(self, image_path):
        pixmap = QPixmap(image_path)
        self.score_label.setPixmap(pixmap)
