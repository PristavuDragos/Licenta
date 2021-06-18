from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout, QHBoxLayout

from Client import main_client
from Client.CustomGUI.create_session import CreateSessionPopup
from Client.CustomGUI.settings_menu import SettingsMenuPopup
from Client.CustomGUI.join_session import JoinSessionPopup
from Client.CustomGUI.register import RegisterPopup
from Client.CustomGUI.login import LoginPopup


class MainPageWidget(QWidget):
    def __init__(self, settings, signals, parent=None):
        super(MainPageWidget, self).__init__(parent)
        self.par = parent
        self.signals = signals
        button_grid = QGridLayout()
        layout = QVBoxLayout(self)
        width = parent.width()
        height = parent.height()
        button_size = QSize(width / 5, height / 10)

        self.test = QPushButton("Test", self)
        self.test.clicked.connect(parent.switch_to_session_screen)
        self.test.move(width / 10 * 9, height / 10 * 9 + 20)

        self.client_settings = settings
        self.login_button = QPushButton()
        self.login_button.setFixedSize(button_size)
        self.logout_button = QPushButton()
        self.logout_button.setFixedSize(button_size)
        self.register_button = QPushButton()
        self.register_button.setFixedSize(button_size)
        self.new_session_button = QPushButton("New Session")
        self.new_session_button.setFixedSize(button_size)
        self.new_session_button.clicked.connect(self.create_session)
        self.join_session_button = QPushButton("Join")
        self.join_session_button.setFixedSize(button_size)
        self.join_session_button.clicked.connect(self.join_session)
        self.login_button.setText("Login")
        self.login_button.clicked.connect(self.login_popup)
        self.logout_button.setText("Logout")
        self.logout_button.clicked.connect(self.logout)
        self.register_button.setText("Register")
        self.register_button.clicked.connect(self.register_popup)
        self.settings_button = QPushButton("Settings")
        self.settings_button.setFixedSize(button_size)
        self.settings_button.clicked.connect(self.settings)
        self.user_label = QLabel(self)
        self.user_label.setText("You are currently not logged in.")
        self.user_label.setAlignment(Qt.AlignCenter)
        if settings["logged_in"] == 0:
            self.login_update_ui(False)
        else:
            self.login_update_ui(True)
        grid_widget = QWidget(self)
        button_grid.addWidget(self.new_session_button, 0, 0, 1, 2)
        button_grid.addWidget(self.join_session_button, 0, 2, 1, 2)
        button_grid.addWidget(self.settings_button, 2, 1, 1, 2)
        button_grid.addWidget(self.login_button, 1, 0, 1, 2)
        button_grid.addWidget(self.register_button, 1, 2, 1, 2)
        button_grid.addWidget(self.logout_button, 1, 1, 1, 2)

        grid_widget.setLayout(button_grid)
        grid_widget.setMaximumSize(width / 1.5, height / 2)

        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.user_label, 0)
        layout.addWidget(grid_widget, 3)
        self.setLayout(layout)

    def login_update_ui(self, logged):
        if logged:
            self.login_button.hide()
            self.register_button.hide()
            self.logout_button.show()
            self.user_label.setText("Welcome back,\n" + self.client_settings["username"])
        else:
            self.login_button.show()
            self.register_button.show()
            self.logout_button.hide()
            self.user_label.setText("You are currently not logged in.")

    def login_popup(self):
        login = LoginPopup(self)
        login.show()

    def register_popup(self):
        register = RegisterPopup(self)
        register.show()

    def create_session(self):
        self.client_settings = self.par.update_settings()
        if self.client_settings["logged_in"] == 1:
            create_session = CreateSessionPopup(self.signals, self)
            create_session.show()
        else:
            self.user_label.setText(
                "You are currently not logged in.\nYou need to be logged in to create/join a session")

    def join_session(self):
        self.client_settings = self.par.update_settings()
        if self.client_settings["logged_in"] == 1:
            join_session = JoinSessionPopup(self.signals, self)
            join_session.show()
        else:
            self.user_label.setText(
                "You are currently not logged in.\nYou need to be logged in to create/join a session")

    def settings(self):
        settings_menu = SettingsMenuPopup(self)
        settings_menu.show()

    def logout(self):
        main_client.logout()
        self.login_update_ui(False)
