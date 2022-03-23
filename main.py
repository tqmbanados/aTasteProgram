from PyQt5.QtWidgets import QApplication

from backend.PyPondWriter import PyPondWriter
from front_end.PyPondWindow import PyPondWindow
from twitch_bot.bot import Messenger
import sys
import parameters as p

if __name__ == "__main__":
    def hook(type_, value, traceback):
        print(value, type_)
        print(traceback)
    sys.__excepthook__ = hook

    app = QApplication([])
    window = PyPondWindow(p.beat_duration_ms)
    render = PyPondWriter(p.measure_duration_ms)
    bot_messenger = Messenger(p.commands)

    window.signal_get_next.connect(render.render_image)
    window.signal_write_score.connect(render.write_score)
    window.signal_update_value.connect(render.update_values)
    bot_messenger.signal_command.connect(render.update_values)
    bot_messenger.signal_start.connect(render.begin)
    render.file_completed.connect(window.update_label)

    bot_messenger.start()
    window.show()
    sys.exit(app.exec())
