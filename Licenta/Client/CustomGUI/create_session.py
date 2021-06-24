from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QGroupBox, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout, \
    QGridLayout
from PyQt5.QtCore import Qt, QRegExp

from Client import client_connection_manager


class CreateSessionPopup(QDialog):
    def __init__(self, signals, parent=None):
        super(CreateSessionPopup, self).__init__(parent)
        self.signals = signals
        self.setWindowTitle("Create New Session")
        self.setGeometry(400, 150, 400, 500)
        self.setFixedSize(400, 500)
        self.formGroupBox = QGroupBox("New session")
        layout = QVBoxLayout()
        grid = QGridLayout()
        session_name_label = QLabel("Session name :")
        session_name_label.setAlignment(Qt.AlignCenter)
        password_label = QLabel("Password :")
        password_label.setAlignment(Qt.AlignCenter)
        duration_label = QLabel("Test duration\n(in minutes)")
        duration_label.setAlignment(Qt.AlignCenter)
        upload_time_label = QLabel("Time to upload\n(in minutes)")
        upload_time_label.setAlignment(Qt.AlignCenter)
        self.session_name_edit = QLineEdit()
        self.session_name_edit.setPlaceholderText("session name")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.duration_edit = QLineEdit()
        self.duration_edit.setPlaceholderText("00")
        self.duration_edit.setAlignment(Qt.AlignRight)
        self.upload_time_edit = QLineEdit()
        self.upload_time_edit.setPlaceholderText("0")
        self.upload_time_edit.setAlignment(Qt.AlignRight)
        self.time_validator = QRegExpValidator(QRegExp('^[0-9]{0,3}'))
        self.duration_edit.setValidator(self.time_validator)
        self.upload_time_edit.setValidator(self.time_validator)
        self.password_validator = QRegExpValidator(QRegExp('^[a-zA-Z0-9!@#$%^&*<>/.,?+=-_]{0,15}$'))
        self.password_edit.setValidator(self.password_validator)
        self.warning_label = QLabel("")
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setStyleSheet('QLabel { color: #f6989d }')
        grid.addWidget(duration_label, 0, 0)
        grid.addWidget(upload_time_label, 0, 1)
        grid.addWidget(self.duration_edit, 1, 0)
        grid.addWidget(self.upload_time_edit, 1, 1)
        layout.addWidget(session_name_label)
        layout.addWidget(self.session_name_edit)
        layout.addWidget(password_label)
        layout.addWidget(self.password_edit)
        layout.addLayout(grid)
        layout.addWidget(self.warning_label)
        self.formGroupBox.setLayout(layout)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.verify_input)
        button_box.rejected.connect(self.reject)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.formGroupBox)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowModality(Qt.ApplicationModal)

    def verify_input(self):
        session_name = self.session_name_edit.text()
        password = self.password_edit.text()
        duration = self.duration_edit.text()
        upload_time = self.upload_time_edit.text()
        result = client_connection_manager.initiate_session([session_name, password, duration, upload_time])
        self.warning_label.setText(result[0])
        if result[0] == "Session created.":
            conn_result = client_connection_manager.connect_to_session([result[1], password])
            if conn_result[0] == "Connected.":
                self.accept()
                self.signals.start_packet_receiver.emit(conn_result[1])
                self.signals.switch_page.emit([[conn_result[2], conn_result[3]], conn_result[4], result[1]])
