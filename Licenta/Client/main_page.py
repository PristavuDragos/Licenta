from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QGridLayout, QVBoxLayout
from create_session import CreateSessionPopup
from settings_menu import SettingsMenuPopup
from join_session import JoinSessionPopup
from register import RegisterPopup
from login import LoginPopup


class MainPageWidget(QWidget):
    def __init__(self, parent=None):
        super(MainPageWidget, self).__init__(parent)
        button_grid = QGridLayout()
        layout = QVBoxLayout(self)
        width = parent.width()
        height = parent.height()
        button_size = QSize(width / 5, height / 10)

        self.login_button = QPushButton("Login")
        self.login_button.setFixedSize(button_size)
        self.login_button.clicked.connect(self.login_popup)
        self.register_button = QPushButton("Register")
        self.register_button.setFixedSize(button_size)
        self.register_button.clicked.connect(self.register_popup)
        self.new_session_button = QPushButton("New Session")
        self.new_session_button.setFixedSize(button_size)
        self.new_session_button.clicked.connect(self.create_session)
        self.join_session_button = QPushButton("Join")
        self.join_session_button.setFixedSize(button_size)
        self.join_session_button.clicked.connect(self.join_session)
        self.settings_button = QPushButton("Settings")
        self.settings_button.setFixedSize(button_size)
        self.settings_button.clicked.connect(self.settings)

        self.user_label = QLabel(self)
        self.user_label.setText("You are currently not logged in")
        self.user_label.setAlignment(Qt.AlignCenter)

        grid_widget = QWidget(self)
        button_grid.addWidget(self.new_session_button, 0, 0, 1, 2)
        button_grid.addWidget(self.join_session_button, 0, 2, 1, 2)
        button_grid.addWidget(self.login_button, 1, 0, 1, 2)
        button_grid.addWidget(self.register_button, 1, 2, 1, 2)
        button_grid.addWidget(self.settings_button, 2, 1, 1, 2)
        grid_widget.setLayout(button_grid)
        grid_widget.setMaximumSize(width / 1.5, height / 2)

        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.user_label, 0)
        layout.addWidget(grid_widget, 3)
        self.setLayout(layout)

    def login_popup(self):
        login = LoginPopup(self)
        login.show()

    def register_popup(self):
        register = RegisterPopup(self)
        register.show()

    def create_session(self):
        create_session = CreateSessionPopup(self)
        create_session.show()

    def join_session(self):
        join_session = JoinSessionPopup(self)
        join_session.show()

    def settings(self):
        settings_menu = SettingsMenuPopup(self)
        settings_menu.show()
