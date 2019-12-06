import sys
from pathlib import Path

import util

script_dir = Path(sys.argv[0]).parent
data_dir = script_dir / 'data'

download_base_url = 'https://api.github.com/repos/{username}/{repo}/contents/data/{file}?ref={branch}'

file_operations = {
    'friend_codes.json': 'create',
    'preferences.json': 'download',
    'version_info.json': 'download',
    'statuses.json': 'download'
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
    (script_dir / 'logs').mkdir(exist_ok=True)
    (script_dir / 'logs' / 'errors').mkdir(exist_ok=True)

    temp_config = util.Config(friend_codes=data_dir / 'friend_codes.json',
                              preferences=data_dir / 'preferences.json',
                              version_info=data_dir / 'version_info.json',
                              statuses=data_dir / 'statuses.json')

    for file, operation in file_operations.items():
        path = data_dir / file
        if path.exists():
            continue

        modified = True
        if operation == 'create':
            create_json(path)
        elif operation == 'download':
            # defaults
            username = 'DismissedGuy'
            repo = 'wiimmfi-rpc'
            branch = 'gui-rewrite'

            if temp_config.version_info.complete:
                username = temp_config.version_info['git']['username']
                repo = temp_config.version_info['git']['repo']
                branch = temp_config.version_info['git']['branch']

            url = download_base_url.format(username=username, repo=repo, branch=branch, file=file)

            download_thread = util.GithubDownloadThread('GET', url)
            thread_manager.add_thread(download_thread)

    return modified
