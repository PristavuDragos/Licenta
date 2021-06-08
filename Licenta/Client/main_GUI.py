import json
import sys
import client_connection_manager
import main_client
from PyQt5 import QtGui
from PyQt5.QtCore import QThreadPool, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QStackedWidget
from qt_material import apply_stylesheet
import feed_receiver
from worker_thread import Worker
from login import LoginPopup
import main_page

settings = None
main_window = None
qt_main_loop = None
participants = None


def init_settings():
    global settings
    with open("../Settings/ui_settings.json", "r") as settings_file:
        settings = json.load(settings_file)


class MainGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker_threads = QThreadPool()
        self.window_title = settings["window_title"]
        self.window_width = settings["window_width"]
        self.window_height = settings["window_height"]
        self.setWindowTitle(self.window_title)
        self.setMinimumHeight(settings["min_window_height"])
        self.resize(self.window_width, self.window_height)
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        main_page_widget = main_page.MainPageWidget(self)
        self.central_widget.addWidget(main_page_widget)
        self.central_widget.setCurrentWidget(main_page_widget)
        # self.update_grid = QPushButton("Baga", self)
        # self.video_labels = {}
        # self.label_grid = QGridLayout(self)
        self.init_ui()

    def show_video_feed(self, frame_data):
        try:
            if frame_data[1] in self.video_labels.keys():
                label = self.video_labels.get(frame_data[1])
                label.setPixmap(frame_data[0])
        except BaseException as err:
            print(str(err))

    def set_participant_list(self, participant_list):
        global participants
        participants = participant_list
        self.update_grid.clicked.emit()

    def set_grid(self):
        counter = 0
        self.reset_grid()
        for it in participants:
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

    def start_packet_receiver(self):
        worker = Worker(client_connection_manager.packet_receiver)
        worker.signals.update.connect(self.set_participant_list)
        worker.signals.connected.connect(self.start_video_packet_processor)
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
        main_client.init_settings()
        main_client.set_window(self)
        # self.test_button.setText("Join as test")
        # self.test_button.move(800, 600)
        # self.test_button.clicked.connect(self.test_button_action)
        # self.test_button.show()
        # self.user_button.setText("Join as user")
        # self.user_button.move(800, 650)
        # self.user_button.clicked.connect(self.user_button_action)
        # self.user_button.show()
        # self.update_grid.clicked.connect(self.set_grid)
        # self.update_grid.hide()
        # self.setLayout(self.label_grid)
        self.show()


def start_ui():
    global main_window
    global qt_main_loop
    qt_main_loop = QApplication([])
    apply_stylesheet(qt_main_loop, theme='dark_blue.xml')
    main_window = MainGUI()
    sys.exit(qt_main_loop.exec_())
