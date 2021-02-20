import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from Functions import funcsCommon, funcs_db, funcsWindow, funcsTest
from AppClasses import Infos
from AesmaLib.journal import Journal
from Globals import gvars


class Window(QMainWindow):
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
        Journal.log("MainWindow::", "\tPreparing UI form")
        try:
            funcsWindow.init_test_list()
            funcsWindow.fill_test_list()
            funcsWindow.init_points_list()
            funcsWindow.fill_spinners()
            funcsWindow.init_graph()
            funcsWindow.set_color_scheme()
            funcsWindow.register_events()
        except BaseException as error:
            Journal.log("MainWindow::", "\terror:", str(error))

    def show(self):
        Journal.log("MainWindow::", "\tShowing UI form")
        super().show()
        self.move(1, 1)
        funcsCommon.Filters.switch_others()
        Infos.Test.set_readonly(self.groupTestInfo, True)
        Infos.Pump.set_readonly(self.groupPumpInfo, True)
        funcsTest.switch_test_running_state()
        pass

# FUNCTIONAL
    @staticmethod
    def __display_record():
        if Infos.Pump.load() and Infos.Test.load():
            Journal.log("MainWindow::", "\tshowing record")
            Infos.Test.display()
            Infos.Pump.display()
            Infos.Type.display()

    @staticmethod
    def __create_record():
        Journal.log("MainWindow::", "\tclearing record")
        Infos.Test.clear()
        Infos.Pump.clear()
        Infos.Type.clear()

    @staticmethod
    def __store_record(self):
        Journal.log("MainWindow::", "\tsaving record")
        # self.__store_type_info()
        # self.__store_pump_info()
        if Infos.Test.save_to_gvars_info():
            if funcs_db.update_record('Tests', gvars.dictTest):
                Journal.log("MainWindow::", "\trecord updated success")
                self.__fill_testlist()
            else:
                Journal.log("MainWindow::", "\terror updating record")

# READ RECORD
