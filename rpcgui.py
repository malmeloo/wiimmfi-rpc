import logging
import sys
import time
from pathlib import Path
import traceback

from PyQt5 import QtWidgets as Qw

import tabs
import util

# TODO: use advanced configuration file
W_WIDTH = 400
W_HEIGHT = 400

# set up logging and add our custom GUI handler
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
formatter = logging.Formatter('[%(asctime)s] %(threadName)s %(levelname)s: %(message)s',
                              '%H:%M:%S')

gui_handler = util.GUILoggerHandler()
gui_handler.setLevel(logging.INFO)
gui_handler.setFormatter(formatter)

file_handler = util.FileLoggerHandler()
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(gui_handler)
logger.addHandler(file_handler)

script_dir = Path(sys.argv[0]).parent
data_dir = script_dir / 'data'
# in case we crash prematurely, let's construct the bare minimum dir structure
(script_dir / 'logs' / 'errors').mkdir(parents=True, exist_ok=True)


def on_error(exc_type, exc_value, exc_traceback):
    tb = traceback.format_tb(exc_traceback)

    log_path = file_handler.create_error_log(tb) or None
    util.MsgBoxes.error('\n'.join(tb), path=log_path)

    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = on_error


class TableWidget(Qw.QWidget):
    TABS = (
        tabs.OverviewTab,
        tabs.FriendcodesTab,
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

            if debug and not self.config.preferences['debug']:
                # debug mode must be enabled for debug tabs
                continue

            params = {
                'config': self.config,
                'width': W_WIDTH,
                'height': W_HEIGHT,
                'gui_handler': gui_handler
            }

            # initialize widget and add it to our tabs
            tab_obj = tab(**params)
            tab_widget.addTab(tab_obj, name)


class Application(Qw.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setGeometry(0, 0, W_HEIGHT, W_WIDTH)

        # Set up the status bar + its widgets
        self.status_bar = Qw.QStatusBar()
        self.setStatusBar(self.status_bar)

        self.thread_counter = Qw.QLabel()
        self.thread_counter.setText('0/0 [p:0]')
        self.progress_bar = Qw.QProgressBar()
        self.progress_bar.setMaximum(100)
        self.thread_status = Qw.QLabel()
        self.thread_status.setText('No operations.')

        self.status_bar.addWidget(self.thread_counter)
        self.status_bar.addWidget(self.progress_bar)
        self.status_bar.addWidget(self.thread_status)

        self.thread_manager = util.ThreadManager(thread_counter=self.thread_counter,
                                                 progress_bar=self.progress_bar,
                                                 thread_status=self.thread_status)
        self.do_reload = util.full_check(self.thread_manager)
        if self.do_reload:
            while self.thread_manager.thread_queue:
                # Ugly, but we need to block until all threads have finished here.
                # Thread.wait() returns too early so we wait for all threads to
                # get kicked out of the queue.
                app.processEvents()
                time.sleep(0.1)
            logging.info('Successfully restored config files')

        self.config = self.load_config()
        logging.info('Loaded config files')
        version = self.config.version_info['version']

        self.wiimmfi_thread = util.WiimmfiCheckThread(self.config)
        self.thread_manager.add_thread(self.wiimmfi_thread)

        # Init the title and tabs.
        self.setWindowTitle(f'Wiimmfi-RPC v{version}')
        self.table_widget = TableWidget(self)
        self.setCentralWidget(self.table_widget)

        logging.info('---- Finished booting ----')

        self.show()

    def crash(self):
        file_handler.create_crash_log()

    def load_config(self):
        config = util.Config(friend_codes=data_dir / 'friend_codes.json',
                             preferences=data_dir / 'preferences.json',
                             version_info=data_dir / 'version_info.json')

        logging.info('Debug mode: '
                     + 'ON' if config.preferences['debug'] else 'OFF')

        return config


if __name__ == '__main__':
    logging.info('Starting...')

    app = Qw.QApplication(sys.argv)
    ex = Application()
    sys.exit(app.exec_())
