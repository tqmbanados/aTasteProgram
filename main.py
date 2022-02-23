from PyQt5.QtWidgets import QApplication

from backend.PyPondWriter import PyPondWriter
from frontend.PyPondWindow import PyPondWindow
import sys

if __name__ == "__main__":
    def hook(type, value, traceback):
        print(value, type)
        print(traceback)
    sys.__excepthook__ = hook

    app = QApplication([])
    window = PyPondWindow()
    render = PyPondWriter()
    window.signal_get_next.connect(render.render_image)
    window.signal_write_score.connect(render.write_score)
    render.file_completed.connect(window.update_label)
    window.show()
    sys.exit(app.exec())
