from PyQt5 import QtWidgets as Qw


class LogsTab(Qw.QWidget):
    OPTIONS = {
        'name': 'Logs',
        'debug': True
    }

    def __init__(self, parent, **params):
        super().__init__()

        self.parent = parent

        self.config = params.get('config')
        self.handler = params.get('gui_handler')

        self.layout = Qw.QVBoxLayout()

        self.log_widget = Qw.QPlainTextEdit(self)
        self.log_widget.setReadOnly(True)
        self.handler.widget = self.log_widget

        self.layout.addWidget(self.log_widget)
        self.setLayout(self.layout)

