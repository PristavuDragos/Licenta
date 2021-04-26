import json
import sys
import numpy as np
import main_client
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap, QImage

settings = None
main_window = None
qt_main_loop = None


def init_settings():
    global settings
    with open("../Settings/ui_settings.json", "r") as settings_file:
        settings = json.load(settings_file)


class MainGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.video_label = QLabel(self)
        self.window_title = settings["window_title"]
        self.window_width = settings["window_width"]
        self.window_height = settings["window_height"]

        self.init_ui()

    def show_video_feed(self, frame):
        qt_frame = QImage(frame.data, frame.shape[1], frame.shape[0],
                          QImage.Format_RGB888)
        qt_frame = QPixmap.fromImage(qt_frame)
        pixmap = QPixmap(qt_frame)
        self.video_label.resize(frame.shape[1], frame.shape[0])
        self.video_label.setPixmap(pixmap)

    def init_ui(self):
        self.setWindowTitle(self.window_title)
        self.resize(self.window_width, self.window_height)
        self.show()

    def closeEvent(self, event):
        main_client.close()


def start_ui():
    global main_window
    global qt_main_loop
    qt_main_loop = QApplication([])
    main_window = MainGUI()
    sys.exit(qt_main_loop.exec_())
