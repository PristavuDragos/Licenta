from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QGroupBox, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout, \
    QGridLayout, QWidget
from PyQt5.QtCore import Qt, QRegExp

from Client import client_connection_manager


class CreateSessionPopup(QDialog):
    def __init__(self, parent=None):
        super(CreateSessionPopup, self).__init__(parent)
        self.setWindowTitle("Create New Session")
        self.setGeometry(400, 150, 400, 500)
        self.setFixedSize(400, 500)
        self.formGroupBox = QGroupBox("New session")
        layout = QVBoxLayout()
        grid = QGridLayout()
        session_name_label = QLabel("Session name :")
        session_name_label.setAlignment(Qt.AlignCenter)
        password_label = QLabel("Password (optional) :")
        password_label.setAlignment(Qt.AlignCenter)
        duration_label = QLabel("Test duration(in minutes)")
        duration_label.setAlignment(Qt.AlignCenter)
        upload_time_label = QLabel("Time to upload(in minutes)")
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
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.verify_input)
        buttonBox.rejected.connect(self.reject)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowModality(Qt.ApplicationModal)

    def verify_input(self):
        session_name = self.session_name_edit.text()
        if len(session_name) < 3:
            self.warning_label.setText("Give this session a proper name!")
            return None
        else:
            self.warning_label.setText("")
        password = self.password_edit.text()
        duration = self.duration_edit.text()
        upload_time = self.upload_time_edit.text()
        result = client_connection_manager.initiate_session([session_name, password, duration, upload_time])
        self.warning_label.setText(result)
        if result == "Logged in successfully!":
            self.parent().login_update_ui(True)
            self.buttonBox.button(QDialogButtonBox.Ok).hide()
