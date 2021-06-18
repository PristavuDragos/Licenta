from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QDialog, QGroupBox, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout
from PyQt5.QtCore import Qt, QRegExp, QThread
from Client import worker_thread
from Client import client_connection_manager


class JoinSessionPopup(QDialog):
    def __init__(self, signals, parent=None):
        super(JoinSessionPopup, self).__init__(parent)
        self.signals = signals
        self.setWindowTitle("Join Session")
        self.setGeometry(400, 150, 400, 350)
        self.setFixedSize(400, 350)
        self.formGroupBox = QGroupBox("Join")
        self.par = parent
        self.code = ""
        self.password = ""
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
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.verify_input)
        button_box.rejected.connect(self.exit)
        self.warning_label = QLabel("")
        self.warning_label.setAlignment(Qt.AlignCenter)
        self.warning_label.setStyleSheet('QLabel { color: #f6989d }')
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.formGroupBox)
        main_layout.addWidget(self.warning_label)
        main_layout.addWidget(button_box)
        self.setLayout(main_layout)

        self.setWindowModality(Qt.ApplicationModal)

    def verify_input(self):
        session_code = self.session_code_edit.text()
        self.code = session_code
        if len(session_code) != 8:
            self.warning_label.setText("The code has to be 8 characters!")
            return None
        else:
            self.warning_label.setText("")
        self.password = self.password_edit.text()
        result = client_connection_manager.connect_to_waiting_room([session_code, self.password])
        self.warning_label.setText(result[0])
        if result[0] == "Connected.":
            self.warning_label.setText("Awaiting host permission.\nDon't close this window.")
            worker = worker_thread.Worker(client_connection_manager.awaiting_permission)
            worker.signals.update.connect(self.finalize)
            self.par.par.worker_threads.start(worker)

    def finalize(self, result):
        if result == -1:
            self.warning_label.setText("Connection timed out.")
        elif result == 0:
            self.warning_label.setText("Access to session denied")
        elif result == 1:
            result = client_connection_manager.connect_to_session([self.code, self.password])
            self.warning_label.setText(result[0])
            if result[0] == "Connected.":
                self.warning_label.setText("Joining")
                self.accept()
                self.signals.start_packet_receiver.emit(result[1])
                self.signals.switch_page.emit([[result[2], result[3]], result[4], self.code])

    def exit(self):
        client_connection_manager.stop_waiting()
        self.reject()

    def closeEvent(self, event):
        client_connection_manager.stop_waiting()
        self.reject()
