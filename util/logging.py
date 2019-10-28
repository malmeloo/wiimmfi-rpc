import logging


class GUILoggerHandler(logging.Handler):
    """Allows logging to a tkinter Text widget"""

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
