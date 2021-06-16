import json
import sys
import time

from PyQt5.QtGui import QIcon

import client_connection_manager
import main_client
from PyQt5 import QtGui
from PyQt5.QtCore import QThreadPool, pyqtSignal
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QStackedWidget
from qt_material import apply_stylesheet
import feed_receiver
from Client.CustomGUI import session_page, gui_signals, disconnected_dialog
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
        self.sig = gui_signals.GUISignals()
        self.sig.switch_page.connect(self.switch_to_session_screen)
        self.sig.start_packet_receiver.connect(self.start_packet_receiver)
        self.window_title = settings["window_title"]
        self.window_width = settings["window_width"]
        self.window_height = settings["window_height"]
        self.setWindowTitle(self.window_title)
        self.setMinimumHeight(settings["min_window_height"])
        self.resize(self.window_width, self.window_height)
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.main_page_widget = main_page.MainPageWidget(main_client.client_settings, self.sig, self)
        self.central_widget.addWidget(self.main_page_widget)
        self.session_page_widget = session_page.SessionPageWidget(main_client.client_settings, self)
        self.central_widget.addWidget(self.session_page_widget)
        self.participants = []
        self.test_started = False
        self.elapsed_test_time = 0
        self.test_duration = 0
        self.test_upload_time = 0
        # self.video_labels = {}
        # self.label_grid = QGridLayout(self)
        self.init_ui()

    def update_settings(self):
        with open("client_settings.json", "r") as settings_file:
            client_settings = json.load(settings_file)
        return client_settings

    def show_video_feed(self, frame_data):
        self.session_page_widget.show_video_feed(frame_data)

    def set_participant_list(self, participant_list):
        self.participants = participant_list
        self.session_page_widget.set_participant_list(participant_list)

    def switch_to_session_screen(self, params):
        addresses = params[0]
        owner = params[1]
        self.session_page_widget.set_session_data(owner, main_client.client_settings["client_id"], params[2])
        self.session_page_widget.init_streams(main_client.settings, addresses)
        self.central_widget.setCurrentWidget(self.session_page_widget)

    def switch_to_home_page(self):
        self.central_widget.setCurrentWidget(self.main_page_widget)

    def start_packet_receiver(self, address):
        worker = Worker(client_connection_manager.packet_receiver, address)
        worker.signals.update.connect(self.set_participant_list)
        worker.signals.close_session.connect(self.session_closed_by_owner)
        worker.signals.test_timer.connect(self.set_test_timer)
        self.start_video_packet_processor()
        self.worker_threads.start(worker)

    def set_test_timer(self, params):
        self.session_page_widget.start_timers(params)
        self.test_started = True
        self.elapsed_test_time = params[0]
        self.test_duration = params[1]
        self.test_upload_time = params[2]
        try:
            worker = Worker(self.session_page_widget.session_time_keeper)
            worker.signals.update.connect(self.timer_update)
            self.worker_threads.start(worker)
        except Exception as err:
            print(err)

    def timer_update(self, params):
        self.session_page_widget.timer_update(params)
        self.elapsed_test_time += 1

    def session_closed_by_owner(self):
        self.session_page_widget.exit()
        disconnect_dialog = disconnected_dialog.DisconnectPopup("Session closed by host.", self)
        disconnect_dialog.show()

    def start_video_packet_processor(self):
        worker = Worker(feed_receiver.process_video_packets)
        worker.signals.send_data.connect(self.show_video_feed)
        self.worker_threads.start(worker)

    def closeEvent(self, event):
        self.session_page_widget.stop_streams()
        self.session_page_widget.stop_timer()
        main_client.close()

    def exit_session(self):
        self.session_page_widget.stop_streams()
        self.session_page_widget.stop_timer()
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
