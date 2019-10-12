import logging
import tkinter as tk


class GUILoggerHandler(logging.Handler):
    """Allows logging to a tkinter Text widget"""

    def __init__(self, widget):
        super().__init__()

        self.widget = widget

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.widget.configure(state='normal')
            self.widget.insert(tk.END, msg + '\n')
            self.widget.configure(state='disabled')

            self.widget.yview(tk.END)

        self.widget.after(0, append)
