from PyQt5.QtCore import QObject, pyqtSignal


class GUISignals(QObject):
    switch_page = pyqtSignal(object)
    start_packet_receiver = pyqtSignal(object)
