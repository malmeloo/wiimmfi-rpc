import json
import os
import platform
import sys
import zipfile
from pathlib import Path

print(r"""
__        ___ _                      __ _       ____  ____   ____   ____        _ _     _           
\ \      / (_|_)_ __ ___  _ __ ___  / _(_)     |  _ \|  _ \ / ___| | __ ) _   _(_) | __| | ___ _ __ 
 \ \ /\ / /| | | '_ ` _ \| '_ ` _ \| |_| |_____| |_) | |_) | |     |  _ \| | | | | |/ _` |/ _ \ '__|
  \ V  V / | | | | | | | | | | | | |  _| |_____|  _ <|  __/| |___  | |_) | |_| | | | (_| |  __/ |   
   \_/\_/  |_|_|_| |_| |_|_| |_| |_|_| |_|     |_| \_\_|    \____| |____/ \__,_|_|_|\__,_|\___|_|   

""")

if 'PYTHON' not in os.environ:
    os.environ['PYTHON'] = 'python'

script_dir = Path(sys.argv[0]).parent
plat = platform.system()
if plat not in ('Linux', 'Darwin', 'Windows'):
    print(f'[!!] Platform {plat} not supported.')
    sys.exit()
arch = platform.architecture()[0]

# find target version
try:
    with (script_dir / 'data' / 'version_info.json').open('r') as file:
        data = json.load(file)
        version = data.get('version')
        if not version:
            print('[!!] No version found in data files!')
            sys.exit()
        print(f'[!] Detected Version: {version}')
        print(f'[!] Building On {plat}')
except FileNotFoundError:
    print('[!!] No version found in data files!')
    sys.exit()

if __name__ == '__main__':
    if len(sys.argv) == 1 or 'build' not in sys.argv[1]:
        print()
        print('WARNING: This script will build a bundled PyInstaller file.\n'
              'If you just want to use the program, this isn\'t the right script for you.\n'
              'Buttt... if you\'re convinced it is, use "build" as first argument.')
        sys.exit()

    print('[!] Installing Packages')
    if plat in ('Windows', 'Darwin'):
        command = os.environ['PYTHON']
        os.system(f'{command} -m pip install -q -U -r requirements.txt')
        os.system(f'{command} -m pip install -q -U pyinstaller')
    elif plat == 'Linux':
        os.system(f'pip install -U -r requirements.txt')
        os.system(f'pip install -U pyinstaller')
    print()

    print('[!] Building Script')
    if plat in ('Windows', 'Linux'):
        command = os.environ['PYTHON'] + ' -m PyInstaller'
    else:
        command = 'pyinstaller'
    os.system(
        f'{command} -y -w --onefile -n "Wiimmfi-RPC v{version}" --log-level WARN ' \
        f'--additional-hooks-dir=buildhooks/ --hidden-import=PyQt5.sip rpcgui.py')
    print()

    print('[!] Packing Files')
    exec_path = list((script_dir / 'dist').iterdir())[0]
    to_pack = list((script_dir / 'data').iterdir()) + list((script_dir / 'icons').iterdir())
    with zipfile.ZipFile((script_dir / f'{plat}-{arch}.zip'), 'x') as archive:
        archive.write(exec_path, arcname=exec_path.name)
        for file in to_pack:
            archive.write(file)
    print()

    if sys.argv[1] == 'build_appveyor':
        os.system(f'appveyor PushArtifact {plat}-{arch}.zip')
    print(f'[!] Finished Building. Output can be found in {plat}-{arch}.zip')
