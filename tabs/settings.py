from PyQt5 import QtWidgets as Qw


class SettingsTab(Qw.QWidget):
    OPTIONS = {
        'name': 'Settings',
        'debug': False
    }

    def __init__(self, **params):
        super().__init__()

        self.config = params.get('config')
        self.width = params.get('width')
        self.height = params.get('height')

        self.create_update_groupbox()
        self.create_danger_groupbox()

        self.layout = Qw.QVBoxLayout()
        self.layout.addWidget(self.update_group)
        self.layout.addWidget(self.danger_group)

        self.setLayout(self.layout)

    def create_update_groupbox(self):
        self.update_group = Qw.QGroupBox('Update Settings')

        auto_download_label = Qw.QLabel('Enable auto download:')
        self.auto_download = Qw.QCheckBox()
        auto_install_label = Qw.QLabel('Enable auto install:')
        self.auto_install = Qw.QCheckBox()
        release_type_label = Qw.QLabel('Update to:')
        self.release_type = Qw.QComboBox()
        self.release_type.addItems(['Latest release', 'Beta', 'Alpha'])

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
        self.clear_config = Qw.QPushButton('Clear config files')
        self.clear_codes = Qw.QPushButton('Clear friend codes')

        layout = Qw.QFormLayout()
        layout.addRow(debug_label, self.debug)
        layout.addRow(self.clear_config)
        layout.addRow(self.clear_codes)
        self.danger_group.setLayout(layout)
