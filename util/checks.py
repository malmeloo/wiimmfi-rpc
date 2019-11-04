from pathlib import Path

script_dir = Path(__path__).parent
data_dir = script_dir / 'data'

file_operations = {
    'friend_codes.json': 'create',
    'preferences.json': 'download',
    'versioninfo.json': 'download'
}


def create_json(path):
    """
    Creates a new, empty JSON file.
    :param path: filename
    :return: None
    """
    with open(path, 'w+') as f:
        f.write('{}')


def full_check():
    """
    Checks for missing or corrupt files and directories, and restores them where necessary.
    :return: bool
    """

    # create directories if they don't exist yet
    data_dir.mkdir()
    (data_dir / 'cache').mkdir()

    for file, operation in file_operations.items():
        if operation == 'create':
            create_json(data_dir / file)
        elif operation == 'download':
            # TODO: download missing files.
            pass
