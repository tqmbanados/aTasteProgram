from PyQt5.QtWidgets import QApplication

from backend.PyPondWriter import PyPondWriter
from front_end.PyPondWindow import PyPondWindow
from twitch_bot.bot import Messenger
import sys
import parameters as p
from private_parameters import channel_name, url


if __name__ == "__main__":
    def hook(type_, value, traceback):
        print(value, type_)
        print(traceback)
    sys.__excepthook__ = hook

    app = QApplication([])
    window = PyPondWindow(p.BEAT_DURATION_MS)
    render = PyPondWriter(p.BEAT_DURATION_MS, p.USE_API, url)
    bot_messenger = Messenger(p.COMMANDS, channel_name)

    window.signal_get_next.connect(render.render_image)
    window.signal_write_score.connect(render.write_score)
    window.signal_update_value.connect(render.update_values)
    bot_messenger.signal_command.connect(render.update_values)
    bot_messenger.signal_start.connect(render.begin)
    bot_messenger.signal_start.connect(window.start)
    render.file_completed.connect(window.update_label)

    bot_messenger.start()
    window.show()
    sys.exit(app.exec())
