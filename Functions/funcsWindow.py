from PyQt5.QtWidgets import QHeaderView, QFrame
from PyQt5 import QtCore

from AesmaLib.journal import Journal
from AppClasses.Pump import Point
from GUI import Events, Models, PumpGraph
from Functions import funcs_db, funcsTable, funcsSpinner, funcsAdam
from Globals import gvars


# INIT WINDOW
from GUI.Markers import Markers


def register_events():
    Journal.log("MainWindow::", "\tregistering events")
    gvars.wnd_main.tableTests.selectionModel().currentChanged.connect(Events.on_changed_testlist)

    gvars.wnd_main.cmbProducers.currentIndexChanged.connect(Events.on_changed_combo_producers)
    gvars.wnd_main.cmbTypes.currentIndexChanged.connect(Events.on_changed_combo_types)
    gvars.wnd_main.cmbSerials.currentIndexChanged.connect(Events.on_changed_combo_serials)

    gvars.wnd_main.btnTest.clicked.connect(Events.on_clicked_test)
    gvars.wnd_main.btnTest_New.clicked.connect(Events.on_clicked_test_new)
    gvars.wnd_main.btnTest_Save.clicked.connect(Events.on_clicked_test_info_save)
    gvars.wnd_main.btnTest_Cancel.clicked.connect(Events.on_clicked_test_info_cancel)

    gvars.wnd_main.btnPump_New.clicked.connect(Events.on_clicked_pump_new)
    gvars.wnd_main.btnPump_Save.clicked.connect(Events.on_clicked_pump_save)
    gvars.wnd_main.btnPump_Cancel.clicked.connect(Events.on_clicked_pump_cancel)

    gvars.wnd_main.btnFilterReset.clicked.connect(Events.on_clicked_filter_reset)

    gvars.wnd_main.txtFilter_ID.textChanged.connect(Events.on_changed_filter_apply)
    gvars.wnd_main.txtFilter_DateTime.textChanged.connect(Events.on_changed_filter_apply)
    gvars.wnd_main.txtFilter_OrderNum.textChanged.connect(Events.on_changed_filter_apply)
    gvars.wnd_main.txtFilter_Serial.textChanged.connect(Events.on_changed_filter_apply)

    gvars.wnd_main.radioOrderNum.toggled.connect(Events.on_radio_changed)

    gvars.wnd_main.btnGoTest.clicked.connect(Events.on_clicked_go_test)
    gvars.wnd_main.btnGoBack.clicked.connect(Events.on_clicked_go_back)

    gvars.wnd_main.txtFlow.textChanged.connect(Events.on_changed_test_values)
    gvars.wnd_main.txtLift.textChanged.connect(Events.on_changed_test_values)
    gvars.wnd_main.txtPower.textChanged.connect(Events.on_changed_test_values)

    gvars.wnd_main.btnAddPoint.clicked.connect(Events.on_clicked_add_point)
    gvars.wnd_main.btnRemovePoint.clicked.connect(Events.on_clicked_remove_point)
    gvars.wnd_main.btnClearCurve.clicked.connect(Events.on_clicked_clear_curve)
    gvars.wnd_main.btnSaveCharts.clicked.connect(Events.on_clicked_test_data_save)

    gvars.wnd_main.checkConnection.clicked.connect(Events.on_clicked_adam_connection)

    funcsAdam.broadcaster.event.connect(Events.on_adam_data_received)
    # gvars.markers.eventMove.connect(Events.on_markers_move)


def set_color_scheme():
    # gvars.wnd_main.stackedWidget.setStyleSheet("QStackedWidget { background: #404040; }")
    # style: str = "QComboBox { color: #ffffff; }" \
    #              "QComboBox:!editable { color: #dddddd; }"
    # gvars.wnd_main.groupTestInfo.setStyleSheet(style)
    # gvars.wnd_main.groupPumpInfo.setStyleSheet(style)
    pass


# FILL CONTROLS
def init_test_list():
    Journal.log("MainWindow::", "\tinitializing test list")
    gvars.wnd_main.tableTests.setColumnWidth(0, 50)
    gvars.wnd_main.tableTests.setColumnWidth(1, 150)
    gvars.wnd_main.tableTests.setColumnWidth(2, 80)

    tests_display = ['ID', 'DateTime', 'OrderNum', 'Serial']
    tests_headers = ['№', 'Дата-Время', 'Наряд-Заказ', 'Заводской номер']
    tests_headers_sizes = [50, 150, 200, 200]
    tests_resizes = [QHeaderView.Fixed, QHeaderView.Fixed, QHeaderView.Stretch, QHeaderView.Stretch]
    tests_data = funcs_db.execute_query(gvars.TESTLIST_QUERY)
    gvars.wnd_main.tests_filter = Models.FilterModel(gvars.wnd_main)
    gvars.wnd_main.tests_filter.setDynamicSortFilter(True)
    funcsTable.init(gvars.wnd_main.tableTests, display=tests_display, filter_proxy=gvars.wnd_main.tests_filter,
                    data=tests_data,
                    headers=tests_headers, headers_sizes=tests_headers_sizes, headers_resizes=tests_resizes)


def fill_test_list():
    Journal.log("MainWindow::", "\tfilling test list")
    tests_data = funcs_db.execute_query(gvars.TESTLIST_QUERY)
    funcsTable.set_data(gvars.wnd_main.tableTests, tests_data)
    funcsTable.select_row(gvars.wnd_main.tableTests, 0)
    # funcs_db.set_permission('Tests', False)


def init_points_list():
    Journal.log("MainWindow::", "\tinitializing points list")
    gvars.wnd_main.tablePoints.setColumnWidth(0, 90)
    gvars.wnd_main.tablePoints.setColumnWidth(1, 90)
    gvars.wnd_main.tablePoints.setColumnWidth(2, 90)

    display = ['flow', 'lift', 'power']
    headers = ['расход', 'напор', 'мощность']
    headers_sizes = [90, 90, 90]
    resizes = [QHeaderView.Stretch, QHeaderView.Stretch, QHeaderView.Stretch]
    funcsTable.init(gvars.wnd_main.tablePoints, display=display,
                    headers=headers, headers_sizes=headers_sizes, headers_resizes=resizes)


def fill_spinners():
    Journal.log("MainWindow::", "\tfilling spinners ->")
    fill_spinner(gvars.wnd_main.cmbProducers, 'Producers', ['ID', 'Name'], 1)
    fill_spinner(gvars.wnd_main.cmbCustomers, 'Customers', ['ID', 'Name'], 1, with_completer=True)
    fill_spinner(gvars.wnd_main.cmbTypes, 'Types', ['ID', 'Name', 'Producer'], 1, with_completer=True)
    fill_spinner(gvars.wnd_main.cmbSerials, 'Pumps', ['ID', 'Serial', 'Type'], 1, order_by='ID Asc', with_completer=True)
    fill_spinner(gvars.wnd_main.cmbAssembly, 'Assembly', [''], 0)
    pass


def fill_spinner(spinner, table, columns, index, conditions=None, order_by='Name Asc', with_completer=False):
    Journal.log("MainWindow::", "\t--> filling", table)
    if conditions is None: conditions = {}
    items = ['', 'Новый', 'Ремонт']
    if not table == 'Assembly':
        items = [''] + funcs_db.get_records(table, columns, conditions, order_by)
    funcsSpinner.fill(spinner, items, columns[index], with_completer=with_completer)


# GRAPH
def init_graph():
    Journal.log("MainWindow::", "\tinitializing graph widget")
    gvars.graph_info = PumpGraph.PumpGraph(100, 100, gvars.PATH_TO_PIC)
    gvars.graph_info.setMargins([10, 10, 10, 10])
    gvars.markers = Markers(['test_lift', 'test_power'], gvars.graph_info)
    gvars.markers.setMarkerColor('test_lift', QtCore.Qt.blue)
    gvars.markers.setMarkerColor('test_power', QtCore.Qt.red)
    gvars.wnd_main.gridGraphTest.addWidget(gvars.markers, 0, 0)


def display_sensors(sensors: dict):
    gvars.wnd_main.txtRPM.setText(str(sensors['rpm']))
    gvars.wnd_main.txtTorque.setText(str(sensors['torque']))
    gvars.wnd_main.txtPsiIn.setText(str(sensors['pressure_in']))
    gvars.wnd_main.txtPsiOut.setText(str(sensors['pressure_out']))
    gvars.wnd_main.txtFlow05.setText(str(sensors['flow05']))
    gvars.wnd_main.txtFlow1.setText(str(sensors['flow1']))
    gvars.wnd_main.txtFlow2.setText(str(sensors['flow2']))
