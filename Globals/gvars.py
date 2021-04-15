"""
    Глобальные переменные
"""
from GUI.mainwindow import Window as MainWindow
from GUI.PumpWindow import Window as PumpWindow
from GUI.PumpGraph import PumpGraph
from GUI.Markers import Markers
from AesmaLib.database import SqliteDB
from Classes.pump_classes import RecordType, RecordTest, RecordPump


wnd_main: MainWindow    # основное окно программы
wnd_pump: PumpWindow    # окно описания типа насоса

PATH_TO_DB = './Files/pump.sqlite'  # путь к файлу базы данных
PATH_TO_PIC = './Files/pic.png'     # путь к картинке графика испытания
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
graph_info: PumpGraph = None         # график испытания
markers: Markers = None              # маркеры на графике (расход, мощность, кпд)
active_flowmeter: str = 'flow2'      # текущий расходомер
