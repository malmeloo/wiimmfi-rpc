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

    def _add_friendcode(self, widget: Qw.QTreeWidgetItem):
        print('Add code:')
        print(widget)

    def _refresh_tree(self):
        self.refresh_button.setDisabled(True)

        self.player_tree.clear()

        active_games = self.parent.wiimmfi_thread.get_active_games()
        active_games = sorted(active_games, key=lambda g: g.console)

        for game in active_games:
            online_players = self.parent.wiimmfi_thread.get_online_players(game.game_id)
            online_players = sorted(online_players, key=lambda p: p.player_1)
            print(f'Getting online players for game {game.game_id}')
            if not online_players:
                continue

            parent_item = Qw.QTreeWidgetItem([game.console, game.game_name, '', ''])
            self.player_tree.addTopLevelItem(parent_item)

            for player in online_players:
                players = [player.player_1]
                if player.player_2:
                    players.append(player.player_2)
                player_names = ' / '.join(players)

                child_item = Qw.QTreeWidgetItem(['', player_names, player.friend_code, ''])
                parent_item.addChild(child_item)

                add_button = Qw.QPushButton('+')
                add_button.setMaximumSize(32, 32)
                add_button.pressed.connect(lambda: self._add_friendcode(child_item))
                self.player_tree.setItemWidget(child_item, 3, add_button)

            parent_item.setExpanded(True)

        self.player_tree.resizeColumnToContents(0)
        self.player_tree.resizeColumnToContents(2)
        self.player_tree.resizeColumnToContents(3)

        self.player_tree.header().setStretchLastSection(False)
        self.player_tree.header().setSectionResizeMode(1, Qw.QHeaderView.Stretch)

        self.refresh_button.setDisabled(False)

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
