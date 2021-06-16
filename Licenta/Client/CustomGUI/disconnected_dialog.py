from PyQt5.QtWidgets import QDialog, QGroupBox, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout, \
    QScrollArea, QWidget
from PyQt5.QtCore import Qt

from Client import client_connection_manager


class DisconnectPopup(QDialog):
    def __init__(self, message, parent=None):
        super(DisconnectPopup, self).__init__(parent)
        self.par = parent
        self.setWindowTitle("Disconnected from session.")
        self.setGeometry(400, 150, 200, 150)
        self.setFixedSize(200, 150)
        self.main_layout = QVBoxLayout()
        self.text_label = QLabel(message)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.button_box.rejected.connect(self.reject)
        self.main_layout.addWidget(self.text_label)
        self.main_layout.addWidget(self.button_box)
        self.setLayout(self.main_layout)
        self.setWindowModality(Qt.ApplicationModal)