import os
import time
import json
from datetime import datetime
import logging
import traceback
from bs4 import BeautifulSoup
import requests
import rpc.rpc as rpc

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s',
    datefmt="%X"
)

# for explanations on how to edit these config files and their purposes,
# please see the README.
try:
    status_codes = json.load(open('config/status_codes.json'))
    friend_codes = {game:key.replace(' ', '-') for (game,key) in json.load(open('config/friend_codes.json')).items()}
    config = json.load(open('config/rpc_config.json'))
except json.decoder.JSONDecodeError:
    logging.critical(f'One of the config files seems to be invalid. This probably means that you edited it incorrectly. Please reinstall this program and refer to the README for the correct format.')
    exit()
except Exception as e:
    logging.critical('An unknown error has occured while trying to read one of the config files. Please try closing all programs and try again. Traceback:\n')
    traceback.print_tb(e.__traceback__)
    exit()

class wiimmfi_rpc():
    def __init__(self):
        logging.info(f'using codes: {friend_codes}')
        self.rpc_obj = rpc.DiscordIpcClient.for_platform(config['rpc_id'])
        logging.info('Rich Presence initialized, listening for changes...')

    def get_online_data(self, game):
        html = requests.get('https://wiimmfi.de/game/' + game).text
        soup = BeautifulSoup(html, 'html.parser')

        table = soup.find(id='online')
        if not table: # no game found
            logging.warning(f'No such game with ID "{game}" was found!')
            return
        elif not table.text: # no people online
            return

        rows = table.find_all('tr')
        self.full_game_name = rows[0].text # useful for more detailed rpc

        data = [[ele.text for ele in row.find_all('td')] for row in rows[2:]]

        return data

    def get_mkwii_data(self, online_data):
        room_data = requests.get(f'https://wiimmfi.de/mkw/room/p{online_data[1]}/?m=json').json()
        if room_data[1]['type'] == 'end':
            return

        host = next((player['names'][0] for player in room_data[1]['members'] if player['ol_role'] == 'host'), None)
        status = f'{status_codes[online_data[7]]} | ' + ('Hosting' if online_data[10] == host else f'Host: {host}')

        return {'state': status}

    def check_online(self, game):
        game, code = game
        online_list = self.get_online_data(game.replace('/', '').replace('\\', ''))
        if not online_list: # returns false when not found
            return

        our_user = next((usr for usr in online_list if usr[2] == code), None)
        if our_user:
            return our_user

    def change_presence(self, pres_data, start_time=None):
        if not pres_data: # no data to send, we'll clear the rpc
            to_send = {'cmd': 'SET_ACTIVITY',
                'args': {'pid': os.getpid()},
                'nonce': '0' # gotta input something /shrug
            }
            logging.info('Rich Presence has been removed')
            return self.rpc_obj.send(to_send)

        activity = {
            'state': status_codes[pres_data[7]],
            'timestamps': {'start': start_time},
        }

        if pres_data[0] == 'RMCJ' and pres_data[7] != '1' and config['show_mkwii_room_data']:
            # playing mkwii friend room, show extra presence
            user_room = self.get_mkwii_data(pres_data)
            if user_room:
                activity.update(user_room)

        user1 = pres_data[10]
        user2 = pres_data[11]
        if user1:
            activity['details'] = user1 + (f' | {user2}' if user2 else '')

        if config["show_game"]:
            activity['assets'] = {
                	'large_image': pres_data[0].lower(),
                    'large_text': self.full_game_name,

                    'small_image': 'wiimmfi',
                    'small_text': 'Wiimmfi'
            }

        self.rpc_obj.set_activity(activity)

def main():
    wiimmfi_obj = wiimmfi_rpc()
    last_game = None #game ID can be found at index 0
    last_status = None
    start_time = None

    while 1:
        is_playing = False
        for game in friend_codes.items():
            online_data = wiimmfi_obj.check_online(game)
            if online_data:
                is_playing = True
                if last_game == online_data[0] and last_status == online_data[7]:
                    #user still playing same game, do nothing
                    pass
                elif last_game == online_data[0] and last_status != online_data[7]:
                    #playing same game, changed statuses
                    logging.info(f'User is now {status_codes[online_data[7]]}')
                    last_status = online_data[7]
                    wiimmfi_obj.change_presence(online_data, start_time)
                else:
                    logging.info(f'Friend code {game[1]} changed game to {wiimmfi_obj.full_game_name}')
                    last_game = online_data[0]
                    last_status = online_data[7]
                    start_time = time.time()
                    wiimmfi_obj.change_presence(online_data, start_time)

        if not is_playing and last_game:
            # user not found online on any game, remove rpc
            logging.info('User went offline')
            last_game = None
            last_status = None
            start_time = None
            wiimmfi_obj.change_presence(None)

        try:
            time.sleep(config['timeout'])
        except KeyboardInterrupt:
            # don't show traceback
            exit()

if __name__ == '__main__':
    main()
