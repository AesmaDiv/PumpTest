#!python
# coding=utf-8
"""
    AesmaDiv 2021
    Программа для стенда испытания ЭЦН
"""
from os import path
import sys
import faulthandler
from pathlib import Path
from loguru import logger

from PyQt5.QtWidgets import QApplication

from Classes.Graph.graph_manager import GraphManager
from Classes.UI.wnd_main import MainWindow
from Classes.UI.wnd_type import TypeWindow
from Classes.Data.db_manager import DataManager
from Classes.Data.record import TestData
from Classes.Data.report import Report
from Classes.Adam import adam_config as config
from Classes.Adam.adam_manager import AdamManager

# пути к файлам используемым приложением
ROOT = Path(path.dirname(__file__)).parent.absolute()
PATHS = {
    'DB': path.join(path.join(ROOT, 'assets'), 'pump.sqlite'),  # путь к файлу базы данных
    'WND': path.join(path.join(ROOT, 'assets'), 'mainwindow.ui'),  # путь к файлу GUI
    'TYPE': path.join(path.join(ROOT, 'assets'), 'pumpwindow.ui'),  # путь к файлу GUI
    'TEMPLATE': path.join(path.join(ROOT, 'assets'), 'report')  # путь к шаблону протокола
}

# для отключения логирования разкомментировать эту строку
# для включения - закомментировать
# logger.remove()


class App(QApplication):
    """Класс основного приложения"""
    def __init__(self, argv) -> None:
        super().__init__(argv)
        self._wnd_main = MainWindow(PATHS['WND'])
        self._dbm = DataManager(PATHS['DB'])
        self._wnd_type = TypeWindow(self._wnd_main, PATHS['TYPE'])
        self._tdt = TestData()
        self._gfm = GraphManager(self._tdt)
        self._report = Report(PATHS['TEMPLATE'], self._gfm, self._dbm)
        self._adam = AdamManager(config.IP, config.PORT, config.ADDRESS)

    def run(self):
        """запуск приложения"""
        self.setStyle('Fusion')
        self._wnd_main.setTestData(self._tdt)
        self._wnd_main.setDataManager(self._dbm)
        self._wnd_type.setDataManager(self._dbm)
        self._wnd_main.setGraphManager(self._gfm)
        self._wnd_main.setAdamManager(self._adam)
        self._wnd_main.onTypeChangeRequest.connect(self._onTypeChangeRequest)
        if self._wnd_main.show():
            self.exec_()

    def _onTypeChangeRequest(self, data: dict):
        self._wnd_type.showDialog(data)
        print(data)


if __name__ == '__main__':
    logger.info("\t*** Запуск приложения ***")
    faulthandler.enable() # вкл. обработчика ошибок
    App(sys.argv).run()
    faulthandler.disable() # выкл. обработчика ошибок
    logger.info("\t*** Завершение приложения ***")
