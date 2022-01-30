from PyQt5.QtWidgets import QApplication

from backend import PyPondWriter
from frontend import PyPondWindow
import sys

if __name__ == "__main__":
    def hook(type, value, traceback):
        print(type)
        print(traceback)
    sys.__excepthook__ = hook

    app = QApplication([])
    window = PyPondWindow()
    render = PyPondWriter()
    window.signal_get_next.connect(render.render_image)
    render.file_completed.connect(window.update_label)
    window.show()
    sys.exit(app.exec())
