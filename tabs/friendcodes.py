import json
import logging
import sys
from pathlib import Path

from PyQt5 import QtCore as Qc
from PyQt5 import QtWidgets as Qw

logging.getLogger(__name__)

cache_path = Path(sys.argv[0]).parent / 'data' / 'cache'


class EditPopup(Qw.QWidget):
    def __init__(self, callback, replace_item=None, **values):
        super().__init__()
        self.callback = callback
        self.replace_item = replace_item

        self.games = []
        self.prepare_game_data()

        self.setWindowTitle('Modify friend code')
        self.setGeometry(0, 0, 300, 200)

        self.form = self.create_form()
        self.buttons = self.create_buttons()

        if values:
            self.load_values(values)

        self.layout = Qw.QVBoxLayout()
        self.layout.addLayout(self.form)
        self.layout.addLayout(self.buttons)

        self.setLayout(self.layout)

        self.show()

    def prepare_game_data(self):
        try:
            with (cache_path / 'wiimmfi_games.json').open('r') as file:
                data = json.load(file)
                games = sorted(data.get('games'), key=lambda i: i.get('name'))
                for game in games:
                    game_id = game.get('id')
                    name = game.get('name')
                    self.games.append(f'{game_id} - {name}')
        except FileNotFoundError:
            return

    def on_complete(self, text):
        game_id, _ = text.split(' - ')
        Qc.QTimer.singleShot(10, lambda: self.game_id.setText(game_id))

    def create_form(self):
        console_label = Qw.QLabel('Console:')
        self.console = Qw.QComboBox()
        self.console.addItems(['Wii', 'WiiWare', 'DS', 'DSiWare'])

        gameid_label = Qw.QLabel('Game ID:')
        self.game_id = Qw.QLineEdit()
        if self.games:
            completer = Qw.QCompleter(self.games)
            completer.setCaseSensitivity(Qc.Qt.CaseInsensitive)
            completer.setFilterMode(Qc.Qt.MatchContains)
            completer.activated.connect(self.on_complete)
            self.game_id.setCompleter(completer)

        friendcode_label = Qw.QLabel('Friend code:')
        self.friend_code = Qw.QLineEdit()
        self.friend_code.setMaxLength(15)  # xxxx-xxxx-xxxx = 15 chars

        priority_label = Qw.QLabel('Priority:')
        self.priority = Qw.QSpinBox()
        self.priority.setRange(1, 5)

        layout = Qw.QFormLayout()
        layout.addRow(console_label, self.console)
        layout.addRow(gameid_label, self.game_id)
        layout.addRow(friendcode_label, self.friend_code)
        layout.addRow(priority_label, self.priority)

        return layout

    def create_buttons(self):
        ok_button = Qw.QPushButton('Ok')
        ok_button.clicked.connect(self.apply_settings)

        cancel_button = Qw.QPushButton('Cancel')
        cancel_button.clicked.connect(self.close)

        layout = Qw.QHBoxLayout()
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)

        return layout

    def load_values(self, values):
        console = values.get('console')
        game_id = values.get('game_id')
        friend_code = values.get('friend_code')
        priority = values.get('priority')
        if priority == '':
            priority = 0

        index = self.console.findText(console)
        self.console.setCurrentIndex(index)
        self.game_id.setText(game_id)
        self.friend_code.setText(friend_code)
        self.priority.setValue(int(priority))

    def apply_settings(self):
        console = self.console.currentText()
        game_id = self.game_id.text().upper()
        friend_code = self.friend_code.text()
        priority = str(self.priority.value())

        payload = {
            'console': console,
            'game_id': game_id,
            'friend_code': friend_code,
            'priority': priority
        }

        self.callback(delete_item=self.replace_item, **payload)
        self.close()


class FriendcodesTab(Qw.QWidget):
    OPTIONS = {
        'name': 'Friend Codes',
        'debug': False
    }

    CATEGORIES = {
        'Wii': Qw.QTreeWidgetItem(['Wii', '', '', '']),
        'WiiWare': Qw.QTreeWidgetItem(['WiiWare', '', '', '']),
        'NDS': Qw.QTreeWidgetItem(['DS', '', '', '']),
        'DSiWare': Qw.QTreeWidgetItem(['DSiWare', '', '', ''])
    }

    def __init__(self, parent, **params):
        super().__init__()

        self.parent = parent

        self.config = params.get('config')

        self.button_layout = self.create_buttons()

        self.tree = self.create_tree()
        self.tree.setColumnWidth(0, 90)
        self.tree.setColumnWidth(1, 60)
        self.tree.setColumnWidth(2, 140)
        self.populate_tree()

        self.layout = Qw.QVBoxLayout()
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.tree)

        self.setLayout(self.layout)

        # Reload the tree when the user switches to this tab.
        # This way, we can reflect changes made to the friend codes
        # by other processes or tabs without complicated signalling.
        self.parent.table_widget.tabs.currentChanged.connect(self._on_tab_changed)

    def _on_tab_changed(self, tab_index):
        if tab_index == 1:  # our tab
            self.populate_tree()

    def create_buttons(self):
        add_button = Qw.QPushButton('+')
        add_button.setMaximumSize(32, 32)
        add_button.clicked.connect(lambda: self.launch_popup(modify=False))

        remove_button = Qw.QPushButton('-')
        remove_button.setMaximumSize(32, 32)
        remove_button.clicked.connect(self.remove_code)

        edit_button = Qw.QPushButton('\U0001F589')  # pencil
        edit_button.setMaximumSize(32, 32)
        edit_button.font().setPointSize(5)
        edit_button.clicked.connect(lambda: self.launch_popup(modify=True))

        button_layout = Qw.QHBoxLayout()
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
        # clear existing codes
        for item_index in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(item_index)
            for _ in range(item.childCount()):
                item.removeChild(item.child(0))

        codes = self.config.friend_codes

        for entry in codes:
            console = entry.get('console')
            game_id = entry.get('game_id')
            friend_code = entry.get('friend_code')
            priority = entry.get('priority')

            if console == 'DS':  # backwards compat
                console = 'NDS'

            category = self.CATEGORIES.get(console)
            if not category:
                logging.warning(f'Invalid console found in friend code entry: {console}')
                continue

            if not (console or game_id or friend_code or priority or category):
                logging.warning(f'Detected invalid friend code entry: {game_id}')
                continue

            item = Qw.QTreeWidgetItem([console, game_id, friend_code, priority])
            category.addChild(item)

    def launch_popup(self, modify):
        item = self.tree.currentItem()
        if modify and item in self.CATEGORIES.values():  # tries to edit category
            return
        if not item:
            self.popup = EditPopup(self.edit_code, replace_item=None)
            return

        console = item.text(0)
        game_id = item.text(1)
        friend_code = item.text(2)
        priority = item.text(3)

        values = {
            'console': console,
            'game_id': game_id,
            'friend_code': friend_code,
            'priority': priority
        }

        replace_item = item if modify else None

        self.popup = EditPopup(self.edit_code, replace_item=replace_item, **values)

    def edit_code(self, delete_item=None, **payload):
        console = payload.get('console')
        game_id = payload.get('game_id')
        friend_code = payload.get('friend_code')
        priority = payload.get('priority')

        category = self.CATEGORIES.get(console)

        self.config.friend_codes.append(payload)

        if delete_item is not None:
            old_console = delete_item.text(0)
            old_game_id = delete_item.text(1)
            old_friend_code = delete_item.text(2)
            old_priority = delete_item.text(3)

            delete_item.setText(0, console)
            delete_item.setText(1, game_id)
            delete_item.setText(2, friend_code)
            delete_item.setText(3, priority)

            old_config_item = {
                'console': old_console,
                'game_id': old_game_id,
                'friend_code': old_friend_code,
                'priority': old_priority
            }

            self.config.friend_codes.remove(old_config_item)
        else:
            item = Qw.QTreeWidgetItem([console, game_id, friend_code, priority])
            category.addChild(item)

    def remove_code(self):
        item = self.tree.currentItem()
        if not item or not item.parent():
            # nothing selected or trying to delete top level item
            return

        console = item.text(0)
        game_id = item.text(1)
        friend_code = item.text(2)
        priority = item.text(3)

        category = self.CATEGORIES.get(console)

        config_item = {
            'console': console,
            'game_id': game_id,
            'friend_code': friend_code,
            'priority': priority
        }

        category.removeChild(item)
        self.config.friend_codes.remove(config_item)
