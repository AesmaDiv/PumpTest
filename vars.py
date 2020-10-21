import AppClasses.UI.MainWindow
import AppClasses.UI.PumpWindow
from AesmaLib.Database import SqliteDB
from AppClasses.UI.PumpGraph import PumpGraph
from AppClasses.UI.Markers import Markers


wnd_main: AppClasses.UI.MainWindow
wnd_pump: AppClasses.UI.PumpWindow

active_flowmeter = 'flow2'

path_to_db = './pump.sqlite'
path_to_pix = './pix.png'
db = SqliteDB()
testlist_query = 'Select Tests.ID, Tests.DateTime, Tests.OrderNum, Pumps.Serial From Tests ' \
                 'Inner Join Pumps on Pumps.ID = Tests.Pump Order by Tests.ID Desc Limit 100'
dictType = {}
dictPump = {}
dictTest = {}
graph_info: PumpGraph = None
markers: Markers = None
testt: int = 3

