import json
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pypresence
import requests
from PyQt5 import QtCore as Qc
from bs4 import BeautifulSoup

from .msgboxes import MsgBoxes
from .threading import Thread

game_info_base_url = 'https://wiimmfi.de/game/{game_id}'
active_game_list_url = 'https://wiimmfi.de/game/'
mkw_room_info_base_url = 'https://wiimmfi.de/stats/mkw/room/p{pid}/?m=json'
wiimmfi_game_list_url = 'https://wiimmfi.de/stat?m=25'
asset_list_base_url = 'https://discordapp.com/api/v6/oauth2/applications/{app_id}/assets'
asset_base_url = 'https://cdn.discordapp.com/app-assets/{app_id}/{asset_id}.png'

cache_path = Path(sys.argv[0]).parent / 'data' / 'cache'


class WiimmfiPlayer:
    def __init__(self, **kwargs):
        self.game_id: str = kwargs.get('game_id')
        self.game_name: str = kwargs.get('game_name')
        self.pid: int = kwargs.get('pid')
        self.friend_code: str = kwargs.get('friend_code')
        self.status: str = kwargs.get('status')
        self.player_1: str = kwargs.get('player_1')
        self.player_2: str = kwargs.get('player_2')
        self.priority: int = kwargs.get('priority', 1)
        self.start: int = kwargs.get('start')

        self.is_mkw: bool = False
        self.n_members: int = 0
        self.n_players: int = 12
        self.track_name: str = ''

        self.has_game_art = True

    def __eq__(self, other):
        if isinstance(other, WiimmfiPlayer):
            return self.friend_code == other.friend_code
        return False

    def set_mkw_info(self):
        if self.game_id != 'RMCJ':
            self.is_mkw = False
            return

        headers = {
            'User-Agent': 'wiimmfi-rpc by DismissedGuy#2118 - github.com/DismissedGuy/wiimmfi-rpc'
        }
        resp = requests.get(mkw_room_info_base_url.format(pid=self.pid), headers=headers)
        resp.raise_for_status()
        data = resp.json()

        race_start = data[1].get('race_start')
        if not race_start:
            # race hasn't started yet or room is offline
            self.is_mkw = False
            return
        self.start = race_start
        self.n_members = data[1]['n_members']
        self.n_players = data[1]['n_players']
        self.track_name = data[1]['track'][1]

        self.is_mkw = True

    def presence_options(self, config):
        options = dict()

        if self.is_mkw:
            options['state'] = self.track_name
            options['party_size'] = [self.n_members, self.n_players]
        else:
            options['state'] = 'No player name'
            if self.player_1:
                options['state'] = self.player_1
                if self.player_2:
                    options['state'] += f' | {self.player_2}'

        options['details'] = config.statuses[self.status]
        options['start'] = self.start
        if self.has_game_art:
            options['large_image'] = self.game_id.lower()
        else:
            options['large_image'] = 'no_image'
        options['large_text'] = self.game_name
        options['small_image'] = 'wiimmfi'
        options['small_text'] = 'Wiimmfi'

        return options


class WiimmfiPlayerList:
    def __init__(self, players=None):
        self._players = []
        self._p_index = 0

        if players is not None:
            self.add_players(players)

    def __len__(self):
        return len(self._players)

    def __iter__(self):
        return iter(self._players)

    def __next__(self):
        index = self._p_index
        self._p_index += 1

        return index

    def add_player(self, player):
        if not isinstance(player, WiimmfiPlayer):
            raise ValueError('player arg must be instance of WiimmfiPlayer.')

        self._players.append(player)

    def add_players(self, players):
        for player in players:
            self.add_player(player)

    def get_player(self, friend_code):
        for player in self._players:
            if player.friend_code == friend_code:
                return player

        return None


class WiimmfiGame:
    def __init__(self, console: str, game_id: str, game_name: str, online_players: int):
        self.console = console
        self.game_id = game_id
        self.game_name = game_name
        self.online_players = online_players


class WiimmfiCheckThread(Thread):
    friendly_progress = ''
    permanent = True
    name = 'WiimmfiCheckThread'

    def __init__(self, config):
        super().__init__()

        self.config = config
        self.timeout_backoff = 0
        self.last_player = None
        self.run = True
        self.assets = None

        try:
            self.presence = pypresence.Presence(self.config.preferences['rpc']['oauth_id'])
            self.presence.connect()
        except (pypresence.PyPresenceException, ConnectionRefusedError):
            MsgBoxes.warn('It appears that your Discord client is not accepting requests. \n'
                          'Please try restarting it and then run this program again.')
            sys.exit()

    def execute(self):
        self.assets = self.get_asset_list()

        # download misc images
        self.save_game_art('no_image')

        # assign some time for the main thread to finish its things
        time.sleep(1)

        while True:
            if not self.run:
                time.sleep(1)
                self.remove_presence()
                continue

            online = None
            for code_entry in self.config.friend_codes:
                console, game_id, friend_code, priority = code_entry.values()

                online_players = self.get_online_players(game_id)
                if online_players is None:
                    continue

                player = online_players.get_player(friend_code)
                if player is None:
                    continue
                player.priority = priority

                if online is None or online.priority >= player.priority:
                    online = player

            if online is None:
                self.remove_presence()
                self.last_player = None
            elif online != self.last_player:
                self.last_player = online
                self.save_game_art(self.last_player.game_id)

                self.log(logging.INFO, f'Now playing: {online.game_name}')

            if self.last_player:
                if self.last_player.game_id == 'RMCJ':
                    self.last_player.set_mkw_info()
                self.set_presence(self.last_player)

            time.sleep(self.config.preferences['rpc']['min_timeout'] + self.timeout_backoff)

    def get_online_players(self, game_id):
        headers = {
            'User-Agent': 'wiimmfi-rpc by DismissedGuy#2118 - github.com/DismissedGuy/wiimmfi-rpc'
        }
        resp = requests.get(game_info_base_url.format(game_id=game_id), headers=headers)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')

        table = soup.find(id='online')
        if not table:
            self.log(logging.WARNING, f'Could not find game: {game_id}')
            return None
        elif not table.text:
            self.log(logging.WARNING, f'No people found online for game: {game_id}')
            return None

        rows = table.find_all('tr')
        game_name = rows[0].text

        players = WiimmfiPlayerList()
        for row in rows[2:]:
            data = [col.text for col in row.find_all('td')]

            if data[11] == '\u2014':
                # "em dash" means no player 2
                data[11] = ''

            player = WiimmfiPlayer(game_name=game_name,
                                   game_id=data[0],
                                   pid=data[1],
                                   friend_code=data[2],
                                   status=data[7],
                                   player_1=data[10],
                                   player_2=data[11],
                                   start=int(datetime.now().timestamp()))
            if player.game_id.lower() not in [a.get('name').lower() for a in self.assets]:
                player.has_game_art = False

            players.add_player(player)

        return players

    def get_active_games(self):
        """Retrieves games with online players"""
        headers = {
            'User-Agent': 'wiimmfi-rpc by DismissedGuy#2118 - github.com/DismissedGuy/wiimmfi-rpc'
        }
        resp = requests.get(active_game_list_url, headers=headers)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')

        # The game list HTML seems to be a little malformed, and it's messing with our parser.
        # Workaround: find all "tr0" and "tr1" classes (alternating game list colors) and concat them.
        # We also unpack dicts here because "class" is a reserved keyword.
        games_0 = soup.find_all(**{'class': 'tr0'})
        games_1 = soup.find_all(**{'class': 'tr1'})

        active_games_data = games_0 + games_1
        if not active_games_data:
            self.log(logging.WARNING, 'No active games found.')

            return []

        active_games = []
        for game in active_games_data:
            rows = game.find_all('td')

            console = rows[0].text
            game_name = rows[1].text
            game_id = rows[1].a['href'][6:]  # strip url part
            online_players = int(rows[4].text)

            game = WiimmfiGame(
                console=console,
                game_name=game_name,
                game_id=game_id,
                online_players=online_players
            )
            active_games.append(game)

        return active_games

    def get_asset_list(self):
        assets_url = asset_list_base_url.format(app_id=self.config.preferences['rpc']['oauth_id'])

        resp = requests.get(assets_url)
        resp.raise_for_status()

        return resp.json()

    def save_game_art(self, game_id):
        img_path = (cache_path / f'{game_id}.png')
        if img_path.exists():
            return

        asset_id = None
        for asset in self.assets:
            if asset.get('name') == game_id.lower():
                asset_id = asset.get('id')
                break

        if asset_id is None:
            self.log(logging.INFO, f'Could not find game art for game: {game_id}')
            return

        asset_url = asset_base_url.format(app_id=self.config.preferences['rpc']['oauth_id'], asset_id=asset_id)

        resp = requests.get(asset_url)
        resp.raise_for_status()

        with open(img_path, 'wb+') as file:
            file.write(resp.content)

        self.log(logging.INFO, f'Downloaded art for game: {game_id}')

    def set_presence(self, player):
        if self.timeout_backoff != 0:
            self.timeout_backoff = 0

            min_timeout = self.config.preferences['rpc']['min_timeout']
            self.log(logging.INFO, f'Reverting timeout back to {min_timeout}')

        self.presence.update(**player.presence_options(self.config))

    def remove_presence(self):
        self.presence.clear()

        if self.last_player is None:
            backoff = self.config.preferences['rpc']['timeout_backoff']
            min_timeout = self.config.preferences['rpc']['min_timeout']

            current_timeout = min_timeout + self.timeout_backoff
            if current_timeout >= self.config.preferences['rpc']['max_timeout']:
                return

            self.timeout_backoff += backoff
            current_timeout = min_timeout + self.timeout_backoff

            self.log(logging.INFO, f'Backing off timeout by {backoff}. Now set to {current_timeout}')
        else:
            self.log(logging.INFO, f'Stopped playing: {self.last_player.game_name}')


class WiimmfiOverviewThread(Thread):
    friendly_progress = ''
    permanent = True
    name = 'WiimmfiCheckThread'

    update_signal = Qc.pyqtSignal(WiimmfiPlayer)
    clear_signal = Qc.pyqtSignal()

    def __init__(self, wiimmfi_thread, update_callback, clear_callback):
        super().__init__()

        self.wiimmfi_thread = wiimmfi_thread
        self.update_callback = update_callback
        self.clear_callback = clear_callback

        self.update_signal.connect(self.update_callback)
        self.clear_signal.connect(self.clear_callback)

    def execute(self):
        while True:
            player = self.wiimmfi_thread.last_player
            if player is not None:
                self.update_signal.emit(player)
            else:
                self.clear_signal.emit()

            time.sleep(1)


class WiimmfiGameListThread(Thread):
    friendly_progress = ''
    permanent = True
    name = 'WiimmfiGameListThread'

    def execute(self):
        try:
            with (cache_path / 'wiimmfi_games.json').open('r') as file:
                data = json.load(file)

                last_update = datetime.utcfromtimestamp(data.get('updated', 0))
                now = datetime.utcnow()

                if last_update < now - timedelta(days=7):
                    return
        except (json.JSONDecodeError, FileNotFoundError):
            self.update_file()

    def update_file(self):
        headers = {
            'User-Agent': 'wiimmfi-rpc by DismissedGuy#2118 - github.com/DismissedGuy/wiimmfi-rpc'
        }
        resp = requests.get(wiimmfi_game_list_url, headers=headers)
        if resp.status_code != 200:
            return

        soup = BeautifulSoup(resp.text, 'html.parser')

        table = soup.find(id='game')
        if table is None:
            return

        games_list = []

        games = table.find_all('tr')[2:]
        for game in games:
            fields = game.find_all('td')
            games_list.append({
                'id': fields[0].text,
                'name': fields[1].text.strip()
            })

        now = datetime.utcnow()
        data = {
            'updated': now.timestamp(),
            'games': games_list
        }
        with (cache_path / 'wiimmfi_games.json').open('w+') as file:
            json.dump(data, file, indent=2)

        self.log(logging.INFO, 'Downloaded games list')
