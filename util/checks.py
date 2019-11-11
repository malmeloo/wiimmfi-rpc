import sys
from pathlib import Path

import util

script_dir = Path(sys.argv[0]).parent
data_dir = script_dir / 'data'
# TODO: Use the new config files and construct a URL using the git params
download_base_url = 'https://api.github.com/repos/DismissedGuy/wiimmfi-rpc/contents/data/'

file_operations = {
    'friend_codes.json': 'create',
    'preferences.json': 'download',
    'version_info.json': 'download'
}


def create_json(path):
    """
    Creates a new, empty JSON file.
    :param path: Path
    :return: None
    """
    with open(path, 'w+') as f:
        f.write('[]')


def write_file(path, content):
    with open(path, 'w+') as f:
        f.write(content)


def full_check(thread_manager):
    """
    Checks for missing or corrupt files and directories, and restores them where necessary.
    :return: bool - Whether any changes have been made
    """
    modified = False

    # create directories if they don't exist yet
    data_dir.mkdir(exist_ok=True)
    (data_dir / 'cache').mkdir(exist_ok=True)

    for file, operation in file_operations.items():
        path = data_dir / file
        if path.exists():
            continue

        modified = True
        if operation == 'create':
            create_json(path)
        elif operation == 'download':
            url = download_base_url + file

            download_thread = util.GithubDownloadThread('GET', url + '?ref=gui-rewrite')
            thread_manager.add_thread(download_thread)

    return modified
