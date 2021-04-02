"""
    Модуль основного окна программы
"""
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from Functions import funcsCommon, funcs_wnd, funcsTest
from AesmaLib.journal import Journal


class Window(QMainWindow):
    """ Класс основного окна программы """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            Journal.log("MainWindow::", "\tLoading UI form")
            path = os.path.dirname(__file__)
            path += "/mainwindow.ui"
            uic.loadUi(path, self)
        except IOError as error:
            Journal.log("MainWindow::", "\terror:", str(error))

    def __del__(self):
        pass

    @staticmethod
    def prepare():
        """ Инициализация компонентов и подготовка основного окна """
        Journal.log("MainWindow::", "\tPreparing UI form")
        funcs_wnd.init_test_list()
        funcs_wnd.fill_test_list()
        funcs_wnd.init_points_list()
        funcs_wnd.fill_spinners()
        funcs_wnd.init_graph()
        funcs_wnd.set_color_scheme()
        funcs_wnd.register_events()

    def show(self):
        """ Отображение окна """
        Journal.log("MainWindow::", "\tShowing UI form")
        super().show()
        self.move(1, 1)
        funcs_wnd.testlist_filter_switch()
        funcs_wnd.group_lock(self.groupTestInfo, True)
        funcs_wnd.group_lock(self.groupPumpInfo, True)
        funcsTest.switch_test_running_state()

# FUNCTIONAL
    @staticmethod
    def __display_record():
        """ Отображение записи """
        Journal.log("MainWindow::", "\tshowing record")
        funcs_wnd.display_record()

    def __clear_record(self):
        """ Очистка информации о записи """
        Journal.log("MainWindow::", "\tclearing record")
        funcs_wnd.clear_record(True)

    def __store_record(self):
        """ Сохранение записи """
        Journal.log("MainWindow::", "\tsaving record")
        # self.__store_type_info()
        # self.__store_pump_info()
        # if Infos.Test.save_to_gvars_info():
        #     if funcs_db.update_record('Tests', gvars.rec_test):
        #         Journal.log("MainWindow::", "\trecord updated success")
        #         self.__fill_testlist()
        #     else:
        #         Journal.log("MainWindow::", "\terror updating record")
