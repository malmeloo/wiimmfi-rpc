import threading

from PyQt5 import QtWidgets as Qw


class MsgBoxes:
    @staticmethod
    def error(msg, path=None, thread_name=None):
        if not thread_name:
            thread_name = threading.current_thread().name
        fmt_msg = f'A fatal error has occurred in thread "{thread_name}" which caused it to terminate. '
        if path:
            fmt_msg += f'Logs have been created at {path}.\n\n{msg}'

        box = Qw.QMessageBox()
        box.setIcon(Qw.QMessageBox.Critical)
        box.setInformativeText(fmt_msg)
        box.setWindowTitle('Error')
        box.exec_()

    @staticmethod
    def info(msg):
        box = Qw.QMessageBox()
        box.setIcon(Qw.QMessageBox.Information)
        box.setText(msg)
        box.setWindowTitle('Information')
        box.exec_()

    @staticmethod
    def promptyesno(msg):
        box = Qw.QMessageBox()
        box.setIcon(Qw.QMessageBox.Question)
        box.setText(msg)
        box.setWindowTitle('Question')
        box.setStandardButtons(Qw.QMessageBox.Ok | Qw.QMessageBox.Cancel)

        button = box.exec_()
        if button == Qw.QMessageBox.Ok:
            return True
        return False
