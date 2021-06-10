from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QGroupBox, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout
from PyQt5.QtCore import Qt, QRegExp

from Client import client_connection_manager


class JoinSessionPopup(QDialog):
    def __init__(self, parent=None):
        super(JoinSessionPopup, self).__init__(parent)
        self.setWindowTitle("Join Session")
        self.setGeometry(400, 150, 400, 300)
        self.setFixedSize(400, 300)
        self.formGroupBox = QGroupBox("Join")
        self.par = parent
        layout = QFormLayout()
        session_code_label = QLabel("Session code :")
        session_code_label.setAlignment(Qt.AlignCenter)
        password_label = QLabel("Password :")
        password_label.setAlignment(Qt.AlignCenter)
        self.session_code_edit = QLineEdit()
        self.session_code_edit.setPlaceholderText("session name")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("password")
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.password_validator = QRegExpValidator(QRegExp('^[a-zA-Z0-9!@#$%^&*<>/.,?+=-_]{4,15}$'))
        self.password_edit.setValidator(self.password_validator)
        layout.addRow(session_code_label)
        layout.addRow(self.session_code_edit)
        layout.addRow(password_label)
        layout.addRow(self.password_edit)
        layout.setSpacing(20)
        self.formGroupBox.setLayout(layout)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.verify_input)
        buttonBox.rejected.connect(self.reject)
        self.warning_label = QLabel("")
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setStyleSheet('QLabel { color: #f6989d }')
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.warning_label)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowModality(Qt.ApplicationModal)

    def verify_input(self):
        session_code = self.session_code_edit.text()
        if len(session_code) != 8:
            self.warning_label.setText("The code has to be 8 characters!")
            return None
        else:
            self.warning_label.setText("")
        password = self.password_edit.text()
        result = client_connection_manager.connect_to_session([session_code, password])
        self.warning_label.setText(result)
        if result == "Connected.":
            self.buttonBox.button(QDialogButtonBox.Ok).hide()
            self.par.start_packet_receiver()
