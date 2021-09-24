"""
    Модуль содержит класс основного окна программы
"""
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from AesmaLib.journal import Journal


class Window(QMainWindow):
    """ Класс основного окна программы """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_displaying = dict.fromkeys(['Producer','Type','Serial'], False)
        try:
            path = os.path.dirname(__file__)
            path += "/UI/mainwindow.ui"
            uic.loadUi(path, self)
        except IOError as error:
            Journal.log(__name__, "::\t", "ошибка:", str(error))
