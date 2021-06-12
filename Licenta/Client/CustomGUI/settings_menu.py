from PyQt5.QtWidgets import QDialog, QGroupBox, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout, \
    QGridLayout, QCheckBox, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt


class SettingsMenuPopup(QDialog):
    def __init__(self, parent=None):
        super(SettingsMenuPopup, self).__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(400, 150, 400, 600)
        self.setFixedSize(400, 600)
        print("da")
        self.general_settings_group = QGroupBox("General Settings")
        layout = QVBoxLayout()
        self.b1 = QCheckBox("setare1")
        self.b1.setChecked(True)
        # self.b1.stateChanged.connect(lambda: self.btnstate(self.b1))
        self.b2 = QCheckBox("setare2")
        self.b2.setChecked(True)
        self.b3 = QCheckBox("setare3")
        self.b3.setChecked(True)
        self.b4 = QCheckBox("setare4")
        self.b4.setChecked(True)
        self.b5 = QCheckBox("setare5")
        self.b5.setChecked(True)
        layout.addWidget(self.b1)
        layout.addWidget(self.b2)
        layout.addWidget(self.b3)
        layout.addWidget(self.b4)
        layout.addWidget(self.b5)

        self.test_video_button = QPushButton("Test Video")
        self.test_audio_button = QPushButton("Test Audio")
        test_button_layout = QHBoxLayout()
        test_button_layout.addWidget(self.test_audio_button)
        test_button_layout.addWidget(self.test_video_button)

        self.general_settings_group.setLayout(layout)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.update_settings)
        buttonBox.rejected.connect(self.reject)
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(20,20,20,20)
        mainLayout.setSpacing(25)
        mainLayout.addWidget(self.general_settings_group)
        mainLayout.addLayout(test_button_layout)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowModality(Qt.ApplicationModal)

    def update_settings(self):
        pass

