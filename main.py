#!python
# coding=utf-8
"""
    AesmaDiv 2021
    Программа для стенда испытания ЭЦН
"""
import os
import sys
import faulthandler
from PyQt5.QtWidgets import QApplication
from Classes.UI.mainwindow import MainWindow
# from AesmaLib.Hardware.Adam5k import Adam5K


# Добавляю текущую папку к путям, где питон ищет модули
sys.path.append('.')
# импортирую класс журнала (from AesmaLib.journal import Journal)
Journal = __import__('AesmaLib.journal', fromlist=['Journal']).Journal


ROOT = os.path.dirname(__file__)
PATHS = {
    'DB': os.path.join(ROOT, 'Files/pump.sqlite'),  # путь к файлу базы данных
    'WND': os.path.join(ROOT, 'Files/mainwindow.ui'),  # путь к файлу GUI
    'TEMPLATE': os.path.join(ROOT, 'Files/report')  # путь к шаблону протокола
}

if __name__ == '__main__':
    Journal.log(__name__, '::\t', "*** Запуск приложения ***")
    faulthandler.enable() # вкл. обработчика ошибок
    app = QApplication(sys.argv)
    app.setStyle("Breeze")

    MainWindow(PATHS).show()

    app.exec_()
    faulthandler.disable() # выкл. обработчика ошибок
    Journal.log(__name__, '::\t', "*** Завершение приложения ***")
