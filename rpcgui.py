from tkinter import *
from tkinter.ttk import *

import util


class NotebookTab(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class OverviewTab(NotebookTab):
    OPTIONS = {
        'text': 'Overview'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SettingsTab(NotebookTab):
    OPTIONS = {
        'text': 'Settings'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DebugTab(NotebookTab):
    OPTIONS = {
        'text': 'Debug'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Application(Notebook):
    TABS = (OverviewTab, SettingsTab)
    DEBUG_TABS = (DebugTab,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = util.Config('preferences.yml')

        self._load_tabs()

    def _load_tabs(self):
        self._add_tabs(self.TABS)
        if self.config.debug:
            self._add_tabs(self.DEBUG_TABS)

    def _add_tabs(self, tabs):
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
