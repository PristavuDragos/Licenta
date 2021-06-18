from PyQt5.QtWidgets import QDialog, QGroupBox, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QVBoxLayout, \
    QScrollArea, QWidget
from PyQt5.QtCore import Qt

from Client import client_connection_manager


class ParticipantListPopup(QDialog):
    def __init__(self, parent=None):
        super(ParticipantListPopup, self).__init__(parent)
        self.par = parent
        self.setWindowTitle("Participant List")
        self.setGeometry(400, 150, 250, 400)
        self.setFixedSize(250, 400)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        self.button_box.rejected.connect(parent.close_dialog)
        self.scroll = QScrollArea(self)
        self.container = QWidget()
        self.label_layout = QVBoxLayout()
        self.main_layout = QVBoxLayout()
        self.container.setLayout(self.label_layout)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.container)
        self.participant_list = parent.participants_list
        self.main_layout.addWidget(self.scroll)
        self.main_layout.addWidget(self.button_box)
        self.setLayout(self.main_layout)

    def reset_layout(self):
        while self.label_layout.count():
            item = self.label_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def set_labels(self, participant_list):
        self.participant_list = participant_list
        self.reset_layout()
        counter = 0
        for it in self.participant_list:
            counter += 1
            label = QLabel(self)
            label.setText(str(str(counter) + ". " + it[1]))
            self.label_layout.addWidget(label)
            self.label_layout.setAlignment(label, Qt.AlignLeft)
        self.label_layout.addStretch()

    def closeEvent(self, event):
        self.par.close_dialog()
