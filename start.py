import os
import time
import sys
import logging
import requests
import traceback
import rpc.rpc as rpc
from ruamel.yaml import YAML
from datetime import datetime
from bs4 import BeautifulSoup

yaml = YAML(typ='safe')
now = datetime.utcnow()

def exception_handler(exc_type, exc_value, tb):
    if not exc_type == KeyboardInterrupt:
        # don't handle when user exits on purpose
        print(f'{exc_value}\n')
        print('Shoot! An unhandled error has occured. Building traceback...')

        with open('logs/crashes/{0.day}.{0.month}.{0.year}.log'.format(now), 'a+') as f:
            f.write('-------- CRASH AT {0.hour}:{0.minute}:{0.second} --------\n'.format(now))
            f.write(f'LINE: {tb.tb_lineno}\n')
            f.write(f'NEXT: {tb.tb_next}\n')
            f.write(f'TYPE: {exc_type}\n')
            f.write(f'VALUE: {exc_value}\n')
            f.write('-- FULL TRACEBACK --\n')
            f.write(''.join(traceback.format_exception(exc_type, exc_value, tb)))

        print('Successfully created traceback in:')
        print('logs/crashes/{0.day}.{0.month}.{0.year}.log\n'.format(now))
        print('Please contact the creator (DismissedGuy#2118) on Discord and attach this file to your message.')

    sys.exit()
sys.excepthook = exception_handler

# for explanations on how to edit these config files and their purposes,
# please see the README.
try:
    status_codes = yaml.load(open('config/status_codes.yaml'))
    friend_codes = {game:key.replace(' ', '-') for (game,key) in yaml.load(open('config/friend_codes.yaml')).items()}
    config = yaml.load(open('config/rpc_config.yaml'))
except Exception as e:
    print('An error has occured while trying to read one of the config files.\n')
    raise e

if 'RAAE' in friend_codes.keys():
    print('Please insert the RPC Startup Disc!')
    print('This will set up your Rich Presence.')

    rpc_obj = rpc.DiscordIpcClient.for_platform(config['rpc_id'])
    activity = {
    'state': 'Setting up RPC',
    'timestamps': {'start': time.time()},
    'assets': {
        'large_image': 'startup_disc',
        'large_text': 'RPC Startup Disc'
        }
    }
    rpc_obj.set_activity(activity)

    input()

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s',
    datefmt="%X",
    handlers=[
    logging.FileHandler('logs/starts/{0.day}.{0.month}.{0.year}.log'.format(now)),
    logging.StreamHandler()
    ]
)
logging.info('-------- BOOT AT {0.hour}:{0.minute}:{0.second} --------'.format(now))

class wiimmfi_rpc():
    def __init__(self):
        logging.info(f'{len(friend_codes)} game(s) registered')
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
            logging.info('Rich Presence has been removed.')
            return self.rpc_obj.send(to_send)

        activity = {
            'state': status_codes[pres_data[7]],
            'timestamps': {'start': start_time},
        }

        user1 = pres_data[10]
        user2 = pres_data[11]
        if user1:
            activity['details'] = user1 + (f' | {user2}' if user2 else '')

        activity['assets'] = {
            	'large_image': pres_data[0].lower(),
                'large_text': self.full_game_name,

                'small_image': 'wiimmfi',
                'small_text': 'Wiimmfi'
        }

        if pres_data[0] == 'RMCJ' and pres_data[7] != '1' and config['show_mkwii_room_data']:
            # playing mkwii friend room, show extra presence
            user_room = self.get_mkwii_data(pres_data)
            if user_room:
                activity.update(user_room)

        self.rpc_obj.set_activity(activity)

class GUI():
    def __init__(self):
        self.main_menu()

    def clear(self, print_header=True):
        os.system('cls' if sys.platform.startswith('win') else 'clear')
        if print_header:
            print('wiimmfi-rpc by DismissedGuy#2118')
            print('-----------------------------------------------------\n')
    def openeditor(self):
        if sys.platform.startswith('darwin'):
            subprocess.call(('open config/friend_codes.yaml'))
        elif os.name == 'nt':
            os.startfile('config/friend_codes.yaml')
        elif os.name == 'posix':
            subprocess.call(('xdg-open config/friend_codes.yaml'))

    def main_menu(self):
        self.clear()
        print('Please enter a number!')
        print('1. Start up the rich presence')
        print('2. Edit your friend codes')
        print('3. Exit\n')

        done = False
        while not done:
            choice = input('> ')
            print(choice)
            actions = {
                '1': start_script,
                '2': self.edit_codes,
                '3': sys.exit
                }
            try:
                to_do = actions[choice]
            except KeyError:
                print('Invalid choice.')
                continue
            done = True
            self.clear(print_header=False)
            to_do()

    def edit_codes(self):
        print('Opening the friend-codes config...')
        openeditor()
        print('Press Enter to return to the main menu.')
        input()
        self.main_menu()

def start_script():
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
                    logging.info(f'Friend code {game[1]} changed game to {wiimmfi_obj.full_game_name}.')
                    last_game = online_data[0]
                    last_status = online_data[7]
                    start_time = time.time()
                    wiimmfi_obj.change_presence(online_data, start_time)

        if not is_playing and last_game:
            # user not found online on any game, remove rpc
            logging.info('User went offline.')
            last_game = None
            last_status = None
            start_time = None
            wiimmfi_obj.change_presence(None)

        time.sleep(config['timeout'])

def main():
    GUI()

if __name__ == '__main__':
    main()
