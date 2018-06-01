import os
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import logging
import rpc.rpc as rpc

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s.%(msecs)03d] %(message)s',
    datefmt="%X"
)

# for explanations on how to edit these config files and their purposes,
# please see the README.
status_codes = json.load(open('config/status_codes.json'))
friend_codes = json.load(open('config/friend_codes.json'))
config = json.load(open('config/rpc_config.json'))

class wiimmfi_rpc():
    def __init__(self):
        logging.info(f'using codes: {friend_codes}')
        self.rpc_obj = rpc.DiscordIpcClient.for_platform(config['rpc_id'])
        logging.info('Rich Presence initialized, listening for changes...')

    def get_online_data(self, game):
        html = requests.get('https://wiimmfi.de/game/' + game).text
        soup = BeautifulSoup(html, 'html.parser')

        table = soup.find(id='online')
        if not table: # either wrong game name or no people online, can't tell
            return
        rows = table.find_all('tr')
        self.full_game_name = rows[0].text # useful for more detailed rpc

        data = [[ele.text for ele in row.find_all('td')] for row in rows[2:]]
        return data

    def check_online(self, game):
        game, code = game
        online_list = self.get_online_data(game)
        if not online_list: # returns false when not found
            return

        our_user = next((usr for usr in online_list if usr[2] == code), None)
        if our_user: # user was found online!
            return our_user
        return

    def change_presence(self, pres_data, game=None):
        if not pres_data: # no data to send, we'll clear the rpc
            to_send = {'cmd': 'SET_ACTIVITY',
                'args': {'pid': os.getpid()},
                'nonce': '0' # gotta input something /shrug
            }
            logging.info('Rich Presence has been removed')
            return self.rpc_obj.send(to_send)

        activity = {
            'state': status_codes[pres_data[7]],
            'timestamps': {'start': time.time()},
        }

        username = pres_data[10]
        if username:
            activity['details'] = username

        if int(config["show_game"]):
            activity['assets'] = {
                	'large_image': game,
                    'large_text': self.full_game_name,

                    'small_image': 'wiimmfi',
                    'small_text': 'Wiimmfi'
            }
        logging.info('updating rpc')
        self.rpc_obj.set_activity(activity)

def main():
    wiimmfi_obj = wiimmfi_rpc()
    last_game = None #game ID can be found at index 0

    while 1:
        is_playing = False
        for game in friend_codes.items():
            online_data = wiimmfi_obj.check_online(game)
            if online_data:
                is_playing = True
                if last_game == online_data[0]:
                    #user still playing same game, do nothing
                    pass
                else:
                    logging.info(f'Friend code {game[1]} changed game to {wiimmfi_obj.full_game_name}')
                    last_game = online_data[0]
                    wiimmfi_obj.change_presence(online_data, game[0])

        if not is_playing and last_game:
            # user not found online on any game, remove rpc
            logging.info('User went offline')
            last_game = None
            wiimmfi_obj.change_presence(None)

        time.sleep(config['timeout'])

if __name__ == '__main__':
    main()
