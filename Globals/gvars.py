"""
    Глобальные переменные
"""
from Classes.record import TestInfo
import os
import __main__

from GUI.mainwindow import Window as MainWindow
from GUI.PumpWindow import Window as PumpWindow



wnd_main: MainWindow    # основное окно программы
wnd_pump: PumpWindow    # окно описания типа насоса

ROOT = os.path.dirname(__main__.__file__)
PATH_TO_DB = os.path.join(ROOT, 'Files/pump.sqlite')  # путь к файлу базы данных
PATH_TO_TEMPLATE = os.path.join(ROOT, 'Files/Report')

TEST_EXISTS_CHOICE = ("Внимание", "Запись с таким наряд-заказом"
                                  "уже присутствует в базе данных.\n"
                                  "Хотите выбрать её или создать новую?")
TEST_EXISTS_BUTTONS = ("Выбрать", "Создать", "Отмена")

