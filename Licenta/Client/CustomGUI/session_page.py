import math
import time

from Client import client_connection_manager, audio_stream, video_stream
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout, QFileDialog
from Client.CustomGUI.waiting_room_page import WaitingRoomPopup
from Client.CustomGUI import confirmation_dialog
from Client.CustomGUI.participant_list_page import ParticipantListPopup


class SessionPageWidget(QWidget):
    def __init__(self, settings, parent=None):
        super(SessionPageWidget, self).__init__(parent)
        self.session_code = ""
        self.owner = "-1"
        self.client_id = "-1"
        self.par = parent
        self.settings = settings
        self.width = parent.width()
        self.height = parent.height()
        self.muted = True
        self.video_on = False
        self.keep_timer_on = False
        self.test_timer = -1
        self.elapsed_test_time = 0
        self.test_duration = 0
        self.test_upload_time = 0
        self.counter = 0
        self.view_page = 1
        self.max_pages = 1
        self.participant_indexing = 15
        self.participants_list = []
        self.waiting_room_dialog_active = False
        self.waiting_room_dialog = WaitingRoomPopup(self)
        self.list_dialog_active = False
        self.list_dialog = ParticipantListPopup(self)
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

        self.session_code_label = QLabel("Session code:\n ASD")
        self.session_code_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.time_label = QLabel()
        self.time_label.hide()
        self.participant_list_button = QPushButton("Participants")
        self.participant_list_button.clicked.connect(self.show_participants)
        self.waiting_room_button = QPushButton("Waiting Room")
        self.waiting_room_button.clicked.connect(self.show_waiting_room)
        # self.participant_list_button.hide()
        self.download_solutions = QPushButton("Download Solutions")
        self.download_solutions.clicked.connect(self.download_solution_files)
        self.upload_subject = QPushButton("Upload test")
        self.upload_subject.clicked.connect(self.upload_subject_file)
        self.upload_solution = QPushButton("Upload solution")
        self.upload_solution.clicked.connect(self.upload_solution_file)
        self.download_subject = QPushButton("Download Test")
        self.download_subject.clicked.connect(self.download_subject_file)
        self.start_test_button = QPushButton("Start Test")
        self.start_test_button.clicked.connect(self.start_test)
        # self.start_button.hide()
        self.close_meeting_button = QPushButton("Close Session")
        self.close_meeting_button.clicked.connect(self.close_meeting)
        # self.close_meeting_button.hide()

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

        self.top_layout.addWidget(self.session_code_label)
        self.top_layout.addWidget(self.time_label)
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.page_left)
        self.top_layout.addWidget(self.page_label)
        self.top_layout.addWidget(self.page_right)
        self.top_layout.addStretch()
        self.top_layout.addWidget(self.waiting_room_button)
        self.top_layout.addWidget(self.participant_list_button)

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
        self.control_layout.addWidget(self.download_solutions)
        self.control_layout.addWidget(self.upload_subject)
        self.control_layout.addWidget(self.upload_solution)
        self.control_layout.addWidget(self.download_subject)
        self.control_layout.addWidget(self.start_test_button)
        self.control_layout.addStretch()
        self.control_layout.addWidget(self.close_meeting_button)
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

    def set_owner_buttons(self, show):
        if not show:
            self.session_code_label.hide()
            self.participant_list_button.hide()
            self.waiting_room_button.hide()
            self.close_meeting_button.hide()
            self.start_test_button.hide()
            self.upload_subject.hide()
            self.download_solutions.hide()
            self.upload_solution.show()
            self.download_subject.show()
        else:
            self.session_code_label.show()
            self.participant_list_button.show()
            self.waiting_room_button.show()
            self.close_meeting_button.show()
            self.start_test_button.show()
            self.upload_subject.show()
            self.download_solutions.show()
            self.upload_solution.hide()
            self.download_subject.hide()

    def set_session_data(self, owner, client_id, session_code):
        self.owner = owner
        self.client_id = client_id
        self.session_code = session_code
        if owner == client_id:
            self.session_code_label.setText(str("Session code:\n" + session_code))
            self.set_owner_buttons(True)
        else:
            self.set_owner_buttons(False)

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

    def timer_update(self, params):
        self.elapsed_test_time += 1
        if self.elapsed_test_time < self.test_duration:
            self.time_label.setText("Time left:" + str(self.test_duration - self.elapsed_test_time)
                                    + "mins\nTime for upload:" + str(self.test_upload_time) + "mins")
        elif self.elapsed_test_time >= self.test_duration and self.elapsed_test_time - self.test_duration < self.test_upload_time:
            self.time_label.setText("Time left: 0mins\nTime for upload:" +
                                    str(self.test_upload_time + self.test_duration - self.elapsed_test_time) + "mins")
        elif self.elapsed_test_time >= self.test_duration + self.test_upload_time:
            self.time_label.setText("Time is up!")
            self.upload_solution.setDisabled(True)

    def start_timers(self, params):
        self.keep_timer_on = True
        self.test_timer = time.perf_counter()
        self.elapsed_test_time = params[0]
        self.test_duration = params[1]
        self.test_upload_time = params[2]
        self.time_label.show()
        if self.elapsed_test_time < self.test_duration:
            self.time_label.setText("Time left:" + str(self.test_duration - self.elapsed_test_time)
                                    + "mins\nTime for upload:" + str(self.test_upload_time) + "mins")
        elif self.elapsed_test_time >= self.test_duration and self.elapsed_test_time - self.test_duration < self.test_upload_time:
            self.time_label.setText("Time left: 0mins\nTime for upload:" +
                                    str(self.test_upload_time + self.test_duration - self.elapsed_test_time) + "mins")
        elif self.elapsed_test_time >= self.test_duration + self.test_upload_time:
            self.time_label.setText("Time is up!")
            self.upload_solution.setDisabled(True)

    def session_time_keeper(self, *args, **signals):
        timer = time.perf_counter()
        while self.keep_timer_on:
            new_time = time.perf_counter()
            if time.perf_counter() - timer > 60:
                timer = new_time
                signals["update_callback"].emit([])

    def stop_timer(self):
        self.keep_timer_on = False

    def upload_subject_file(self):
        filename = QFileDialog.getOpenFileName(self, 'Open file',
                                               'c:\\', "Document (*.pdf)")
        client_connection_manager.upload_file([filename[0], self.session_code, 0])

    def upload_solution_file(self):
        self.settings = self.par.update_settings()
        filename = QFileDialog.getOpenFileName(self, 'Open file',
                                               'c:\\', "Document (*.pdf)")
        client_connection_manager.upload_file([filename[0], self.session_code, 1, self.settings["username"]])

    def download_subject_file(self):
        filename = QFileDialog.getSaveFileName(self, 'Save file',
                                               'c:\\', "Document (*.pdf)")
        client_connection_manager.download_subject([self.session_code, filename[0]])

    def download_solution_files(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        client_connection_manager.download_solutions([self.session_code, directory])

    def exit(self):
        self.set_owner_buttons(False)
        self.par.exit_session()
        self.par.switch_to_home_page()

    def set_waiting_room(self, waiting_list):
        self.waiting_room_dialog.waiting_list = waiting_list

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
        if self.list_dialog_active:
            self.list_dialog.set_labels(participants)

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

    def start_test(self):
        client_connection_manager.start_test()

    def close_meeting(self):
        confirm = confirmation_dialog.ConfirmationPopup("End Session", "Close this session?",
                                                        client_connection_manager.close_session, self)
        confirm.show()

    def show_participants(self):
        self.list_dialog_active = True
        self.list_dialog.show()
        self.list_dialog.set_labels(self.participants_list)

    def show_waiting_room(self):
        self.waiting_room_dialog_active = True
        self.waiting_room_dialog.set_labels()
        self.waiting_room_dialog.show()

    def close_waiting_room_dialog(self):
        self.waiting_room_dialog_active = False
        self.waiting_room_dialog.hide()

    def close_dialog(self):
        self.list_dialog_active = False
        self.list_dialog.hide()

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
