"""
    Модуль содержит класс основного окна программы
"""
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from Functions import funcs_wnd, funcs_test
from AesmaLib.journal import Journal


class Window(QMainWindow):
    """ Класс основного окна программы """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_displaying = dict.fromkeys(['Producer','Type','Serial'], False)
        self.init()

    def __del__(self):
        pass

    @Journal.logged
    def init(self):
        """ инициализирует и загружает интерфейс главного окна """
        try:
            path = os.path.dirname(__file__)
            path += "/UI/mainwindow.ui"
            uic.loadUi(path, self)
        except IOError as error:
            Journal.log(__name__, "::\t", "ошибка:", str(error))

    @staticmethod
    @Journal.logged
    def prepare():
        """ инициализирует и подготавливает компоненты главного окна """
        funcs_wnd.set_color_scheme()
        funcs_wnd.init_test_list()
        funcs_wnd.init_points_table()
        funcs_wnd.init_graph()
        funcs_wnd.fill_combos()
        funcs_wnd.fill_test_list()
        funcs_wnd.register_events()

    @Journal.logged
    def show(self):
        """ отображает главное окно """
        super().show()
        self.move(1, 1)
        funcs_wnd.testlist_filter_switch()
        funcs_wnd.group_lock(self.groupTestInfo, True)
        funcs_wnd.group_lock(self.groupPumpInfo, True)
        funcs_test.switch_test_running_state()
