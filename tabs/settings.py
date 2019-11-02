from PyQt5 import QtWidgets as Qw


class SettingsTab(Qw.QWidget):
    OPTIONS = {
        'name': 'Settings',
        'debug': False
    }

    def __init__(self, **params):
        super().__init__()

        self.config = params.get('config')
        self.width = params.get('width')
        self.height = params.get('height')
