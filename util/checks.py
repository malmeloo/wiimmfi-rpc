import os

# TODO: actually use this and defeat the laziness
script_dir = os.path.dirname(os.path.realpath(__file__))

DIRS = (
    'data'
)


class FileRestoreException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


def restore_dirs():
    for directory in DIRS:
        if not os.path.isdir(directory):
            os.mkdir(directory)


def create_empty_json(fn):
    """
    :param fn: Filename of the file to create.
    :return: None
    """

    with open(fn, 'w+') as f:
        f.write('{}')


def full_check():
    """
    Checks for missing or corrupt files and directories, and restores them where necessary.
    :return: bool
    """
    try:
        restore_dirs()
    except Exception as e:
        # TODO: open up dialog box somehow
        pass
