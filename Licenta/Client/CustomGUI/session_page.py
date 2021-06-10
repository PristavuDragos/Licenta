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
    def __init__(self, parent=None):
        super(SessionPageWidget, self).__init__(parent)
        self.par = parent
        self.width = parent.width()
        self.height = parent.height()
        button_size = QSize(self.width / 5, self.height / 10)
        self.muted = False
        self.video_on = True
        self.counter = 0

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

        self.page_label = QLabel("sample text")

        self.page_right = QPushButton()
        self.page_right.setIcon(self.right_arrow_icon)
        self.page_right.setFixedSize(50, 50)
        self.page_right.setIconSize(QSize(30, 30))
        self.page_right.setStyleSheet('border: none;')
        self.page_right.setDisabled(True)

        self.top_layout.addStretch()
        self.top_layout.addWidget(self.page_left)
        self.top_layout.addWidget(self.page_label)
        self.top_layout.addWidget(self.page_right)
        self.top_layout.addStretch()

        self.quit = QPushButton("back")
        self.quit.setFixedSize(100, 50)
        self.quit.clicked.connect(parent.switch_to_home_page)
        self.quit.setStyleSheet("background-color: #0C2237")

        self.test_btn = QPushButton("Add")
        self.test_btn.setFixedSize(100, 50)
        self.test_btn.clicked.connect(self.test_for_view)

        self.mute = QPushButton()
        self.mute.clicked.connect(self.change_mute_img)
        self.mute.setIcon(self.unmuted_icon)
        self.mute.setFixedSize(50, 50)
        self.mute.setIconSize(QSize(50, 50))
        self.mute.setStyleSheet("background-color: #0C2237")

        self.video = QPushButton()
        self.video.clicked.connect(self.change_video_img)
        self.video.setIcon(self.cam_on_icon)
        self.video.setFixedSize(50, 50)
        self.video.setIconSize(QSize(50, 50))
        self.video.setStyleSheet("background-color: #0C2237")

        #self.quit.move(width / 10 * 9, height / 10 * 9 + 20)
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

    def test_for_view(self):
        if self.counter < 15:
            self.counter += 1
        self.set_grid()

    def change_mute_img(self):
        if not self.muted:
            self.mute.setIcon(self.muted_icon)
            self.muted = not self.muted
        else:
            self.mute.setIcon(self.unmuted_icon)
            self.muted = not self.muted

    def change_video_img(self):
        self.counter = 0
        if not self.video_on:
            self.video.setIcon(self.cam_on_icon)
            self.video_on = not self.video_on
        else:
            self.video.setIcon(self.cam_off_icon)
            self.video_on = not self.video_on

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
        for it in self.par.participants:
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
        counter = self.counter
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
