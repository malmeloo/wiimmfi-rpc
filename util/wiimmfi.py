import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime

import pypresence
import requests
from bs4 import BeautifulSoup

from .threading import Thread

game_info_base_url = 'https://wiimmfi.de/game/'


@dataclass
class WiimmfiPlayer:
    game_id: str
    game_name: str
    friend_code: str
    host: int
    status: int
    player_1: str
    player_2: str = ''
    start: int = 0
    priority: int = 1

    def __eq__(self, other):
        if isinstance(other, WiimmfiPlayer):
            return self.friend_code == other.friend_code
        return False

    def presence_options(self):
        options = dict()
        options['state'] = self.player_1
        if self.player_2:
            options['state'] += f' | {self.player_2}'
        options['details'] = '--'
        options['start'] = self.start

        options['pid'] = os.getpid()
        options['large_image'] = self.game_id.lower()
        options['large_text'] = self.game_name
        options['small_image'] = 'wiimmfi'
        options['small_text'] = 'Wiimmfi'

        return options


class WiimmfiPlayerList:
    def __init__(self, players=None):
        self._players = []

        if players is not None:
            self.add_players(players)

    def __len__(self):
        return len(self._players)

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


class WiimmfiCheckThread(Thread):
    friendly_progress = ""
    permanent = True
    name = 'WiimmfiCheckThread'

    def __init__(self, config):
        super().__init__()

        self.config = config
        self.last_player = None
        self.run = True

        self.presence = pypresence.Presence(self.config.preferences['rpc']['oauth_id'])
        self.presence.connect()

    def execute(self):
        while True:
            if not self.run:
                time.sleep(0.1)
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
                self.set_presence(online)

            time.sleep(self.config.preferences['rpc']['timeout'])

    def get_online_players(self, game_id):
        resp = requests.get(game_info_base_url + game_id)
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

            player = WiimmfiPlayer(game_name=game_name,
                                   game_id=data[0],
                                   friend_code=data[2],
                                   host=data[3],
                                   status=data[7],
                                   player_1=data[10],
                                   player_2=data[11],
                                   start=int(datetime.now().timestamp()))
            players.add_player(player)

        return players

    def set_presence(self, player):
        self.presence.update(**player.presence_options())

        self.log(logging.INFO, f'Now playing: {player.game_name}')

    def remove_presence(self):
        self.presence.clear()

        if self.last_player is None:
            pass
        else:
            self.log(logging.INFO, f'Stopped playing: {self.last_player.game_name}')
