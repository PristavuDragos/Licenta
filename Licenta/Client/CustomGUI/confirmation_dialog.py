from PyQt5.QtWidgets import QDialog, QGroupBox, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout, \
    QScrollArea, QWidget
from PyQt5.QtCore import Qt

from Client import client_connection_manager


class ConfirmationPopup(QDialog):
    def __init__(self, title, text, function, parent=None):
        super(ConfirmationPopup, self).__init__(parent)
        self.par = parent
        self.function = function
        self.setWindowTitle(title)
        self.setGeometry(400, 150, 200, 150)
        self.setFixedSize(200, 150)
        self.main_layout = QVBoxLayout()
        self.text_label = QLabel(text)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.accept_dialog)
        self.main_layout.addWidget(self.text_label)
        self.main_layout.addWidget(self.button_box)
        self.setLayout(self.main_layout)

    def accept_dialog(self):
        self.accept()
        self.function(self.par.session_code, self.par.client_id)

