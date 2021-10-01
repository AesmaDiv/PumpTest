#!python
# coding=utf-8
"""
    AesmaDiv 2021
    Программа для стенда испытания ЭЦН
"""
import faulthandler, sys, os
from PyQt5.QtWidgets import QApplication
from Classes.mainwindow import MainWindow


# Добавляю текущую папку к путям, где питон ищет модули
sys.path.append('.')
# импортирую класс журнала (from AesmaLib.journal import Journal)
Journal = __import__('AesmaLib.journal', fromlist=['Journal']).Journal


ROOT = os.path.dirname(__file__)
PATHES = {
    'DB': os.path.join(ROOT, 'Files/pump.sqlite'),  # путь к файлу базы данных
    'WND': os.path.join(ROOT, 'Files/mainwindow.ui'),  # путь к файлу базы данных
    'TEMPLATE': os.path.join(ROOT, 'Files/Report')  # путь к шаблону протокола
}

if __name__ == '__main__':
    Journal.log(__name__, '::\t', "*** Запуск приложения ***")
    faulthandler.enable() # вкл. обработчика ошибок
    app = QApplication(sys.argv)

    window = MainWindow(PATHES)
    window.prepare()
    window.show()

    app.exec_()
    faulthandler.disable() # выкл. обработчика ошибок
    Journal.log(__name__, '::\t', "*** Завершение приложения ***")
