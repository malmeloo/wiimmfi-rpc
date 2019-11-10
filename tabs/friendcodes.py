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

        self.create_tree()

        self.layout = Qw.QVBoxLayout()
        self.layout.addWidget(self.tree)

        self.setLayout(self.layout)

    def create_tree(self):
        self.tree = Qw.QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(['Console', 'Game', 'Friend Code'])

        self.wii_entry = Qw.QTreeWidgetItem(['Wii', '-', '-'])
        self.wiiware_entry = Qw.QTreeWidgetItem(['WiiWare', '-', '-'])
        self.ds_entry = Qw.QTreeWidgetItem(['DS', '-', '-'])
        self.dsiware_entry = Qw.QTreeWidgetItem(['DSiWare', '-', '-'])

        self.tree.addTopLevelItems([self.wii_entry, self.wiiware_entry,
                                    self.ds_entry, self.dsiware_entry])
