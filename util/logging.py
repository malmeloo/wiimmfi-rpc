import logging
import sys
from pathlib import Path
from datetime import datetime

class GUILoggerHandler(logging.Handler):
    """Allows logging to a PyQt5 PlainTextEdit widget."""

    def __init__(self, widget=None):
        super().__init__()

        self._widget = widget
        self._buffer = ''

    @property
    def widget(self):
        return self._widget

    @widget.setter
    def widget(self, widget):
        """We have been assigned a widget, flush the buffer log into it."""
        self._widget = widget
        self.append(self._buffer.strip())

        self._buffer = None

    def append(self, msg):
        self.widget.appendPlainText(msg)

    def emit(self, record):
        msg = self.format(record)

        if self.widget is None:
            #  No widget yet to log to, save log into buffer.
            self._buffer += msg + '\n'
            return

        self.append(msg)


class FileLoggerHandler(logging.Handler):
    """Keeps track of all logs and stores them in a file. Features error log generation."""
    def __init__(self):
        super().__init__()

        self._fn = self._get_filename()
        self._buffer = ''

    def _get_filename(self):
        log_dir = (Path(sys.argv[0]).parent / 'logs')
        time = datetime.now()

        time_text = time.strftime('%Y%m%d')
        ext = 0
        file = (log_dir / f'{time_text}.log')
        while file.exists():
            file = (log_dir / f'{time_text}-{ext}.log')
            ext += 1

        return file

    def emit(self, record):
        msg = self.format(record)

        self._buffer += msg + '\n'
        with open(self._fn, 'w+') as file:
            file.write(self._buffer)
