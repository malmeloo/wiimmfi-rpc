import json


class JSONConfig:
    def __init__(self, path):
        self.path = path

        with open(path, 'r') as file:
            self._config = json.load(file)

    def flush(self):
        with open(self.path, 'w+') as file:
            json.dump(self._config, file, indent=2)

    def remove(self, item):
        self._config.remove(item)

        self.flush()

    def append(self, item):
        self._config.append(item)

        self.flush()

    def __getitem__(self, item):
        return self._config[item]

    def __setitem__(self, key, value):
        self._config[key] = value

        self.flush()

    def __delitem__(self, key):
        del self._config[key]

        self.flush()

    def __next__(self):
        return next(iter(self._config))

    def __iter__(self):
        return iter(self._config)


class Config:
    def __init__(self, **files):
        self.friend_codes = JSONConfig(files.get('friend_codes'))
        self.preferences = JSONConfig(files.get('preferences'))
        self.version_info = JSONConfig(files.get('version_info'))
