from PyQt5 import QtWidgets as Qw


class OverviewTab(Qw.QWidget):
    OPTIONS = {
        'name': 'Overview',
        'debug': False
    }

    def __init__(self, **params):
        super().__init__()

        self.width = params.get('width')
        self.height = params.get('height')
