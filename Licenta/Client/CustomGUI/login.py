from PyQt5.QtWidgets import QDialog, QGroupBox, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout
from PyQt5.QtCore import Qt

from Client import client_connection_manager


class LoginPopup(QDialog):
    def __init__(self, parent=None):
        super(LoginPopup, self).__init__(parent)
        self.par = parent
        self.setWindowTitle("Login")
        self.setGeometry(400, 150, 300, 350)
        self.setFixedSize(300, 350)

        self.formGroupBox = QGroupBox("Login")
        layout = QFormLayout()
        email_label = QLabel("Email:")
        email_label.setAlignment(Qt.AlignCenter)
        password_label = QLabel("Password:")
        password_label.setAlignment(Qt.AlignCenter)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("email")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("password")
        self.password_edit.setEchoMode(QLineEdit.Password)

        layout.addRow(email_label)
        layout.addRow(self.email_edit)
        layout.addRow(password_label)
        layout.addRow(self.password_edit)
        layout.setSpacing(20)
        self.formGroupBox.setLayout(layout)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.verify_input)
        self.warning_label = QLabel("")
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setStyleSheet('QLabel { color: #f6989d }')
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.formGroupBox)
        main_layout.addWidget(self.warning_label)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)
        self.setWindowModality(Qt.ApplicationModal)

    def verify_input(self):
        email = self.email_edit.text()
        if len(email) == 0:
            self.warning_label.setText("Insert your email!")
            return None
        else:
            self.warning_label.setText("")
        password = self.password_edit.text()
        if len(password) == 0:
            self.warning_label.setText("Insert your password!")
            return None
        else:
            self.warning_label.setText("")
        result = client_connection_manager.login_request([email, password])
        self.warning_label.setText(result)
        if result == "Logged in successfully!":
            self.parent().login_update_ui(True)
            self.button_box.button(QDialogButtonBox.Ok).hide()
