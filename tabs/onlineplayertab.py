from PyQt5 import QtWidgets as Qw


class OnlinePlayerTab(Qw.QWidget):
    OPTIONS = {
        'name': 'Online Players',
        'debug': False
    }

    def __init__(self, parent, **params):
        super().__init__()

        self.parent = parent
        self.config = params.get('config')

        self.refresh_button = None

        self.header = self.create_header()
        self.player_tree = self.create_tree()

        self.layout = Qw.QVBoxLayout()
        self.layout.addLayout(self.header)
        self.layout.addWidget(self.player_tree)
        self.setLayout(self.layout)

    def _refresh_tree(self):
        print('Refresh')

    def _search_tree(self, friend_code):
        print(f'Search {friend_code}')

    def create_header(self):
        self.refresh_button = Qw.QPushButton('\u21BB Refresh')
        self.refresh_button.clicked.connect(self._refresh_tree)

        search_field = Qw.QLineEdit()
        search_field.textChanged.connect(self._search_tree)
        search_field.setPlaceholderText('Search for a FC...')

        layout = Qw.QHBoxLayout()
        layout.addWidget(self.refresh_button)
        layout.addStretch()
        layout.addWidget(search_field)

        return layout

    def create_tree(self):
        tree = Qw.QTreeWidget()
        tree.setColumnCount(4)

        return tree
