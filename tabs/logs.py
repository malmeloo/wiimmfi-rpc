from PyQt5 import QtWidgets as Qw


class LogsTab(Qw.QWidget):
    OPTIONS = {
        'name': 'Logs',
        'debug': True
    }

    def __init__(self, **params):
        super().__init__()

        self.config = params.get('config')
        self.width = params.get('width')
        self.height = params.get('height')
        self.handler = params.get('log_handler')

        self.layout = Qw.QVBoxLayout()

        self.log_widget = Qw.QPlainTextEdit(self)
        self.log_widget.setReadOnly(True)
        self.log_widget.resize(self.width, self.height)
        self.handler.widget = self.log_widget

        self.layout.addWidget(self.log_widget)
        self.setLayout(self.layout)

