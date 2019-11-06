import json


class JSONConfig:
    def __init__(self, path):
        self.path = path

        with open(path, 'r') as file:
            self._config = json.load(file)

    def __str__(self):
        return json.dumps(self._config)

    def set(self, key, value):
        self._config[key] = value

    def get(self, key):
        return self._config[key]


class Config:
    def __init__(self, **files):
        self.friend_codes = JSONConfig(files.get('friend_codes'))
        self.preferences = JSONConfig(files.get('preferences'))
        self.version_info = JSONConfig(files.get('version_info'))
