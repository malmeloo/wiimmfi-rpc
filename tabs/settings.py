from PyQt5 import QtWidgets as Qw


class SettingsTab(Qw.QWidget):
    OPTIONS = {
        'name': 'Settings',
        'debug': False
    }
    RELEASES = {
        'Latest release': 'latest',
        'Beta': 'beta',
        'Alpha': 'alpha'
    }

    def __init__(self, parent, **params):
        super().__init__()

        self.parent = parent

        self.config = params.get('config')

        self.create_update_groupbox()
        self.create_danger_groupbox()

        self.layout = Qw.QVBoxLayout()
        self.layout.addWidget(self.update_group)
        self.layout.addWidget(self.danger_group)

        self.load_settings()

        self.setLayout(self.layout)

    def create_update_groupbox(self):
        self.update_group = Qw.QGroupBox('Update Settings')

        auto_download_label = Qw.QLabel('Enable auto download:')
        self.auto_download = Qw.QCheckBox()
        self.auto_download.clicked.connect(lambda checked: self.modify_config('auto_download', checked))
        auto_install_label = Qw.QLabel('Enable auto install:')
        self.auto_install = Qw.QCheckBox()
        self.auto_install.clicked.connect(lambda checked: self.modify_config('auto_install', checked))
        release_type_label = Qw.QLabel('Update to:')
        self.release_type = Qw.QComboBox()
        self.release_type.addItems(self.RELEASES.keys())
        self.release_type.currentTextChanged.connect(lambda text: self.modify_config('release', text))

        layout = Qw.QFormLayout()
        layout.addRow(auto_download_label, self.auto_download)
        layout.addRow(auto_install_label, self.auto_install)
        layout.addRow(release_type_label, self.release_type)
        self.update_group.setLayout(layout)

    def create_danger_groupbox(self):
        self.danger_group = Qw.QGroupBox('Danger zone')
        self.danger_group.setStyleSheet('QGroupBox {color: red}')

        debug_label = Qw.QLabel('Enable debug mode:')
        self.debug = Qw.QCheckBox()
        self.debug.clicked.connect(lambda checked: self.modify_config('debug', checked))
        self.clear_config = Qw.QPushButton('Clear config files')
        self.clear_codes = Qw.QPushButton('Clear friend codes')

        layout = Qw.QFormLayout()
        layout.addRow(debug_label, self.debug)
        layout.addRow(self.clear_config)
        layout.addRow(self.clear_codes)
        self.danger_group.setLayout(layout)

    def load_settings(self):
        debug = self.config.preferences['debug']
        auto_download = self.config.preferences['config']['updates']['auto_download']
        auto_install = self.config.preferences['config']['updates']['auto_install']
        release_type = self.config.preferences['config']['updates']['release_type']

        self.debug.setChecked(debug)
        self.auto_download.setChecked(auto_download)
        self.auto_install.setChecked(auto_install)

        release_index = list(self.RELEASES.values()).index(release_type)
        self.release_type.setCurrentIndex(release_index)

    def modify_config(self, setting, value):
        preferences = self.config.preferences

        if setting == 'debug':
            preferences['debug'] = value
        elif setting == 'auto_download':
            preferences['config']['updates']['auto_download'] = value
        elif setting == 'auto_install':
            preferences['config']['updates']['auto_install'] = value
        elif setting == 'release':
            preferences['config']['updates']['release_type'] = self.RELEASES.get(value)

        # manual flushing due to get/setitem recursion
        preferences.flush()
