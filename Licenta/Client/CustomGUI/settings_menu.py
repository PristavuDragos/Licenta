import json

from PyQt5.QtWidgets import QDialog, QGroupBox, QDialogButtonBox, QVBoxLayout, QCheckBox
from PyQt5.QtCore import Qt
from Client import main_client


class SettingsMenuPopup(QDialog):
    def __init__(self, settings, parent=None):
        super(SettingsMenuPopup, self).__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(400, 150, 300, 300)
        self.setFixedSize(300, 300)
        self.general_settings_group = QGroupBox()
        layout = QVBoxLayout()
        self.client_settings = settings
        self.video_setting = QCheckBox("Start video when entering session")
        if self.client_settings["video_start_on_enter"] == 1:
            self.video_setting.setChecked(True)
        else:
            self.video_setting.setChecked(False)
        self.video_setting.clicked.connect(self.change_video_setting)
        self.audio_setting = QCheckBox("Start audio when entering session")
        if self.client_settings["audio_start_on_enter"] == 1:
            self.audio_setting.setChecked(True)
        else:
            self.audio_setting.setChecked(False)
        self.audio_setting.clicked.connect(self.change_audio_setting)
        layout.addWidget(self.video_setting)
        layout.addWidget(self.audio_setting)
        self.general_settings_group.setLayout(layout)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.update_client_settings)
        button_box.rejected.connect(self.reject)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)
        main_layout.addWidget(self.general_settings_group)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowModality(Qt.ApplicationModal)

    def change_audio_setting(self):
        self.client_settings["audio_start_on_enter"] = 1 if self.audio_setting.isChecked() else 0

    def change_video_setting(self):
        self.client_settings["video_start_on_enter"] = 1 if self.video_setting.isChecked() else 0

    def update_client_settings(self):
        main_client.update_client_settings(self.client_settings)
        self.accept()

