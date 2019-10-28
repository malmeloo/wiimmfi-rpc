import logging
import sys

import yaml
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QWidget, QTabWidget, QPlainTextEdit, \
    QVBoxLayout

import util

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
        'name': 'Overview'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class SettingsTab(QWidget):
    OPTIONS = {
        'name': 'Settings'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LogsTab(QWidget):
    OPTIONS = {
        'name': 'Logs'
    }

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.log_widget = QPlainTextEdit(self)
        self.log_widget.setReadOnly(True)
        self.log_widget.resize(400, 400)
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
        self.layout = QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.add_tabs(self.tabs)
        self.tabs.resize(400, 400)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        logging.info('Initialized window tabs')

    def add_tabs(self, tab_widget):
        for tab in self.TABS:
            name = tab.OPTIONS.pop('name')

            tab_obj = tab()
            tab_widget.addTab(tab_obj, name)


class Application(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.config = util.Config('preferences.yml')
        except FileNotFoundError:
            logging.warning('Preference file doesn\'t exist! Downloading latest from server...')
            # TODO: show dialog with warning + download file
        except yaml.YAMLError as err:
            logging.error(f'Failed to load application preferences: {err}')

        logging.info('Debug mode: '
                     + 'ON' if self.config.debug else 'OFF')

        self.title = f'Wiimmfi-RPC v{self.config.version}'
        self.left = 0
        self.top = 0
        self.width = 400
        self.height = 400
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.table_widget = TableWidget(self)
        self.setCentralWidget(self.table_widget)

        self.show()


if __name__ == '__main__':
    logging.info('Starting...')

    app = QApplication(sys.argv)
    ex = Application()
    logging.fatal('No instructions given.')
    sys.exit(app.exec_())
