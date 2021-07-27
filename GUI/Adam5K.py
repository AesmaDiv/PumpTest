import os
from PyQt5.QtWidgets import QWidget, QFrame
from PyQt5 import uic
from AesmaLib.journal import Journal


class Adam5K(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            Journal.log("Advantech::", "\tLoading UI form")
            path = os.path.dirname(__file__)
            path += "/adam5k.ui"
            uic.loadUi(path, self)
        except IOError as error:
            Journal.log("Advantech::", "\terror:", str(error))

    @staticmethod
    def prepare():
        Journal.log("Advantech::", "\tPreparing UI form")
        try:
            pass
        except BaseException as error:
            Journal.log("Advantech::", "\terror:", str(error))

    def show(self):
        Journal.log("Advantech::", "\tShowing UI form")
        super().show()
        self.move(1, 1)
        pass
