"""
    Модуль содержит функции основного окна программы
"""
from PyQt5.QtWidgets import QHeaderView, QGroupBox, QWidget
from PyQt5.QtWidgets import QPushButton, QLineEdit, QComboBox
from PyQt5 import QtCore

from Functions import funcs_db, funcsTable, funcsSpinner, funcsAdam, funcsGraph
from GUI import Events, Models, PumpGraph, filters
from GUI.Markers import Markers
from AesmaLib.journal import Journal
from Globals import gvars


def register_events():
    """ Регистрация событий элементов формы (привязка к обработчикам) """
    Journal.log("MainWindow::", "\tregistering events")
    wnd = gvars.wnd_main
    wnd.tableTests.selectionModel().currentChanged.connect(Events.on_changed_testlist)

    wnd.cmbProducer.currentIndexChanged.connect(Events.on_changed_combo_producers)
    wnd.cmbType.currentIndexChanged.connect(Events.on_changed_combo_types)
    wnd.cmbSerial.currentIndexChanged.connect(Events.on_changed_combo_serials)

    wnd.btnTest.clicked.connect(Events.on_clicked_test)
    wnd.btnTest_New.clicked.connect(Events.on_clicked_test_new)
    wnd.btnTest_Save.clicked.connect(Events.on_clicked_test_info_save)
    wnd.btnTest_Cancel.clicked.connect(Events.on_clicked_test_info_cancel)

    wnd.btnPump_New.clicked.connect(Events.on_clicked_pump_new)
    wnd.btnPump_Save.clicked.connect(Events.on_clicked_pump_save)
    wnd.btnPump_Cancel.clicked.connect(Events.on_clicked_pump_cancel)

    wnd.btnFilterReset.clicked.connect(Events.on_clicked_filter_reset)

    wnd.txtFilter_ID.textChanged.connect(Events.on_changed_filter_apply)
    wnd.txtFilter_DateTime.textChanged.connect(Events.on_changed_filter_apply)
    wnd.txtFilter_OrderNum.textChanged.connect(Events.on_changed_filter_apply)
    wnd.txtFilter_Serial.textChanged.connect(Events.on_changed_filter_apply)

    wnd.radioOrderNum.toggled.connect(Events.on_radio_changed)

    wnd.btnGoTest.clicked.connect(Events.on_clicked_go_test)
    wnd.btnGoBack.clicked.connect(Events.on_clicked_go_back)

    wnd.txtFlow.textChanged.connect(Events.on_changed_sensors)
    wnd.txtLift.textChanged.connect(Events.on_changed_sensors)
    wnd.txtPower.textChanged.connect(Events.on_changed_sensors)

    wnd.btnAddPoint.clicked.connect(Events.on_clicked_add_point)
    wnd.btnRemovePoint.clicked.connect(Events.on_clicked_remove_point)
    wnd.btnClearCurve.clicked.connect(Events.on_clicked_clear_curve)
    wnd.btnSaveCharts.clicked.connect(Events.on_clicked_test_data_save)

    wnd.checkConnection.clicked.connect(Events.on_clicked_adam_connection)

    funcsAdam.broadcaster.event.connect(Events.on_adam_data_received)
    # gvars.markers.eventMove.connect(Events.on_markers_move)


def set_color_scheme():
    """ устанавливает цветовую схему """
    # gvars.wnd_main.stackedWidget.setStyleSheet("QStackedWidget { background: #404040; }")
    # style: str = "QComboBox { color: #ffffff; }" \
    #              "QComboBox:!editable { color: #dddddd; }"
    # gvars.wnd_main.groupTestInfo.setStyleSheet(style)
    # gvars.wnd_main.groupPumpInfo.setStyleSheet(style)


# FILL CONTROLS
def init_test_list():
    """ инициализирует список тестов """
    Journal.log("MainWindow::", "\tinitializing test list")
    wnd = gvars.wnd_main
    wnd.tableTests.setColumnWidth(0, 50)
    wnd.tableTests.setColumnWidth(1, 150)
    wnd.tableTests.setColumnWidth(2, 80)
    tests_display = ['ID', 'DateTime', 'OrderNum', 'Serial']
    tests_headers = ['№', 'Дата-Время', 'Наряд-Заказ', 'Заводской номер']
    tests_headers_sizes = [50, 150, 200, 200]
    tests_resizes = [QHeaderView.Fixed, QHeaderView.Fixed,
                     QHeaderView.Stretch, QHeaderView.Stretch]
    tests_data = funcs_db.execute_query(gvars.TESTLIST_QUERY)
    wnd.tests_filter = Models.FilterModel(wnd)
    wnd.tests_filter.setDynamicSortFilter(True)
    funcsTable.init(wnd.tableTests, display=tests_display,
                    filter_proxy=wnd.tests_filter, data=tests_data,
                    headers=tests_headers, headers_sizes=tests_headers_sizes,
                    headers_resizes=tests_resizes)


def fill_test_list():
    """ заполняет список тестов """
    Journal.log("MainWindow::", "\tfilling test list")
    tests_data = funcs_db.execute_query(gvars.TESTLIST_QUERY)
    funcsTable.set_data(gvars.wnd_main.tableTests, tests_data)
    funcsTable.select_row(gvars.wnd_main.tableTests, 0)
    # funcs_db.set_permission('Tests', False)


def init_points_list():
    """ инициализирует список точек """
    Journal.log("MainWindow::", "\tinitializing points list")
    wnd = gvars.wnd_main
    wnd.tablePoints.setColumnWidth(0, 90)
    wnd.tablePoints.setColumnWidth(1, 90)
    wnd.tablePoints.setColumnWidth(2, 90)
    display = ['flow', 'lift', 'power']
    headers = ['расход', 'напор', 'мощность']
    headers_sizes = [90, 90, 90]
    resizes = [QHeaderView.Stretch, QHeaderView.Stretch, QHeaderView.Stretch]
    funcsTable.init(wnd.tablePoints, display=display, headers=headers,
                    headers_sizes=headers_sizes, headers_resizes=resizes)


def fill_spinners():
    """ заполняет комбобоксы формы """
    Journal.log("MainWindow::", "\tfilling spinners ->")
    db_params1 = {'columns': ['ID', 'Name']}
    db_params2 = {'columns': ['ID', 'Name', 'Producer']}
    db_params3 = {'columns': ['ID', 'Serial', 'Type'], 'order': 'ID Asc'}
    db_params4 = {'columns': ['']}
    fill_spinner(gvars.wnd_main.cmbProducer, 'Producers', db_params1, 1)
    fill_spinner(gvars.wnd_main.cmbCustomer, 'Customers', db_params1, 1, True)
    fill_spinner(gvars.wnd_main.cmbType, 'Types', db_params2, 1, True)
    fill_spinner(gvars.wnd_main.cmbSerial, 'Pumps', db_params3, 1, True)
    fill_spinner(gvars.wnd_main.cmbAssembly, 'Assembly', db_params4, 0)


def fill_spinner(spinner, table, db_params, index, with_completer=False):
    """ заполняет комбобокс в соответствии с условиями """
    Journal.log("MainWindow::", "\t--> filling", table)
    clmns = db_params['columns']
    conds = db_params['conditions'] if 'conditions' in db_params else {}
    order = db_params['order'] if 'order' in db_params else 'Name Asc'
    if table == 'Assembly':
        items = ['', 'Новый', 'Ремонт']
    else:
        items = [''] + funcs_db.get_records(table, clmns, conds, order)
    funcsSpinner.fill(spinner, items, clmns[index],
                      with_completer=with_completer)


# GRAPH
def init_graph():
    """ инициализирует элемент графика """
    Journal.log("MainWindow::", "\tinitializing graph widget")
    gvars.graph_info = PumpGraph.PumpGraph(100, 100, gvars.PATH_TO_PIC)
    gvars.graph_info.setMargins([10, 10, 10, 10])
    gvars.markers = Markers(['test_lift', 'test_power'], gvars.graph_info)
    gvars.markers.setMarkerColor('test_lift', QtCore.Qt.blue)
    gvars.markers.setMarkerColor('test_power', QtCore.Qt.red)
    gvars.wnd_main.gridGraphTest.addWidget(gvars.markers, 0, 0)


def display_sensors(sensors: dict):
    """ отображает показания датчиков """
    wnd = gvars.wnd_main
    wnd.txtRPM.setText(str(sensors['rpm']))
    wnd.txtTorque.setText(str(sensors['torque']))
    wnd.txtPsiIn.setText(str(sensors['pressure_in']))
    wnd.txtPsiOut.setText(str(sensors['pressure_out']))
    wnd.txtFlow05.setText(str(sensors['flow05']))
    wnd.txtFlow1.setText(str(sensors['flow1']))
    wnd.txtFlow2.setText(str(sensors['flow2']))


def display_record():
    """ отображает полную информации о записи """
    wnd = gvars.wnd_main
    row = funcsTable.get_row(wnd.tableTests)
    if gvars.rec_test.load(row['ID']):
        group_display(wnd.groupTestInfo, gvars.rec_test)
        if gvars.rec_pump.load(gvars.rec_test['Pump']):
            group_display(wnd.groupPumpInfo, gvars.rec_pump)
            if gvars.rec_type.load(gvars.rec_pump['Type']):
                funcsGraph.draw_charts()

def clear_record(also_clear_classes: bool):
    """ очищает отображаемую информацию и сами записи """
    wnd = gvars.wnd_main
    group_clear(wnd.groupTestInfo)
    group_clear(wnd.groupPumpInfo)
    if also_clear_classes:
        gvars.rec_test.clear()
        gvars.rec_pump.clear()
        gvars.rec_type.clear()


def group_display(group: QGroupBox, record):
    """ отображает информацию записи в полях группы """
    for name, value in record.items():
        item = group.findChild(QLineEdit, f'txt{name}')
        if item:
            item.setText(str(value))
            continue
        item = group.findChild(QComboBox, f'cmb{name}')
        if item:
            funcsSpinner.select_item_containing(item, value)
            continue


def group_clear(group: QGroupBox):
    """ очищает отображаемую информацию записи в полях группы """
    widgets = group.findChildren(QWidget)
    for item in widgets:
        if isinstance(item, QLineEdit):
            item.clear()
        elif isinstance(item, QComboBox):
            item.setCurrentIndex(0)
    group.repaint()


def group_lock(group: QGroupBox, state: bool):
    """ блокирует поля группы от изменений """
    widgets = group.findChildren(QWidget)
    for item in widgets:
        if isinstance(item, QLineEdit):
            item.setReadOnly(state)
        elif isinstance(item, QComboBox):
            item.setEnabled(not state)
        elif isinstance(item, QPushButton):
            if '_New' in item.objectName():
                _ = item.show() if state else item.hide()
            else:
                _ = item.hide() if state else item.show()
        if state:
            item.clearFocus()
    group.repaint()

def testlist_filter_apply():
    """ применяет фильтр к списку тестов """
    filters.TestListFilters.apply()

def testlist_filter_reset():
    """ сбрасывает фильтр списка тестов """
    filters.TestListFilters.reset()

def testlist_filter_switch():
    """ переключает список тестов (зав.номер/наряд-заказ) """
    filters.TestListFilters.switch_others()
