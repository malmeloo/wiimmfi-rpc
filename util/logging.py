import logging
import tkinter as tk


class GUILoggerHandler(logging.Handler):
    """Allows logging to a tkinter Text widget"""

    def __init__(self, widget=None):
        super().__init__()

        self._widget = widget
        self._buffer = ''

    def append_to_widget(self, msg):
        def append():
            self.widget.configure(state='normal')
            self.widget.insert(tk.END, msg + '\n')
            self.widget.configure(state='disabled')

            self.widget.yview(tk.END)

        self.widget.after(0, append)

    @property
    def widget(self):
        return self._widget

    @widget.setter
    def widget(self, widget):
        """We have been assigned a widget, flush the buffer log into it."""
        self._widget = widget
        self.append_to_widget(self._buffer)

        self._buffer = None

    def emit(self, record):
        msg = self.format(record)

        if self.widget is None:
            #  No widget yet to log to, save log into buffer.
            self._buffer += msg + '\n'
            return

        self.append_to_widget(msg)
