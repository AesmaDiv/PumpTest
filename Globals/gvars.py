"""
    Глобальные переменные
"""
import os
import __main__
from GUI.mainwindow import Window as MainWindow
from GUI.PumpWindow import Window as PumpWindow
from GUI.pump_graph import PumpGraph
from GUI.Markers import Markers
from AesmaLib.database import SqliteDB
from Classes.pump_classes import RecordType, RecordTest, RecordPump
from Classes.report import Report



wnd_main: MainWindow    # основное окно программы
wnd_pump: PumpWindow    # окно описания типа насоса

ROOT = os.path.dirname(__main__.__file__)
PATH_TO_DB = os.path.join(ROOT, 'Files/pump.sqlite')  # путь к файлу базы данных
PATH_TO_TEMPLATE = os.path.join(ROOT, 'Files/Report/template.html')
PATH_TO_REPORTS = os.path.join(ROOT, '.')
TESTLIST_QUERY: str =\
    """Select Tests.ID, Tests.DateTime, Tests.OrderNum, Pumps.Serial From Tests
    Inner Join Pumps on Pumps.ID = Tests.Pump
    Order by Tests.ID Desc
    Limit 100"""                     # sql запрос для списка тестов
TEST_EXISTS_CHOICE = ("Внимание", "Запись с таким наряд-заказом"
                                  "уже присутствует в базе данных.\n"
                                  "Хотите выбрать её или создать новую?")
TEST_EXISTS_BUTTONS = ("Выбрать", "Создать", "Отмена")

db = SqliteDB(PATH_TO_DB)            # база данных
rec_test = RecordTest(db)            # данные по типу насоса
rec_pump = RecordPump(db)            # данные по текущему насосу
rec_type = RecordType(db)            # данные по испытанию
rec_deltas = {}                      # отклонения итоговых значений от эталона
pump_graph: PumpGraph = None         # график испытания
markers: Markers = None              # маркеры на графике (расход, мощность, кпд)
active_flwmeter: str = 'flw2'        # текущий расходомер
report = Report(PATH_TO_TEMPLATE, PATH_TO_REPORTS)
