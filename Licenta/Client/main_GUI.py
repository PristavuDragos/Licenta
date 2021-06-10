import json
import sys

from PyQt5.QtGui import QIcon

import client_connection_manager
import main_client
from PyQt5 import QtGui
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QStackedWidget
from qt_material import apply_stylesheet
import feed_receiver
from Client.CustomGUI import session_page
from worker_thread import Worker
from CustomGUI import main_page

settings = None
main_window = None
qt_main_loop = None


def init_settings():
    global settings
    with open("../Settings/ui_settings.json", "r") as settings_file:
        settings = json.load(settings_file)


class MainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        main_client.init_settings()
        main_client.set_window(self)
        self.worker_threads = QThreadPool()
        self.muted_icon = QIcon("../Assets/Images/mic_off.png")
        self.unmuted_icon = QIcon("../Assets/Images/mic_on.png")
        self.cam_on_icon = QIcon("../Assets/Images/cam_on.png")
        self.cam_off_icon = QIcon("../Assets/Images/cam_off.png")
        self.left_arrow_icon = QIcon("../Assets/Images/left_arrow.png")
        self.right_arrow_icon = QIcon("../Assets/Images/right_arrow.png")
        self.setStyleSheet('QLabel { color: #BAC0F0; font-family: Courier; font-style: bold; font-size: 12px}'
                           'QPushButton {background-color: #0C2237}')
        self.window_title = settings["window_title"]
        self.window_width = settings["window_width"]
        self.window_height = settings["window_height"]
        self.setWindowTitle(self.window_title)
        self.setMinimumHeight(settings["min_window_height"])
        self.resize(self.window_width, self.window_height)
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.main_page_widget = main_page.MainPageWidget(main_client.client_settings, self)
        self.central_widget.addWidget(self.main_page_widget)
        self.session_page_widget = session_page.SessionPageWidget(self)
        self.central_widget.addWidget(self.session_page_widget)
        self.switch_to_session_screen()
        self.participants = []
        # self.video_labels = {}
        # self.label_grid = QGridLayout(self)
        self.init_ui()

    def show_video_feed(self, frame_data):
        self.session_page_widget.show_video_feed(frame_data)

    def set_participant_list(self, participant_list):
        self.participants = participant_list
        self.update_grid.clicked.emit()

    def set_grid(self):
        counter = 0
        self.reset_grid()
        for it in self.participants:
            label = QLabel(self)
            label.resize(320, 240)
            default_label = QtGui.QPixmap(main_client.settings["video_default_width"],
                                          main_client.settings["video_default_height"])
            default_label.fill(QtGui.QColor("black"))
            label.setPixmap(default_label)
            self.video_labels[it] = label
            self.label_grid.addWidget(label, counter // 4, counter % 4)
            counter += 1

    def reset_grid(self):
        while self.label_grid.count():
            item = self.label_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def switch_to_session_screen(self):
        self.central_widget.setCurrentWidget(self.session_page_widget)

    def switch_to_home_page(self):
        self.central_widget.setCurrentWidget(self.main_page_widget)

    def start_packet_receiver(self):
        worker = Worker(client_connection_manager.packet_receiver)
        worker.signals.update.connect(self.set_participant_list)
        self.start_video_packet_processor()
        self.worker_threads.start(worker)

    def start_video_packet_processor(self):
        worker = Worker(feed_receiver.process_video_packets)
        worker.signals.send_data.connect(self.show_video_feed)
        self.worker_threads.start(worker)

    def test_button_action(self):
        self.start_packet_receiver()
        self.user_button.hide()
        self.test_button.hide()
        main_client.connect_to_server_test("0")

    def user_button_action(self):
        # self.user_button.hide()
        self.start_packet_receiver()
        self.test_button.hide()
        main_client.connect_to_server("0")

    def closeEvent(self, event):
        main_client.close()

    def init_ui(self):
        self.show()


def start_ui():
    global main_window
    global qt_main_loop
    qt_main_loop = QApplication([])
    apply_stylesheet(qt_main_loop, theme='dark_blue.xml')
    main_window = MainGUI()
    sys.exit(qt_main_loop.exec_())
