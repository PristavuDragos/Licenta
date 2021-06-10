import time

from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QGroupBox, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout
from PyQt5.QtCore import Qt, QRegExp
from Client import client_connection_manager


class RegisterPopup(QDialog):
    def __init__(self, parent=None):
        super(RegisterPopup, self).__init__(parent)
        self.setWindowTitle("Register")
        self.setGeometry(400, 150, 300, 500)
        self.setFixedSize(300, 500)

        self.formGroupBox = QGroupBox("Register")
        layout = QFormLayout()
        email_label = QLabel("Email:")
        email_label.setAlignment(Qt.AlignCenter)
        username_label = QLabel("Full name:")
        username_label.setAlignment(Qt.AlignCenter)
        password_label = QLabel("Password:")
        password_label.setAlignment(Qt.AlignCenter)
        password_confirmation_label = QLabel("Confirm password:")
        password_confirmation_label.setAlignment(Qt.AlignCenter)
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("email")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("full name")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("password")
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.email_validator = QRegExpValidator(QRegExp('^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'))
        self.email_edit.setValidator(self.email_validator)
        self.username_validator = QRegExpValidator(QRegExp('^[a-zA-Z -]+$'))
        self.username_edit.setValidator(self.username_validator)

        self.password_validator = QRegExpValidator(QRegExp('^[a-zA-Z0-9!@#$%^&*<>/.,?+=-_]{8,20}$'))
        self.password_edit.setValidator(self.password_validator)
        self.password_edit.textChanged.connect(self.password_state)

        self.password_confirmation_edit = QLineEdit()
        self.password_confirmation_edit.setPlaceholderText("confirm password")
        self.password_confirmation_edit.setEchoMode(QLineEdit.Password)
        self.password_confirmation_edit.textChanged.connect(self.compare_passwords)
        layout.addRow(email_label)
        layout.addRow(self.email_edit)
        layout.addRow(username_label)
        layout.addRow(self.username_edit)
        layout.addRow(password_label)
        layout.addRow(self.password_edit)
        layout.addRow(password_confirmation_label)
        layout.addRow(self.password_confirmation_edit)

        self.warning_label = QLabel("")
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setStyleSheet('QLabel { color: #f6989d }')
        layout.addRow(self.warning_label)

        layout.setSpacing(20)
        self.formGroupBox.setLayout(layout)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.verify_input)
        self.buttonBox.rejected.connect(self.reject)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowModality(Qt.ApplicationModal)

    '''
    https://snorfalorpagus.net/blog/2014/08/09/validating-user-input-in-pyqt4-using-qvalidator/
    '''

    def password_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        text = sender.text()
        state = validator.validate(text, 0)[0]
        flag_count = 0
        uppercase_flag = 0
        number_flag = 0
        special_char_flag = 0
        for it in range(len(text)):
            if number_flag == 0 and text[it] in "0123456789":
                number_flag = 1
                continue
            if special_char_flag == 0 and text[it] in "!@#$%^&*<>/.,?+=-_":
                special_char_flag = 1
                continue
            if uppercase_flag == 0 and text[it] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                uppercase_flag = 1
                continue
        flag_count = uppercase_flag + special_char_flag + number_flag
        if state == 2 and flag_count == 3:
            color = '#c4df9b'  # green
        elif state == 2 and flag_count <= 2:
            color = '#fff79a'
        else:
            color = '#f6989d'  # red
        sender.setStyleSheet('QLineEdit { color: %s }' % color)

    def compare_passwords(self, *args, **kwargs):
        match = False
        if self.password_edit.text() == self.password_confirmation_edit.text():
            match = True
        if match:
            color = '#c4df9b'  # green
        else:
            color = '#f6989d'  # red
        self.sender().setStyleSheet('QLineEdit { color: %s }' % color)

    def verify_input(self):
        email_state = self.email_validator.validate(self.email_edit.text(), 0)[0]
        if email_state == 1:
            self.warning_label.setText("Invalid email!")
            return None
        else:
            self.warning_label.setText("")
        password_state = self.password_validator.validate(self.password_edit.text(), 0)[0]
        if len(self.username_edit.text()) < 6:
            self.warning_label.setText("Full name required!")
            return None
        else:
            self.warning_label.setText("")
        if password_state == 1:
            self.warning_label.setText("Password needs to be 8 characters long!")
            return None
        else:
            self.warning_label.setText("")
        password_confirmation_state = self.password_validator.validate(self.password_confirmation_edit.text(), 0)[0]
        if password_confirmation_state == 1:
            self.warning_label.setText("Passwords don't match!")
            return None
        else:
            self.warning_label.setText("")
        result = client_connection_manager.register_request(
            [self.email_edit.text(), self.username_edit.text(), self.password_edit.text()])
        self.warning_label.setText(result)
        if result == "Account created!":
            self.buttonBox.button(QDialogButtonBox.Ok).hide()
