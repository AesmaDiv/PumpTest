"""
    Модуль основного окна программы
"""
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from Functions import funcsCommon, funcs_db, funcsWindow, funcsTest
from AppClasses import Infos
from AesmaLib.journal import Journal
from Globals import gvars


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
        funcsWindow.init_test_list()
        funcsWindow.fill_test_list()
        funcsWindow.init_points_list()
        funcsWindow.fill_spinners()
        funcsWindow.init_graph()
        funcsWindow.set_color_scheme()
        funcsWindow.register_events()

    def show(self):
        """ Отображение окна """
        Journal.log("MainWindow::", "\tShowing UI form")
        super().show()
        self.move(1, 1)
        funcsCommon.Filters.switch_others()
        Infos.Test.set_readonly(self.groupTestInfo, True)
        Infos.Pump.set_readonly(self.groupPumpInfo, True)
        funcsTest.switch_test_running_state()

# FUNCTIONAL
    @staticmethod
    def __display_record():
        """ Отображение записи """
        if Infos.Pump.load() and Infos.Test.load():
            Journal.log("MainWindow::", "\tshowing record")
            Infos.Test.display()
            Infos.Pump.display()
            Infos.Type.display()

    def __clear_record(self):
        """ Очистка информации о записи """
        Journal.log("MainWindow::", "\tclearing record")
        Infos.Test.clear(self.groupTestInfo)
        Infos.Pump.clear(self.groupPumpInfo)
        Infos.Type.clear(None)

    def __store_record(self):
        """ Сохранение записи """
        Journal.log("MainWindow::", "\tsaving record")
        # self.__store_type_info()
        # self.__store_pump_info()
        if Infos.Test.save_to_gvars_info():
            if funcs_db.update_record('Tests', gvars.dictTest):
                Journal.log("MainWindow::", "\trecord updated success")
                self.__fill_testlist()
            else:
                Journal.log("MainWindow::", "\terror updating record")
