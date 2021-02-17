import os
from PyQt5.QtWidgets import QWidget, QFrame
from PyQt5 import uic
from AesmaLib import journal
import gvars


class Adam5K(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            journal.log("Advantech::", "\tLoading UI form")
            path = os.path.dirname(__file__)
            path += "/adam5k.ui"
            uic.loadUi(path, self)
        except IOError as error:
            journal.log("Advantech::", "\terror:", str(error))

    @staticmethod
    def prepare():
        journal.log("Advantech::", "\tPreparing UI form")
        try:
            pass
        except BaseException as error:
            journal.log("Advantech::", "\terror:", str(error))

    def show(self):
        journal.log("Advantech::", "\tShowing UI form")
        super().show()
        self.move(1, 1)
        pass
