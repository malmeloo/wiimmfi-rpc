import sys
from pathlib import Path

from PyQt5 import QtGui as Qg
from PyQt5 import QtWidgets as Qw

import util

cache_dir = Path(sys.argv[0]).parent / 'data' / 'cache'


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

        self.overview_group = self.create_overview_group()
        self.mkw_group = self.create_mkw_group()

        self.layout = Qw.QVBoxLayout()
        self.layout.addWidget(self.overview_group)
        self.layout.addWidget(self.mkw_group)
        self.layout.addStretch(1)

        self.setLayout(self.layout)

        self.update_thread = util.WiimmfiOverviewThread(self.parent.wiimmfi_thread,
                                                        self.update_status, self.clear_overview)
        self.parent.thread_manager.add_thread(self.update_thread)

    def create_overview_group(self):
        groupbox = Qw.QGroupBox('Presence Overview')

        self.image = Qw.QLabel()

        self.presence_overview = Qw.QTextEdit()
        self.presence_overview.setReadOnly(True)
        self.presence_overview.setMaximumHeight(130)
        self.presence_overview.setStyleSheet('QTextEdit {background-color: rgba(0, 0, 0, 0); border: 0}')
        self.presence_overview.setText('Loading...')

        layout = Qw.QHBoxLayout()
        layout.addWidget(self.image)
        layout.addWidget(self.presence_overview)
        groupbox.setLayout(layout)

        return groupbox

    def create_mkw_group(self):
        groupbox = Qw.QGroupBox('Advanced Properties')

        self.advanced_properties = Qw.QTableWidget()
        self.advanced_properties.setRowCount(11)
        self.advanced_properties.setColumnCount(2)
        self.advanced_properties.setEditTriggers(Qw.QTableWidget.NoEditTriggers)
        self.advanced_properties.horizontalHeader().setVisible(False)
        self.advanced_properties.horizontalHeader().setStretchLastSection(True)
        self.advanced_properties.verticalHeader().setVisible(False)

        self.advanced_properties.setItem(0, 0, Qw.QTableWidgetItem('Game ID'))
        self.advanced_properties.setItem(1, 0, Qw.QTableWidgetItem('Game Name'))
        self.advanced_properties.setItem(2, 0, Qw.QTableWidgetItem('PID'))
        self.advanced_properties.setItem(3, 0, Qw.QTableWidgetItem('Friend Code'))
        self.advanced_properties.setItem(4, 0, Qw.QTableWidgetItem('Status'))
        self.advanced_properties.setItem(5, 0, Qw.QTableWidgetItem('Player 1'))
        self.advanced_properties.setItem(6, 0, Qw.QTableWidgetItem('Player 2'))
        self.advanced_properties.setItem(7, 0, Qw.QTableWidgetItem('Priority'))
        self.advanced_properties.setItem(8, 0, Qw.QTableWidgetItem('Game/race Start'))

        self.advanced_properties.setItem(9, 0, Qw.QTableWidgetItem('Room Size'))
        self.advanced_properties.setItem(10, 0, Qw.QTableWidgetItem('Room players'))
        self.advanced_properties.setItem(11, 0, Qw.QTableWidgetItem('Track Name'))

        layout = Qw.QHBoxLayout()
        layout.addWidget(self.advanced_properties)
        groupbox.setLayout(layout)

        return groupbox

    def update_status(self, player):
        self.set_image(player.game_id, player.game_name)
        self.set_overview(player)
        self.set_properties(player)

    def set_image(self, game_id, game_name):
        img_path = cache_dir / f'{game_id}.png'
        if not img_path.exists:
            img_path = cache_dir / 'notfound.png'

        path = str(img_path.resolve())
        pixmap = Qg.QPixmap(path)
        self.image.setPixmap(pixmap)
        self.image.setToolTip(game_name)

    def set_overview(self, player):
        text = '''
        <html>
          <b>Wiimmfi</b>
            <p>
              {details} <br/>
              {state} {party} <br/>
              {time}
            </p>
        </html>
        '''

        pres_options = player.presence_options()
        details = pres_options.get('details')
        state = pres_options.get('state')
        time = pres_options.get('start')
        party = ''
        if player.is_mkw:
            party = f'({player.n_members} of {player.n_players})'

        fmt_text = text.format(details=details, state=state, time=time, party=party)
        self.presence_overview.setText(fmt_text)

    def set_properties(self, player):
        self.advanced_properties.setItem(0, 1, Qw.QTableWidgetItem(player.game_id))
        self.advanced_properties.setItem(1, 1, Qw.QTableWidgetItem(player.game_name))
        self.advanced_properties.setItem(2, 1, Qw.QTableWidgetItem(player.pid))
        self.advanced_properties.setItem(3, 1, Qw.QTableWidgetItem(player.friend_code))
        self.advanced_properties.setItem(4, 1, Qw.QTableWidgetItem(player.status))
        self.advanced_properties.setItem(5, 1, Qw.QTableWidgetItem(player.player_1))
        self.advanced_properties.setItem(6, 1, Qw.QTableWidgetItem(player.player_2))
        self.advanced_properties.setItem(7, 1, Qw.QTableWidgetItem(player.priority))
        self.advanced_properties.setItem(8, 1, Qw.QTableWidgetItem(player.start))

        if player.is_mkw:
            self.advanced_properties.setItem(9, 1, Qw.QTableWidgetItem(player.n_members))
            self.advanced_properties.setItem(10, 1, Qw.QTableWidgetItem(player.n_players))
            self.advanced_properties.setItem(11, 1, Qw.QTableWidgetItem(player.track_name))
        else:
            for item in range(9, 12):
                self.advanced_properties.setItem(item, 1, Qw.QTableWidgetItem(''))

    def clear_overview(self):
        self.image.clear()
        self.presence_overview.setText('Not playing anything.')
        for item in range(12):
            self.advanced_properties.setItem(item, 1, Qw.QTableWidgetItem(''))
