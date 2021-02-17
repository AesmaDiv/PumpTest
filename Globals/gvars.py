import GUI.MainWindow
import GUI.PumpWindow
from AesmaLib.database import SqliteDB
from GUI.PumpGraph import PumpGraph
from GUI.Markers import Markers


wnd_main: GUI.MainWindow
wnd_pump: GUI.PumpWindow

active_flowmeter = 'flow2'

db = SqliteDB('./Files/pump.sqlite')
# testlist_query = '''Select Tests.ID, Tests.DateTime, Tests.OrderNum, Pumps.Serial From Tests
#                     Inner Join Pumps on Pumps.ID = Tests.Pump
#                     Order by Tests.ID Desc
#                     Limit 100'''
testlist_query = {
    'table': 'Tests',
    'columns': ['Tests.ID', 'Tests.DateTime', 'Tests.OrderNum', 'Pumps.Serial'],
    'inner': {'Inner Join Pumps on Pumps.ID': 'Tests.Pump'},
    'order': 'Tests.ID Desc Limit 100'
}
dictType = {}
dictPump = {}
dictTest = {}
graph_info: PumpGraph = None
markers: Markers = None
