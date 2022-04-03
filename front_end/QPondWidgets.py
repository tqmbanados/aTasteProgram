from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QPixmap, QColor, QPainter, QFont
from PyQt5.QtCore import QTimer, QThread, pyqtSlot
from time import sleep


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


class Metronome(QLabel):
    def __init__(self, beat_duration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.countdown = QLabel(" ", parent=self)
        self.beeper = Beeper(parent=self)
        self.timer = QTimer()

        self.beat_number = 6
        self.beat_duration = beat_duration
        self.__current_beat = 0
        #self.init_gui()

    def current_beat(self):
        if self.__current_beat >= self.beat_number:
            self.__current_beat = 0
        self.__current_beat += 1
        return self.__current_beat

    def init_gui(self):
        self.timer.setInterval(self.beat_duration)
        self.timer.timeout.connect(self.beat)
        font = QFont("Times", 18, QFont.Bold)
        self.countdown.setFont(font)

        beeper_box = QHBoxLayout()
        beeper_box.addStretch()
        beeper_box.addWidget(self.beeper)
        beeper_box.addStretch()

        number_box = QHBoxLayout()
        number_box.addStretch()
        number_box.addWidget(self.countdown)
        number_box.addStretch()

        vbox = QVBoxLayout()
        vbox.addLayout(beeper_box)
        vbox.addStretch()
        vbox.addLayout(number_box)
        self.setLayout(vbox)

        self.timer.start()
        self.beeper.start()
        self.countdown.hide()

    def beat(self):
        current_beat = self.current_beat()
        remaining = (self.beat_number - current_beat) + 1
        if remaining <= 4:
            self.countdown.setText(str(remaining))
        else:
            self.countdown.setText(" ")
        self.beeper.beep()

    def new_measure(self, time):
        self.beat_duration = time
        self.__current_beat = 0


class Beeper(QLabel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._alpha = 255
        self.thread = BeeperThread(self)
        self.setMinimumSize(50, 50)

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = min(max(0, value), 255)
        self.update()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QColor(255, 0, 0, self.alpha))
        painter.drawEllipse(event.rect())
        painter.end()

    def beep(self):
        self.alpha = 255

    def start(self):
        self.thread.start()


class BeeperThread(QThread):
    def __init__(self, beeper, *args, **kwargs):
        super().__init__()
        self.beeper = beeper

    def run(self):
        while True:
            self.beeper.alpha -= 20
            sleep(0.04)

