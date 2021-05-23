from PyQt5.QtCore import QObject, pyqtSignal


class WorkerSignals(QObject):
    progress = pyqtSignal(object)
    update = pyqtSignal(object)
    send_data = pyqtSignal(object)
    connected = pyqtSignal()
