import logging

from PyQt5 import QtWidgets as Qw

logging.getLogger(__name__)


class EditPopup(Qw.QWidget):
    def __init__(self, callback, replace_item=None, **values):
        super().__init__()
        self.callback = callback
        self.replace_item = replace_item

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

    def create_form(self):
        console_label = Qw.QLabel('Console:')
        self.console = Qw.QComboBox()
        self.console.addItems(['Wii', 'WiiWare', 'DS', 'DSiWare'])

        gameid_label = Qw.QLabel('Game ID:')
        self.game_id = Qw.QLineEdit()
        self.game_id.setMaxLength(6)

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

        index = self.console.findText(console)
        self.console.setCurrentIndex(index)
        self.game_id.setText(game_id)
        self.friend_code.setText(friend_code)
        self.priority.setValue(int(priority))

    def apply_settings(self):
        console = self.console.currentText()
        game_id = self.game_id.text()
        friend_code = self.friend_code.text()
        priority = str(self.priority.value())

        payload = {
            'console': console,
            'game_id': game_id,
            'friend_code': friend_code,
            'priority': priority
        }

        if self.replace_item is not None:
            self.replace_item.delete()
        self.callback(**payload)
        self.close()


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
        add_button = Qw.QPushButton('+')
        add_button.setMaximumSize(32, 32)
        add_button.clicked.connect(self.launch_popup)

        remove_button = Qw.QPushButton('-')
        remove_button.setMaximumSize(32, 32)

        edit_button = Qw.QPushButton('\U0001F589')  # pencil
        edit_button.setMaximumSize(32, 32)
        edit_button.font().setPointSize(5)

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

            item = Qw.QTreeWidgetItem([console, game_id, friend_code, priority])
            category.addChild(item)

    def launch_popup(self):
        item = self.tree.currentItem()
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

        self.popup = EditPopup(self.edit_code, replace_item=item, **values)

    def edit_code(self, **payload):
        console = payload.get('console')
        game_id = payload.get('game_id')
        friend_code = payload.get('friend_code')
        priority = payload.get('priority')

        category = self.CATEGORIES.get(console)

        item = Qw.QTreeWidgetItem([console, game_id, friend_code, priority])
        category.addChild(item)

        self.config.friend_codes.add(payload)
