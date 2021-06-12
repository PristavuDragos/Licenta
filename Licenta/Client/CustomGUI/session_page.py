import math
from Client import client_connection_manager, audio_stream, video_stream
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout

from Client import main_client
from Client.CustomGUI.create_session import CreateSessionPopup
from Client.CustomGUI.settings_menu import SettingsMenuPopup
from Client.CustomGUI.join_session import JoinSessionPopup
from Client.CustomGUI.register import RegisterPopup
from Client.CustomGUI.login import LoginPopup


class SessionPageWidget(QWidget):
    def __init__(self, settings, parent=None):
        super(SessionPageWidget, self).__init__(parent)
        self.par = parent
        self.settings = settings
        self.width = parent.width()
        self.height = parent.height()
        self.muted = True
        self.video_on = False
        self.counter = 0
        self.view_page = 1
        self.max_pages = 1
        self.participant_indexing = 15
        self.participants_list = []
        main_layout = QVBoxLayout(self)
        self.muted_icon = parent.muted_icon
        self.unmuted_icon = parent.unmuted_icon
        self.cam_on_icon = parent.cam_on_icon
        self.cam_off_icon = parent.cam_off_icon
        self.left_arrow_icon = parent.left_arrow_icon
        self.right_arrow_icon = parent.right_arrow_icon
        self.control_layout = QHBoxLayout()
        self.view_layout = QGridLayout()
        self.top_layout = QHBoxLayout()
        self.view_container = QWidget()
        self.view_container.setLayout(self.view_layout)
        self.view_container.setStyleSheet('background-color: #2A2E32;')
        self.view_container.setFixedHeight(self.height / 10 * 7)
        self.top_container = QWidget()
        self.top_container.setLayout(self.top_layout)
        self.top_container.setStyleSheet('background-color: #202238;')
        self.control_container = QWidget()
        self.control_container.setLayout(self.control_layout)
        self.control_container.setStyleSheet('background-color: #202238;')

        self.page_left = QPushButton()
        self.page_left.setIcon(self.left_arrow_icon)
        self.page_left.setFixedSize(50, 50)
        self.page_left.setIconSize(QSize(30, 30))
        self.page_left.setStyleSheet('border: none;')
        self.page_left.setDisabled(True)
        self.page_left.clicked.connect(self.previous_page)

        self.page_label = QLabel("Page: 1/1")

        self.page_right = QPushButton()
        self.page_right.setIcon(self.right_arrow_icon)
        self.page_right.setFixedSize(50, 50)
        self.page_right.setIconSize(QSize(30, 30))
        self.page_right.setStyleSheet('border: none;')
        self.page_right.setDisabled(True)
        self.page_right.clicked.connect(self.next_page)

        self.top_layout.addStretch()
        self.top_layout.addWidget(self.page_left)
        self.top_layout.addWidget(self.page_label)
        self.top_layout.addWidget(self.page_right)
        self.top_layout.addStretch()

        self.quit = QPushButton("Leave")
        self.quit.setFixedSize(100, 50)
        self.quit.clicked.connect(self.exit)
        self.quit.setStyleSheet("background-color: #0C2237")

        self.test_btn = QPushButton("Add")
        self.test_btn.setFixedSize(100, 50)
        self.test_btn.clicked.connect(self.test_for_view)

        self.mute = QPushButton()
        self.mute.clicked.connect(self.change_mute_state)
        self.mute.setIcon(self.muted_icon)
        self.mute.setFixedSize(50, 50)
        self.mute.setIconSize(QSize(50, 50))
        self.mute.setStyleSheet("background-color: #0C2237")

        self.video = QPushButton()
        self.video.clicked.connect(self.change_video_state)
        self.video.setIcon(self.cam_off_icon)
        self.video.setFixedSize(50, 50)
        self.video.setIconSize(QSize(50, 50))
        self.video.setStyleSheet("background-color: #0C2237")

        self.control_layout.addWidget(self.mute)
        self.control_layout.setAlignment(self.mute, Qt.AlignLeft)
        self.control_layout.addWidget(self.video)
        self.control_layout.setAlignment(self.video, Qt.AlignLeft)
        self.control_layout.addStretch()
        self.control_layout.addWidget(self.test_btn)
        self.control_layout.setAlignment(self.test_btn, Qt.AlignCenter)
        self.control_layout.addStretch()
        self.control_layout.addWidget(self.quit)
        self.control_layout.setAlignment(self.quit, Qt.AlignRight)
        self.control_layout.setAlignment(Qt.AlignCenter)
        self.view_layout.setAlignment(Qt.AlignCenter)
        self.top_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.top_container)
        main_layout.addWidget(self.view_container)
        main_layout.addWidget(self.control_container)

        self.video_labels = {}
        self.setLayout(main_layout)
        self.test_list = []

    def init_streams(self, settings, addresses):
        video_stream.init(settings, addresses[0])
        audio_stream.init(settings, addresses[1])
        if self.settings["video_start_on_enter"] == 1:
            self.change_video_state()
        if self.settings["audio_start_on_enter"] == 1:
            self.change_mute_state()

    def stop_streams(self):
        video_stream.stop_video_feed()
        audio_stream.stop_audio_feed()

    def exit(self):
        self.par.exit_session()
        self.par.switch_to_home_page()

    def set_participant_list(self, participants):
        self.participants_list = participants
        self.max_pages = math.ceil(len(self.participants_list) / 15)
        if self.max_pages <= self.view_page:
            self.view_page = self.max_pages
            self.participant_indexing = len(self.participants_list)
        elif self.max_pages == 1:
            self.view_page = 1
            self.participant_indexing = len(self.participants_list)
        if self.view_page > 1:
            self.page_left.setEnabled(True)
        if self.view_page < self.max_pages:
            self.page_right.setEnabled(True)
        client_connection_manager.require_feeds(self.participant_indexing)
        self.page_label.setText("Page: " + str(self.view_page) + "/" + str(self.max_pages))
        self.set_grid()

    def previous_page(self):
        if self.view_page > 1:
            self.view_page -= 1
        if self.view_page == 1:
            self.page_left.setEnabled(False)
        if self.view_page == 1 and self.max_pages == 1:
            self.participant_indexing = len(self.participants_list)
        else:
            self.participant_indexing = self.view_page * 15
        if self.view_page < self.max_pages:
            self.page_right.setEnabled(True)
        client_connection_manager.require_feeds(self.participant_indexing)
        self.page_label.setText("Page: " + str(self.view_page) + "/" + str(self.max_pages))
        self.set_grid()

    def next_page(self):
        if self.view_page < self.max_pages:
            self.view_page += 1
        if self.view_page == self.max_pages:
            self.participant_indexing = len(self.participants_list)
            self.page_right.setEnabled(False)
        else:
            self.participant_indexing = self.view_page * 15
        if self.view_page > 1:
            self.page_left.setEnabled(True)
        client_connection_manager.require_feeds(self.participant_indexing)
        self.page_label.setText("Page: " + str(self.view_page) + "/" + str(self.max_pages))
        self.set_grid()

    def test_for_view(self):
        self.counter += 1
        self.test_list.append([self.counter, str("User" + str(self.counter))])
        self.set_participant_list(self.test_list)

    def change_mute_state(self):
        if not self.muted:
            self.mute.setIcon(self.muted_icon)
            self.muted = not self.muted
            audio_stream.stop_audio_feed()
        else:
            self.mute.setIcon(self.unmuted_icon)
            self.muted = not self.muted
            audio_stream.start_audio_feed()

    def change_video_state(self):
        if self.counter > 0:
            self.counter -= 1
            del self.test_list[-1]
            self.set_participant_list(self.test_list)

        if not self.video_on:
            self.video.setIcon(self.cam_on_icon)
            self.video_on = not self.video_on
            video_stream.start_video_feed()
        else:
            self.video.setIcon(self.cam_off_icon)
            self.video_on = not self.video_on
            video_stream.stop_video_feed()

    def show_video_feed(self, frame_data):
        try:
            if frame_data[1] in self.video_labels.keys():
                label = self.video_labels.get(frame_data[1])
                label.setPixmap(frame_data[0])
        except BaseException as err:
            print(str(err))

    def reset_grid(self):
        while self.view_layout.count():
            item = self.view_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def set_grid(self):
        counter_ = 0
        self.reset_grid()
        width = 200
        height = 150
        columns = self.get_grid_shape()
        if self.participant_indexing < 15:
            it_list = self.participants_list
        else:
            it_list = self.participants_list[self.participant_indexing - 15:self.participant_indexing]
        for it in it_list:
            label = QLabel(self)
            label.resize(width, height)
            default_label = QPixmap(width,
                                    height)
            default_label.fill(QColor("black"))
            label.setPixmap(default_label)
            name_label = QLabel(it[1], label)
            if len(name_label.text()) > 25:
                name_label.setText(name_label.text()[:23] + "..")
            name_label.setStyleSheet("QLabel {background:transparent; color:white; font-size: 12px}")
            self.video_labels[it[0]] = label
            self.view_layout.addWidget(label, counter_ // columns, counter_ % columns)
            self.view_layout.setAlignment(label, Qt.AlignCenter)
            counter_ += 1

    def get_grid_shape(self):
        counter = len(self.participants_list)
        if counter <= 3:
            return 4
        elif counter == 4:
            return 2
        elif counter <= 6:
            return 3
        elif counter <= 8:
            return 4
        elif counter == 9:
            return 3
        elif counter <= 12:
            return 4
        else:
            return 5
