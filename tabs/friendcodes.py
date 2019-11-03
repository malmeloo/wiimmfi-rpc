from PyQt5 import QtWidgets as Qw


class FriendcodesTab(Qw.QWidget):
    OPTIONS = {
        'name': 'Friend Codes',
        'debug': False
    }

    def __init__(self, **params):
        super().__init__()

        self.config = params.get('config')
        self.width = params.get('width')
        self.height = params.get('height')
