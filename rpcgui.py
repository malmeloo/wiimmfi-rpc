import logging
import sys

import yaml
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QWidget, QTabWidget, QPlainTextEdit, \
    QVBoxLayout

import util

# TODO: use advanced configuration file
W_WIDTH = 400
W_HEIGHT = 400

logging.basicConfig(filename='test.log',
                    level=logging.INFO)
handler = util.GUILoggerHandler()
formatter = logging.Formatter('[%(asctime)s] %(threadName)s %(levelname)s: %(message)s',
                              '%H:%M:%S')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)


class OverviewTab(QWidget):
    OPTIONS = {
        'name': 'Overview',
        'debug': False
    }

    def __init__(self):
        super().__init__()


class SettingsTab(QWidget):
    OPTIONS = {
        'name': 'Settings',
        'debug': False
    }

    def __init__(self):
        super().__init__()


class LogsTab(QWidget):
    OPTIONS = {
        'name': 'Logs',
        'debug': True
    }

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.log_widget = QPlainTextEdit(self)
        self.log_widget.setReadOnly(True)
        self.log_widget.resize(W_WIDTH, W_HEIGHT)
        handler.widget = self.log_widget

        self.layout.addWidget(self.log_widget)
        self.setLayout(self.layout)


class TableWidget(QWidget):
    TABS = (
        OverviewTab,
        SettingsTab,
        LogsTab
    )

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.config = self.parent.config
        self.layout = QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.add_tabs(self.tabs)
        self.tabs.resize(W_WIDTH, W_HEIGHT)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        logging.info('Initialized window tabs')

    def add_tabs(self, tab_widget):
        for tab in self.TABS:
            name = tab.OPTIONS.pop('name')
            debug = tab.OPTIONS.pop('debug')

            if debug and not self.config.debug:
                # debug mode must be enabled for debug tabs
                continue

            tab_obj = tab()
            tab_widget.addTab(tab_obj, name)


class Application(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = self.load_config('preferences.yml')

        self.setWindowTitle(f'Wiimmfi-RPC v{self.config.version}')
        self.setGeometry(0, 0, W_HEIGHT, W_WIDTH)

        self.table_widget = TableWidget(self)
        self.setCentralWidget(self.table_widget)

        self.show()

    def load_config(self, fn):
        try:
            config = util.Config(fn)
        except FileNotFoundError:
            logging.warning(f'File {fn} doesn\'t exist! Downloading latest from server...')
            # TODO: show dialog with warning + download file
            sys.exit()
        except yaml.YAMLError as err:
            logging.warning(f'Error in config file {fn}: {err}')
            sys.exit()

        logging.info('Debug mode: '
                     + 'ON' if config.debug else 'OFF')

        return config


if __name__ == '__main__':
    logging.info('Starting...')

    app = QApplication(sys.argv)
    ex = Application()
    sys.exit(app.exec_())
