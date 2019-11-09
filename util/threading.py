import logging
import traceback

from PyQt5 import QtCore as Qc

logging.getLogger('__main__')


class ThreadSignals(Qc.QObject):
    """
    Signal definitions for our Thread

    finished: None
    - Signals thread finish
    error: msg
    - Show an error dialog with `msg` and stop the thread
    progress: int
    - Update progress bar percentage
    message: msg
    - Update thread status
    log: tuple
    - (level: int, msg: str)
    data: object
    - Send any result back. This is not handled by the ThreadManager,
      but should instead be connected to manually.
    """
    finished = Qc.pyqtSignal()
    error = Qc.pyqtSignal(str)
    progress = Qc.pyqtSignal(int)
    message = Qc.pyqtSignal(str)
    log = Qc.pyqtSignal(tuple)
    data = Qc.pyqtSignal(object)


class Thread(Qc.QThread):
    """
    Thread boilerplate.

    Implementations using a thread of some kind
    are expected to subclass, instantiate and add
    the thread to an instance of ThreadManager.

    Subclasses should override the class attributes below,
    as well as the execute() method which will be executed in a thread.
    This method should make use of Thread.emit_message() and Thread.emit_progress().

    Class attrs:
    - friendly_progress: str
        What the thread is doing. Example: "Checking for updates..."
        This can be overridden using Thread.emit_message().
    - permanent: bool
        Permanent threads are infinitely running threads that should be kept alive at all times.
        These threads will run regardless of whether another thread is running or not.
        Note: progress bar updates are disabled.
    """
    friendly_progress = ""
    permanent = False

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.args = args
        self.kwargs = kwargs
        self.signals = ThreadSignals()

    @Qc.pyqtSlot()
    def run(self):
        try:
            self.execute(*self.args, **self.kwargs)
        except:
            self.signals.error.emit(traceback.format_exc())
        else:
            self.signals.finished.emit()

    def execute(self, *args, **kwargs):
        """
        The actual code to run in a thread.

        Subclasses should override this method.
        """
        raise NotImplementedError("Subclasses of Thread should override Thread.execute()")

    def emit_finished(self):
        self.signals.finished.emit()

    def emit_error(self, msg: str):
        self.signals.error.emit(msg)

    def emit_progress(self, progress: int):
        if self.permanent:
            # No support for progress bar updates.
            return
        self.signals.progress.emit(progress)

    def emit_message(self, msg: str):
        self.signals.message.emit(msg)

    def emit_data(self, data):
        self.signals.data.emit(data)

    def log(self, *payload):
        self.signals.log.emit(payload)


class ThreadManager:
    """
    Manages our threads and provides signal callbacks for them,
    as well as updates our GUI status bar.
    Its purpose is to replace the PyQt5 ThreadPool class,
    since that does not allow adding threads and is less flexible.

    only one dynamic (non-permanent) thread can run at a time.
    """
    def __init__(self, **kwargs):
        self.thread_counter = kwargs.get('thread_counter')
        self.progress_bar = kwargs.get('progress_bar')
        self.thread_status = kwargs.get('thread_status')

        self.thread_queue = []
        self._permanent_threads = []

    def add_thread(self, thread: Thread):
        if thread.permanent:
            self._permanent_threads.append(thread)
            self.run_thread(thread)
        else:
            self.thread_queue.append(thread)

        if len(self.thread_queue) == 1:
            self.start_new_thread()

    def run_thread(self, thread: Thread):
        thread.signals.finished.connect(self._on_thread_finish)
        thread.signals.error.connect(self._on_thread_error)
        thread.signals.progress.connect(self._on_thread_progress)
        thread.signals.message.connect(self._on_thread_message)
        thread.signals.log.connect(self._on_thread_log)

        thread.start()
        self.thread_status.setText(thread.friendly_progress)

        return True

    def start_new_thread(self):
        """Checks if we can start a new thread and manages the queue."""
        if not self.thread_queue:
            # No threads in our queue.
            self.thread_status.setText('No operations.')
            return
        if self.thread_queue[0].isRunning():
            # A thread is already running.
            return

        new_thread = self.thread_queue[0]

        self.run_thread(new_thread)

    @Qc.pyqtSlot()
    def _on_thread_finish(self):
        """A thread finished."""
        thread = self.thread_queue.pop(0)

        thread.quit()
        thread.wait()

        self.progress_bar.reset()
        self.start_new_thread()

    Qc.pyqtSlot()
    def _on_thread_error(self, msg):
        """A thread reported an error."""

        # TODO: popup with error message
        print(msg)

        thread = self.thread_queue.pop(0)

        thread.quit()
        thread.wait()

        self.progress_bar.reset()
        self.start_new_thread()

    Qc.pyqtSlot()
    def _on_thread_progress(self, progress):
        """A thread wants to update its progress bar."""
        self.progress_bar.setValue(progress)

    Qc.pyqtSlot()
    def _on_thread_message(self, msg):
        """A thread wants to set its status message."""
        self.thread_status.setText(msg)

    Qc.pyqtSlot()
    def _on_thread_log(self, payload: tuple):
        logging.log(*payload)
