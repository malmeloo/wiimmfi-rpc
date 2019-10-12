import yaml


class Config:
    def __init__(self, fn):
        self.fn = fn

        with open(fn, 'r') as file:
            self._config = yaml.safe_load(file)

    def __getattr__(self, name):
        """Allows accessing dict items by dot notation. Note: feature only supported for getattr"""
        value = self._config.get(name)
        if not name:
            raise AttributeError
        return value

    def __setitem__(self, key, value):
        """Makes sure the config file gets updated with the new value."""
        self._config[key] = value

        with open(self.fn, 'w') as file:
            yaml.safe_dump(self._config, file)

    def __delitem__(self, key):
        """Makes sure the config file gets updated with the deleted value."""
        del self._config[key]

        with open(self.fn, 'w') as file:
            yaml.safe_dump(self._config, file)
