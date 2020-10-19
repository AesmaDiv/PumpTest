from PyQt5.QtWidgets import QHeaderView, QFrame
from PyQt5 import QtCore

from AesmaLib import Journal
from AppClasses.Pump import Point
from AppClasses.UI import Events, Models, PumpGraph
from AppClasses.Functions import funcsDB, funcsTable, funcsSpinner, funcsAdam
import vars


# INIT WINDOW
from AppClasses.UI.Markers import Markers


def register_events():
    Journal.log("MainWindow::", "\tregistering events")
    vars.wnd_main.tableTests.selectionModel().currentChanged.connect(Events.on_changed_testlist)

    vars.wnd_main.cmbProducers.currentIndexChanged.connect(Events.on_changed_combo_producers)
    vars.wnd_main.cmbTypes.currentIndexChanged.connect(Events.on_changed_combo_types)
    vars.wnd_main.cmbSerials.currentIndexChanged.connect(Events.on_changed_combo_serials)

    vars.wnd_main.btnTest.clicked.connect(Events.on_clicked_test)
    vars.wnd_main.btnTest_New.clicked.connect(Events.on_clicked_test_new)
    vars.wnd_main.btnTest_Save.clicked.connect(Events.on_clicked_test_info_save)
    vars.wnd_main.btnTest_Cancel.clicked.connect(Events.on_clicked_test_info_cancel)

    vars.wnd_main.btnPump_New.clicked.connect(Events.on_clicked_pump_new)
    vars.wnd_main.btnPump_Save.clicked.connect(Events.on_clicked_pump_save)
    vars.wnd_main.btnPump_Cancel.clicked.connect(Events.on_clicked_pump_cancel)

    vars.wnd_main.btnFilterReset.clicked.connect(Events.on_clicked_filter_reset)

    vars.wnd_main.txtFilter_ID.textChanged.connect(Events.on_changed_filter_apply)
    vars.wnd_main.txtFilter_DateTime.textChanged.connect(Events.on_changed_filter_apply)
    vars.wnd_main.txtFilter_OrderNum.textChanged.connect(Events.on_changed_filter_apply)
    vars.wnd_main.txtFilter_Serial.textChanged.connect(Events.on_changed_filter_apply)

    vars.wnd_main.radioOrderNum.toggled.connect(Events.on_radio_changed)

    vars.wnd_main.btnGoTest.clicked.connect(Events.on_clicked_go_test)
    vars.wnd_main.btnGoBack.clicked.connect(Events.on_clicked_go_back)

    vars.wnd_main.txtFlow.textChanged.connect(Events.on_changed_test_values)
    vars.wnd_main.txtLift.textChanged.connect(Events.on_changed_test_values)
    vars.wnd_main.txtPower.textChanged.connect(Events.on_changed_test_values)

    vars.wnd_main.btnAddPoint.clicked.connect(Events.on_clicked_add_point)
    vars.wnd_main.btnRemovePoint.clicked.connect(Events.on_clicked_remove_point)
    vars.wnd_main.btnClearCurve.clicked.connect(Events.on_clicked_clear_curve)
    vars.wnd_main.btnSaveCharts.clicked.connect(Events.on_clicked_test_data_save)

    vars.wnd_main.checkConnection.clicked.connect(Events.on_clicked_adam_connection)

    funcsAdam.broadcaster.event.connect(Events.on_adam_data_received)
    # vars.markers.eventMove.connect(Events.on_markers_move)
    pass


def set_color_scheme():
    # vars.wnd_main.stackedWidget.setStyleSheet("QStackedWidget { background: #404040; }")
    # style: str = "QComboBox { color: #ffffff; }" \
    #              "QComboBox:!editable { color: #dddddd; }"
    # vars.wnd_main.groupTestInfo.setStyleSheet(style)
    # vars.wnd_main.groupPumpInfo.setStyleSheet(style)
    pass


# FILL CONTROLS
def init_test_list():
    Journal.log("MainWindow::", "\tinitializing test list")
    vars.wnd_main.tableTests.setColumnWidth(0, 50)
    vars.wnd_main.tableTests.setColumnWidth(1, 150)
    vars.wnd_main.tableTests.setColumnWidth(2, 80)

    tests_display = ['ID', 'DateTime', 'OrderNum', 'Serial']
    tests_headers = ['№', 'Дата-Время', 'Наряд-Заказ', 'Заводской номер']
    tests_headers_sizes = [50, 150, 200, 200]
    tests_resizes = [QHeaderView.Fixed, QHeaderView.Fixed, QHeaderView.Stretch, QHeaderView.Stretch]
    # tests_data = funcsDB.execute_query(vars.testlist_query)
    vars.wnd_main.tests_filter = Models.FilterModel(vars.wnd_main)
    vars.wnd_main.tests_filter.setDynamicSortFilter(True)
    funcsTable.init(vars.wnd_main.tableTests, display=tests_display, filter_proxy=vars.wnd_main.tests_filter,
                    # data=tests_data,
                    headers=tests_headers, headers_sizes=tests_headers_sizes, headers_resizes=tests_resizes)


def fill_test_list():
    Journal.log("MainWindow::", "\tfilling test list")
    tests_data = funcsDB.execute_query(vars.testlist_query)
    funcsTable.set_data(vars.wnd_main.tableTests, tests_data)
    funcsTable.select_row(vars.wnd_main.tableTests, 0)
    # funcsDB.set_permission('Tests', False)


def init_points_list():
    Journal.log("MainWindow::", "\tinitializing points list")
    vars.wnd_main.tablePoints.setColumnWidth(0, 90)
    vars.wnd_main.tablePoints.setColumnWidth(1, 90)
    vars.wnd_main.tablePoints.setColumnWidth(2, 90)

    display = ['flow', 'lift', 'power']
    headers = ['расход', 'напор', 'мощность']
    headers_sizes = [90, 90, 90]
    resizes = [QHeaderView.Stretch, QHeaderView.Stretch, QHeaderView.Stretch]
    funcsTable.init(vars.wnd_main.tablePoints, display=display,
                    headers=headers, headers_sizes=headers_sizes, headers_resizes=resizes)


def fill_spinners():
    Journal.log("MainWindow::", "\tfilling spinners ->")
    fill_spinner(vars.wnd_main.cmbProducers, 'Producers', ['ID', 'Name'], 1)
    fill_spinner(vars.wnd_main.cmbCustomers, 'Customers', ['ID', 'Name'], 1, with_completer=True)
    fill_spinner(vars.wnd_main.cmbTypes, 'Types', ['ID', 'Name', 'Producer'], 1, with_completer=True)
    fill_spinner(vars.wnd_main.cmbSerials, 'Pumps', ['ID', 'Serial', 'Type'], 1, order_by='ID Asc', with_completer=True)
    fill_spinner(vars.wnd_main.cmbAssembly, 'Assembly', [''], 0)
    pass


def fill_spinner(spinner, table, columns, index, conditions=None, order_by='Name Asc', with_completer=False):
    Journal.log("MainWindow::", "\t--> filling", table)
    if conditions is None: conditions = {}
    items = ['', 'Новый', 'Ремонт']
    if not table == 'Assembly':
        items = [''] + funcsDB.get_records(table, columns, conditions, order_by)
    funcsSpinner.fill(spinner, items, columns[index], with_completer=with_completer)


# GRAPH
def init_graph():
    Journal.log("MainWindow::", "\tinitializing graph widget")
    vars.graph_info = PumpGraph.PumpGraph(100, 100, vars.path_to_pix)
    vars.graph_info.setMargins([10, 10, 10, 10])
    vars.markers = Markers(['test_lift', 'test_power'], vars.graph_info)
    vars.markers.setMarkerColor('test_lift', QtCore.Qt.blue)
    vars.markers.setMarkerColor('test_power', QtCore.Qt.red)
    vars.wnd_main.gridGraphTest.addWidget(vars.markers, 0, 0)


def display_sensors(sensors: dict):
    vars.wnd_main.txtRPM.setText(str(sensors['rpm']))
    vars.wnd_main.txtTorque.setText(str(sensors['torque']))
    vars.wnd_main.txtPsiIn.setText(str(sensors['pressure_in']))
    vars.wnd_main.txtPsiOut.setText(str(sensors['pressure_out']))
    vars.wnd_main.txtFlow05.setText(str(sensors['flow05']))
    vars.wnd_main.txtFlow1.setText(str(sensors['flow1']))
    vars.wnd_main.txtFlow2.setText(str(sensors['flow2']))
