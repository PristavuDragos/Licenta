import json
import sys
import numpy as np
from PyQt5 import QtGui

import main_client
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGridLayout
from PyQt5.QtGui import QPixmap, QImage

settings = None
main_window = None
qt_main_loop = None
participants = None


def init_settings():
    global settings
    with open("../Settings/ui_settings.json", "r") as settings_file:
        settings = json.load(settings_file)


class MainGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.update_grid = QPushButton("Baga", self)
        self.video_labels = {}
        self.label_grid = QGridLayout(self)
        self.test_button = QPushButton(self)
        self.user_button = QPushButton(self)
        self.window_title = settings["window_title"]
        self.window_width = settings["window_width"]
        self.window_height = settings["window_height"]
        self.init_ui()

    def show_video_feed(self, byte_frame, participant_id):
        if participant_id in self.video_labels.keys():
            frame = np.frombuffer(byte_frame, dtype="B").reshape(240, 320, 3)
            qt_frame = QImage(frame.data, frame.shape[1], frame.shape[0],
                              QImage.Format_RGB888)
            qt_frame = QPixmap.fromImage(qt_frame)
            pixmap = QPixmap(qt_frame)
            label = self.video_labels.get(participant_id)
            label.resize(frame.shape[1], frame.shape[0])
            label.setPixmap(pixmap)

    def set_participant_list(self, participant_list):
        global participants
        participants = participant_list
        self.update_grid.clicked.emit()

    def set_grid(self):
        counter = 0
        for it in participants:
            label = QLabel(self)
            label.resize(320, 240)
            default_label = QtGui.QPixmap(320, 240)
            default_label.fill(QtGui.QColor("black"))
            label.setPixmap(default_label)
            self.video_labels[it] = label
            self.label_grid.addWidget(label, counter // 3, counter % 3)
            counter += 1

    def test_button_action(self):
        self.user_button.hide()
        self.test_button.hide()
        main_client.connect_to_server_test()

    def user_button_action(self):
        # self.user_button.hide()
        self.test_button.hide()
        main_client.connect_to_server()

    def init_ui(self):
        main_client.init_settings()
        main_client.set_window(self)
        self.setWindowTitle(self.window_title)
        self.resize(self.window_width, self.window_height)
        self.test_button.setText("Join as test")
        self.test_button.move(800, 600)
        self.test_button.clicked.connect(self.test_button_action)
        self.test_button.show()
        self.user_button.setText("Join as user")
        self.user_button.move(800, 650)
        self.user_button.clicked.connect(self.user_button_action)
        self.user_button.show()
        self.update_grid.clicked.connect(self.set_grid)
        self.update_grid.hide()
        self.setLayout(self.label_grid)
        self.show()

    def closeEvent(self, event):
        main_client.close()


def start_ui():
    global main_window
    global qt_main_loop
    qt_main_loop = QApplication([])
    main_window = MainGUI()
    sys.exit(qt_main_loop.exec_())
