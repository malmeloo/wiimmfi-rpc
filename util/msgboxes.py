from PyQt5 import QtWidgets as Qw


class MsgBoxes:
    @staticmethod
    def error(msg, thread_name, path):
        fmt_msg = f'A fatal error has occurred in thread "{thread_name}" which caused it to terminate. ' \
                  f'Logs have been created at {path}.\n\n' + msg

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
