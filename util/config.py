import yaml


class Config(dict):
    def __init__(self, fn):
        with open(fn, 'r') as file:
            self._config = yaml.safe_load(file)

        super().__init__(**self._config)

    def __getattr__(self, name):
        value = self._config.get(name)
        if not name:
            raise AttributeError
        return value
