import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from util import checks


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

    def _get_dir_structure(self, path):
        files = []

        for f in path.iterdir():
            if f.name.startswith('.') or f.name.startswith('_') or f.name == 'venv':
                continue  # skip unimportant files

            if f.is_dir():
                files += self._get_dir_structure(f)
            else:
                files.append(os.path.relpath(f.absolute(), Path(sys.argv[0]).parent.absolute()))

        return files

    def create_error_log(self, traceback):
        script_dir = Path(sys.argv[0]).parent
        error_log_path = (script_dir / 'logs' / 'errors' / self._fn.name)
        date = datetime.now().strftime('%c')

        with open(error_log_path, 'w+') as file:
            file.write(f'------------ [EXCEPTION RAPPORT AT {date}] ------------\n')
            file.write(''.join(traceback) + '\n')
            file.write('----- [PROGRAM INFO]\n')
            file.write(f'Bundled: {checks.is_bundled()}' + '\n')
            file.write('----- [DIRECTORY STRUCTURE]\n')
            file.write('\n'.join(self._get_dir_structure(script_dir)))

        return error_log_path

    def emit(self, record):
        msg = self.format(record)

        self._buffer += msg + '\n'
        with open(self._fn, 'w+') as file:
            file.write(self._buffer)
