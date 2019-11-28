from PyQt5 import QtWidgets as Qw


class OverviewTab(Qw.QWidget):
    OPTIONS = {
        'name': 'Overview',
        'debug': False
    }

    def __init__(self, parent, **params):
        super().__init__()

        self.parent = parent

        self.config = params.get('config')
        self.width = params.get('width')
        self.height = params.get('height')
