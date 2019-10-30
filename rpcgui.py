import logging
import sys

import yaml
from PyQt5 import QtWidgets as Qw

import tabs
import util

# TODO: use advanced configuration file
W_WIDTH = 400
W_HEIGHT = 400

logging.basicConfig(level=logging.INFO)
handler = util.GUILoggerHandler()
formatter = logging.Formatter('[%(asctime)s] %(threadName)s %(levelname)s: %(message)s',
                              '%H:%M:%S')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)


class TableWidget(Qw.QWidget):
    TABS = (
        tabs.OverviewTab,
        tabs.SettingsTab,
        tabs.LogsTab
    )

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.config = self.parent.config
        self.layout = Qw.QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = Qw.QTabWidget()
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

            params = {
                'width': W_WIDTH,
                'height': W_HEIGHT,
                'log_handler': handler
            }

            tab_obj = tab(**params)
            tab_widget.addTab(tab_obj, name)


class Application(Qw.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = self.load_config('preferences.yml')

        self.setWindowTitle(f'Wiimmfi-RPC v{self.config.version}')
        self.setGeometry(0, 0, W_HEIGHT, W_WIDTH)

        # Initialize the main tabs
        self.table_widget = TableWidget(self)
        self.setCentralWidget(self.table_widget)

        # Set up the status bar + its widgets
        # TODO: implement thread manager that informs and manages this bad boy
        self.statusBar = Qw.QStatusBar()
        self.setStatusBar(self.statusBar)

        self.progress_bar = Qw.QProgressBar()
        self.progress_label = Qw.QLabel()
        self.progress_label.setText('0/0')

        self.statusBar.addWidget(self.progress_bar)
        self.statusBar.addWidget(self.progress_label)

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

    app = Qw.QApplication(sys.argv)
    ex = Application()
    sys.exit(app.exec_())
