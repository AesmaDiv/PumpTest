#!python
# coding=utf-8
"""
    AesmaDiv 2021
    Программа для стенда испытания ЭЦН
"""
import faulthandler
import sys
from PyQt5.QtWidgets import QApplication
from Globals import gvars


# Добавляю текущую папку к путям, где питон ищет модули
sys.path.append('.')
# импортирую класс журнала (from AesmaLib.journal import Journal)
Journal = __import__('AesmaLib.journal', fromlist=['Journal']).Journal

if __name__ == '__main__':
    Journal.log(__name__, '::\t', "*** Запуск приложения ***")
    faulthandler.enable() # вкл. обработчика ошибок
    app = QApplication(sys.argv)

    gvars.wnd_main = gvars.MainWindow()
    gvars.wnd_main.prepare()
    gvars.wnd_main.show()

    app.exec_()
    faulthandler.disable() # выкл. обработчика ошибок
    Journal.log(__name__, '::\t', "*** Завершение приложения ***")
