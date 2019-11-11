import logging

from PyQt5 import QtWidgets as Qw

logging.getLogger(__name__)


class FriendcodesTab(Qw.QWidget):
    OPTIONS = {
        'name': 'Friend Codes',
        'debug': False
    }

    CATEGORIES = {
        'Wii': Qw.QTreeWidgetItem(['Wii', '-', '-', '-']),
        'WiiWare': Qw.QTreeWidgetItem(['WiiWare', '-', '-', '-']),
        'DS': Qw.QTreeWidgetItem(['DS', '-', '-', '-']),
        'DSiWare': Qw.QTreeWidgetItem(['DSiWare', '-', '-', '-'])
    }

    def __init__(self, **params):
        super().__init__()

        self.config = params.get('config')
        self.width = params.get('width')
        self.height = params.get('height')

        self.button_layout = self.create_buttons()
        self.tree = self.create_tree()
        self.populate_tree()

        self.layout = Qw.QVBoxLayout()
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.tree)

        self.setLayout(self.layout)

    def create_buttons(self):
        button_layout = Qw.QHBoxLayout()

        add_button = Qw.QPushButton('+')
        add_button.setMaximumSize(32, 32)
        remove_button = Qw.QPushButton('-')
        remove_button.setMaximumSize(32, 32)
        edit_button = Qw.QPushButton('\U0001F589')  # pencil
        edit_button.setMaximumSize(32, 32)
        edit_button.font().setPointSize(5)

        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(edit_button)
        button_layout.addStretch()

        return button_layout

    def create_tree(self):
        tree = Qw.QTreeWidget()
        tree.setColumnCount(4)
        tree.setHeaderLabels(['Console', 'Game', 'Friend Code', 'Priority'])

        tree.addTopLevelItems(self.CATEGORIES.values())

        return tree

    def populate_tree(self):
        codes = self.config.friend_codes

        for entry in codes.__dict__():
            console = entry.get('console')
            game_id = entry.get('game_id')
            friend_code = entry.get('friend_code')
            priority = entry.get('priority')

            category = self.CATEGORIES.get(console)

            if not (console or game_id or friend_code or priority or category):
                logging.warning(f'Detected invalid friend code entry: {game_id}')
                continue

            item = Qw.QTreeWidgetItem(['', game_id, friend_code, priority])
            category.addChild(item)
