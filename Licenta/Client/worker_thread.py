from PyQt5.QtCore import QRunnable
from Client.worker_signal import WorkerSignals


class Worker(QRunnable):
    def __init__(self, function, *args, **kwargs):
        super(Worker, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.kwargs['progress_callback'] = self.signals.progress
        self.kwargs['update_callback'] = self.signals.update
        self.kwargs['send_data'] = self.signals.send_data
        self.kwargs['connected'] = self.signals.connected
        self.kwargs['close_session'] = self.signals.close_session
        self.kwargs['test_timer'] = self.signals.test_timer

    def run(self):
        self.function(*self.args, **self.kwargs)
