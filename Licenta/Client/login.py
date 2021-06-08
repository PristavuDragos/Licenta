from PyQt5.QtWidgets import QDialog, QGroupBox, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout
from PyQt5.QtCore import Qt


class LoginPopup(QDialog):
    def __init__(self, parent=None):
        super(LoginPopup, self).__init__(parent)
        self.setWindowTitle("Login")
        self.setGeometry(400, 150, 300, 300)
        self.setFixedSize(300, 300)

        self.formGroupBox = QGroupBox("Login")
        layout = QFormLayout()
        email_label = QLabel("Email:")
        email_label.setAlignment(Qt.AlignCenter)
        password_label = QLabel("Password:")
        password_label.setAlignment(Qt.AlignCenter)
        email_edit = QLineEdit()
        email_edit.setPlaceholderText("email")
        password_edit = QLineEdit()
        password_edit.setPlaceholderText("password")
        password_edit.setEchoMode(QLineEdit.Password)

        layout.addRow(email_label)
        layout.addRow(email_edit)
        layout.addRow(password_label)
        layout.addRow(password_edit)
        layout.setSpacing(20)
        self.formGroupBox.setLayout(layout)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.rejected.connect(self.reject)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowModality(Qt.ApplicationModal)
