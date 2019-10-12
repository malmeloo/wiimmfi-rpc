import logging
from tkinter import *
from tkinter import scrolledtext
from tkinter.ttk import *

import util

logging.basicConfig(filename='test.log',
                    level=logging.INFO)


class OverviewTab(Frame):
    OPTIONS = {
        'text': 'Overview'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SettingsTab(Frame):
    OPTIONS = {
        'text': 'Settings'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LogsTab(Frame):
    OPTIONS = {
        'text': 'Logs'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.build()

    def build(self):
        log_window = scrolledtext.ScrolledText(self, state='disabled')
        log_window.configure(font='TkFixedFont')
        log_window.pack()

        handler = util.GUILoggerHandler(log_window)
        formatter = logging.Formatter('[%(asctime)s, %(threadName)s, %(levelname)s] %(message)s')
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.addHandler(handler)


class Application(Notebook):
    TABS = (OverviewTab, SettingsTab)
    DEBUG_TABS = (LogsTab,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = util.Config('preferences.yml')

        self.load_tabs()

    def load_tabs(self):
        self.add_tabs(self.TABS)
        if self.config.debug:
            self.add_tabs(self.DEBUG_TABS)

    def add_tabs(self, tabs):
        for tab in tabs:
            tab.config = self.config
            self.add(tab(), **tab.OPTIONS)


if __name__ == '__main__':
    root = Tk()
    app = Application(root)
    app.pack(side="top", fill="both", expand=True)

    root.wm_geometry("400x400")
    root.title(f'Wiimmfi-RPC v{app.config.version}')

    root.mainloop()
