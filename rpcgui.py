import logging
import sys
import time
from pathlib import Path

from PyQt5 import QtGui as Qg
from PyQt5 import QtWidgets as Qw

import tabs
import util

# set up logging and add our custom GUI handler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
formatter = logging.Formatter('[%(asctime)s] %(threadName)s %(levelname)s: %(message)s',
                              '%H:%M:%S')
logging.getLogger('requests').setLevel(logging.WARNING)

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
    tb = exc_traceback.format()

    log_path = file_handler.create_error_log(tb)
    util.MsgBoxes.error('\n'.join(tb), path=log_path)

    sys.__excepthook__(exc_type, exc_value, exc_traceback)


sys.excepthook = on_error


class SystemTrayIcon(Qw.QSystemTrayIcon):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.update()

        self.quit_button = None
        self.toggle_button = None
        self.open_button = None

        self.activated.connect(self._open_window)

        self.menu = Qw.QMenu(parent)
        self.populate_menu(self.menu)

        self.setContextMenu(self.menu)

    def _toggle_enabled(self):
        curr_enabled = self.parent.wiimmfi_thread.run
        if curr_enabled:
            self.parent.wiimmfi_thread.run = False
            self.toggle_button.setText('Enable game detection')
        else:
            self.parent.wiimmfi_thread.run = True
            self.toggle_button.setText('Disable game detection')

        self.update()

    def _open_window(self, reason=None):
        if reason and reason == Qw.QSystemTrayIcon.Context:  # right-click
            return

        self.parent.setHidden(False)
        self.parent.activateWindow()

    def _quit(self):
        self.parent.do_close = True
        self.parent.close()

    def populate_menu(self, menu):
        version = self.parent.config.version_info['version']
        header = menu.addAction(f'Wiimmfi-RPC v{version}')
        header.setDisabled(True)

        menu.addSeparator()

        self.open_button = menu.addAction('Open Wiimmfi-RPC')
        self.open_button.triggered.connect(self._open_window)

        toggle_text = 'Disable' if self.parent.wiimmfi_thread.run else 'Enable'
        self.toggle_button = menu.addAction(toggle_text + ' game detection')
        self.toggle_button.triggered.connect(self._toggle_enabled)

        menu.addSeparator()

        self.quit_button = menu.addAction('Quit Wiimmfi-RPC')
        self.quit_button.triggered.connect(self._quit)

    def update(self):
        online_player = self.parent.wiimmfi_thread.last_player

        if not self.parent.wiimmfi_thread.run:
            icon_path = script_dir / 'icons' / 'disabled.png'
            self.setToolTip('Game detection has been disabled.')
        elif online_player:
            icon_path = script_dir / 'icons' / 'active.png'
            self.setToolTip(f'Playing {online_player.game_name}.')
        else:
            icon_path = script_dir / 'icons' / 'inactive.png'
            self.setToolTip('Not playing any games.')

        icon = Qg.QIcon(str(icon_path))
        self.setIcon(icon)


class TableWidget(Qw.QWidget):
    TABS = (
        tabs.OverviewTab,
        tabs.FriendcodesTab,
        tabs.OnlinePlayerTab,
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
        self.tabs.resize(400, 400)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        logging.info('Initialized window tabs')

    def add_tabs(self):
        for tab in self.TABS:
            name = tab.OPTIONS.pop('name')
            debug = tab.OPTIONS.pop('debug')

            if debug and not self.config.preferences['debug']:
                # debug mode must be enabled for debug tabs
                continue

            params = {
                'config': self.config,
                'gui_handler': gui_handler
            }

            # initialize widget and add it to our tabs
            tab_obj = tab(self.parent, **params)
            self.tabs.addTab(tab_obj, name)


class Application(Qw.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.do_close = False

        self.setGeometry(0, 0, 400, 400)

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

        self.thread_manager = util.ThreadManager(file_handler=file_handler,
                                                 thread_counter=self.thread_counter,
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

        self.wiimmfi_thread = util.WiimmfiCheckThread(self.config, self._status_updated)
        self.thread_manager.add_thread(self.wiimmfi_thread)

        self.game_list_thread = util.WiimmfiGameListThread()
        self.thread_manager.add_thread(self.game_list_thread)

        self.updater = util.Updater(self.thread_manager, self.config)
        self.updater.check_updates()

        # Init the title and tabs.
        self.setWindowTitle(f'Wiimmfi-RPC v{version}')
        self.table_widget = TableWidget(self)
        self.table_widget.add_tabs()
        self.setCentralWidget(self.table_widget)

        logging.info('---- Finished booting ----')

        # We do this at the end to make sure it has
        # access to all the resources it needs.
        self.sys_tray = SystemTrayIcon(self)
        self.sys_tray.show()

        self.show()

    def _status_updated(self):
        self.sys_tray.update()

    def closeEvent(self, event: Qg.QCloseEvent):
        self.setHidden(True)

        if not self.config.preferences['config']['tray']['minimize_on_exit']:
            event.accept()
            return

        if self.do_close:
            event.accept()
        else:
            event.ignore()
            if self.config.preferences['config']['tray']['show_notice']:
                self.config.preferences['config']['tray']['show_notice'] = False

                self.sys_tray.showMessage('Wiimmfi-RPC',
                                          'Wiimmfi-RPC has been minimized to tray and will '
                                          'keep running in the background. To quit the program, '
                                          'right-click on this icon and select "Quit".')

    def load_config(self):
        config = util.Config(friend_codes=data_dir / 'friend_codes.json',
                             preferences=data_dir / 'preferences.json',
                             version_info=data_dir / 'version_info.json',
                             statuses=data_dir / 'statuses.json')

        logging.info('Debug mode: '
                     + ('ON' if config.preferences['debug'] else 'OFF'))

        return config


if __name__ == '__main__':
    logging.info('Starting...')

    app = Qw.QApplication(sys.argv)
    ex = Application()
    sys.exit(app.exec_())
