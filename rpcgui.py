from tkinter import *
from tkinter.ttk import *


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


class Application(Notebook):
    TABS = (OverviewTab, SettingsTab)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._add_tabs(self.TABS)

    def _add_tabs(self, tabs):
        for tab in tabs:
            self.add(tab(), **tab.OPTIONS)


if __name__ == '__main__':
    root = Tk()
    app = Application(root)
    app.pack(side="top", fill="both", expand=True)
    root.wm_geometry("400x400")
    root.mainloop()
