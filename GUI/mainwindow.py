"""
    Модуль основного окна программы
"""
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from Functions import funcs_wnd, funcsTest
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
            path += "/mainwindow.ui"
            uic.loadUi(path, self)
        except IOError as error:
            Journal.log(__name__, "::\t", "ошибка:", str(error))

    @staticmethod
    @Journal.logged
    def prepare():
        """ инициализирует и подготавливает компоненты главного окна """
        funcs_wnd.set_color_scheme()
        funcs_wnd.init_test_list()
        funcs_wnd.init_points_list()
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
        funcsTest.switch_test_running_state()

    @staticmethod
    @Journal.logged
    def __display_record():
        """ отображение выбранную запись """
        funcs_wnd.display_record()

    @Journal.logged
    def __clear_record(self):
        """ очисткает поля отображения записи """
        funcs_wnd.clear_record(True)

    @Journal.logged
    def __store_record(self):
        """ сохраняет текущую запись """
        # self.__store_type_info()
        # self.__store_pump_info()
        # if Infos.Test.save_to_gvars_info():
        #     if funcs_db.update_record('Tests', gvars.rec_test):
        #         Journal.log(__name__, "::", "\trecord updated success")
        #         self.__fill_testlist()
        #     else:
        #         Journal.log(__name__, "::", "\terror updating record")
