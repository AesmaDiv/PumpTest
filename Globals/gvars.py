"""
    Глобальные переменные
"""
from GUI.mainwindow import Window as mainwindow
from GUI.PumpWindow import Window as pumpwindow
from GUI.PumpGraph import PumpGraph
from GUI.Markers import Markers
from AesmaLib.database import SqliteDB


wnd_main: mainwindow    # основное окно программы
wnd_pump: pumpwindow    # окно описания типа насоса

PATH_TO_DB = './Files/pump.sqlite'  # путь к файлу базы данных
PATH_TO_PIC = './Files/pic.png'     # путь к картинке графика испытания
TESTLIST_QUERY = \
'''Select Tests.ID, Tests.DateTime, Tests.OrderNum, Pumps.Serial From Tests
   Inner Join Pumps on Pumps.ID = Tests.Pump
   Order by Tests.ID Desc
   Limit 100'''                     # sql запрос для списка тестов

db = SqliteDB(PATH_TO_DB)           # база данных
dictType = {}                       # данные по типу насоса
dictPump = {}                       # данные по текущему насосу
dictTest = {}                       # данные по испытанию
graph_info: PumpGraph = None        # график испытания
markers: Markers = None             # маркеры на графике (расход, мощность, кпд)
active_flowmeter: str = 'flow2'     # текущий расходомер
