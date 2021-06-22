from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, \
    QScrollArea, QWidget, QCheckBox
from PyQt5.QtCore import Qt

from Client import client_connection_manager


class WaitingRoomPopup(QDialog):
    def __init__(self, parent=None):
        super(WaitingRoomPopup, self).__init__(parent)
        self.par = parent
        self.setWindowTitle("Participant List")
        self.setGeometry(400, 150, 250, 400)
        self.setFixedWidth(250)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.rejected.connect(parent.close_waiting_room_dialog)
        self.button_box.accepted.connect(self.send_list)
        self.scroll = QScrollArea(self)
        self.container = QWidget()
        self.label_layout = QVBoxLayout()
        self.main_layout = QVBoxLayout()
        self.container.setLayout(self.label_layout)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.container)
        self.waiting_list = []
        self.widget_list = {}
        self.main_layout.addWidget(self.scroll)
        self.main_layout.addWidget(self.button_box)
        self.setLayout(self.main_layout)

    def reset_layout(self):
        while self.label_layout.count():
            item = self.label_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        self.widget_list = {}

    def set_labels(self):
        self.reset_layout()
        counter = 0
        for it in self.waiting_list:
            counter += 1
            checkbox = QCheckBox(self)
            checkbox.setText(str(str(counter) + ". " + it[1]))
            checkbox.setChecked(True)
            self.label_layout.addWidget(checkbox)
            self.label_layout.setAlignment(checkbox, Qt.AlignLeft)
            self.widget_list[it[0]] = checkbox
        self.label_layout.addStretch()

    def send_list(self):
        approval_list = []
        for client_id, widget in self.widget_list.items():
            value = '0'
            if widget.isChecked():
                value = '1'
            approval_list.append([client_id, value])
        client_connection_manager.send_approval_list(approval_list)
        self.hide()

    def closeEvent(self, event):
        self.par.close_dialog()
