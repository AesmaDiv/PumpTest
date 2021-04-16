"""
    Модуль содержит функции основного окна программы
"""
from PyQt5.QtWidgets import QHeaderView, QGroupBox, QWidget
from PyQt5.QtWidgets import QPushButton, QLineEdit, QComboBox
from PyQt5 import QtCore

from Functions import funcs_db, funcsTable, funcsAdam, funcsGraph
from GUI import events, models, PumpGraph
from GUI.Markers import Markers
from AesmaLib.journal import Journal
from AesmaLib.database import QueryParams
from Globals import gvars


@Journal.logged
def register_events():
    """ привязывает события элементов формы к обработчикам """
    wnd = gvars.wnd_main
    wnd.tableTests.selectionModel().currentChanged.connect(events.on_changed_testlist)

    wnd.cmbProducer.currentIndexChanged.connect(events.on_changed_combo_producers)
    wnd.cmbType.currentIndexChanged.connect(events.on_changed_combo_types)
    wnd.cmbSerial.currentIndexChanged.connect(events.on_changed_combo_serials)

    wnd.btnTest.clicked.connect(events.on_clicked_test)
    wnd.btnTest_New.clicked.connect(events.on_clicked_test_new)
    wnd.btnTest_Save.clicked.connect(events.on_clicked_test_info_save)
    wnd.btnTest_Cancel.clicked.connect(events.on_clicked_test_info_cancel)

    wnd.btnPump_New.clicked.connect(events.on_clicked_pump_new)
    wnd.btnPump_Save.clicked.connect(events.on_clicked_pump_save)
    wnd.btnPump_Cancel.clicked.connect(events.on_clicked_pump_cancel)

    wnd.btnFilterReset.clicked.connect(events.on_clicked_filter_reset)

    wnd.txtFilter_ID.textChanged.connect(events.on_changed_filter_apply)
    wnd.txtFilter_DateTime.textChanged.connect(events.on_changed_filter_apply)
    wnd.txtFilter_OrderNum.textChanged.connect(events.on_changed_filter_apply)
    wnd.txtFilter_Serial.textChanged.connect(events.on_changed_filter_apply)

    wnd.radioOrderNum.toggled.connect(events.on_changed_testlist_column)

    wnd.btnGoTest.clicked.connect(events.on_clicked_go_test)
    wnd.btnGoBack.clicked.connect(events.on_clicked_go_back)

    wnd.txtFlow.textChanged.connect(events.on_changed_sensors)
    wnd.txtLift.textChanged.connect(events.on_changed_sensors)
    wnd.txtPower.textChanged.connect(events.on_changed_sensors)

    wnd.btnAddPoint.clicked.connect(events.on_clicked_add_point)
    wnd.btnRemovePoint.clicked.connect(events.on_clicked_remove_point)
    wnd.btnClearCurve.clicked.connect(events.on_clicked_clear_curve)
    wnd.btnSaveCharts.clicked.connect(events.on_clicked_test_data_save)

    wnd.checkConnection.clicked.connect(events.on_clicked_adam_connection)

    funcsAdam.broadcaster.event.connect(events.on_adam_data_received)
    # gvars.markers.eventMove.connect(events.on_markers_move)


@Journal.logged
def set_color_scheme():
    """ устанавливает цветовую схему """
    # gvars.wnd_main.stackedWidget.setStyleSheet("QStackedWidget { background: #404040; }")
    # style: str = "QComboBox { color: #ffffff; }" \
    #              "QComboBox:!editable { color: #dddddd; }"
    # gvars.wnd_main.groupTestInfo.setStyleSheet(style)
    # gvars.wnd_main.groupPumpInfo.setStyleSheet(style)


@Journal.logged
def init_test_list():
    """ инициализирует список тестов """
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
    wnd.tests_filter = models.FilterModel(wnd)
    wnd.tests_filter.setDynamicSortFilter(True)
    funcsTable.init(wnd.tableTests, display=tests_display,
                    filter_proxy=wnd.tests_filter, data=tests_data,
                    headers=tests_headers, headers_sizes=tests_headers_sizes,
                    headers_resizes=tests_resizes)


@Journal.logged
def fill_test_list():
    """ заполняет список тестов """
    wnd = gvars.wnd_main
    tests_data = funcs_db.execute_query(gvars.TESTLIST_QUERY)
    funcsTable.set_data(wnd.tableTests, tests_data)
    funcsTable.select_row(wnd.tableTests, 0)
    # funcs_db.set_permission('Tests', False)


@Journal.logged
def init_points_list():
    """ инициализирует список точек """
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


@Journal.logged
def fill_combos():
    """ инициализирует комбобоксы --> """
    fill_combos_test()
    fill_combos_pump()


def fill_combos_test():
    """ инициализирует комбобоксы для теста --> """
    fill_combo_customers()
    fill_combo_assembly()


def fill_combos_pump():
    """ инициализирует комбобоксы для насоса --> """
    fill_combo_producers()
    fill_combo_types()
    fill_combo_serials()


@Journal.logged
def fill_combo_customers():
    """ --> заполняет заказчик (cmbCustomer) """
    qp = QueryParams('Customers', ['ID', 'Name'])
    fill_combo(gvars.wnd_main.cmbCustomer, qp)


@Journal.logged
def fill_combo_assembly():
    """ --> заполняет сборка (cmbAssembly) """
    qp = QueryParams('Assemblies', ['ID', 'Name'])
    fill_combo(gvars.wnd_main.cmbAssembly, qp)


@Journal.logged
def fill_combo_producers():
    """ --> заполняет производитель (cmbProducer) """
    qp = QueryParams('Producers', ['ID', 'Name'])
    fill_combo(gvars.wnd_main.cmbProducer, qp)


@Journal.logged
def fill_combo_types():
    """ --> заполняет типоразмер (cmbType) """
    qp = QueryParams('Types', ['ID', 'Name', 'Producer'])
    fill_combo(gvars.wnd_main.cmbType, qp)


@Journal.logged
def fill_combo_serials():
    """ --> заполняет зав.номер (cmbSerial) """
    qp = QueryParams('Pumps', ['ID', 'Serial', 'Type'])
    fill_combo(gvars.wnd_main.cmbSerial, qp)


def fill_combo(combo: QComboBox, query_params):
    """ инициализирует фильтр и заполняет комбобокс """
    model = models.ComboItemModel(combo)
    display = query_params.columns[1]
    data = funcs_db.get_records(query_params)
    data.insert(0, {key: None for key in query_params.columns})
    model.fill(data, display)
    combo.setModel(model)


@Journal.logged
def init_graph():
    """ инициализирует элемент графика """
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


@Journal.logged
def display_record():
    """ отображает полную информации о записи """
    wnd = gvars.wnd_main
    row = funcsTable.get_row(wnd.tableTests)
    if row:
        display_test(row['ID'])


def display_test(test_id: int):
    """ отображает информацию о тесте """
    Journal.log(f"{__name__}::\t загружает информацию о тесте --> {test_id}")
    if gvars.rec_test.load(test_id):
        group_display(gvars.wnd_main.groupTestInfo, gvars.rec_test)
        group_lock(gvars.wnd_main.groupTestInfo, True)
        display_pump(gvars.rec_test['Pump'])


def display_pump(pump_id: int):
    """ отображает информацию о насосе """
    Journal.log(f"{__name__}::\t загружает информацию о насосе --> {pump_id}")
    wnd = gvars.wnd_main
    if gvars.rec_pump.load(pump_id):
        type_id = gvars.rec_pump['Type']
        Journal.log(f"{__name__}::\t загружает информацию о типе --> {type_id}")
        if gvars.rec_type.load(type_id):
            group_display(wnd.groupPumpInfo, gvars.rec_pump)
            group_lock(wnd.groupPumpInfo, True)
            wnd.groupTestFrame.setTitle(gvars.rec_type.Name)



@Journal.logged
def save_test_info():
    """ сохраняет информацию о насосе """
    Journal.log(f"{__name__}::\t сохраняет информацию о новом тесте")
    wnd = gvars.wnd_main
    gvars.rec_test['Pump'] = gvars.rec_pump['ID']
    group_save(wnd.groupTestInfo, gvars.rec_test)
    group_lock(wnd.groupTestInfo, True)
    gvars.rec_test.save()


@Journal.logged
def save_pump_info() -> bool:
    """ сохраняет информацию о насосе """
    wnd = gvars.wnd_main
    group_save(wnd.groupPumpInfo, gvars.rec_pump)
    group_lock(wnd.groupPumpInfo, True)
    return gvars.rec_pump.save()


def clear_record(also_clear_classes: bool):
    """ очищает отображаемую информацию и сами записи """
    wnd = gvars.wnd_main
    group_clear(wnd.groupTestInfo)
    group_clear(wnd.groupPumpInfo)
    if also_clear_classes:
        gvars.rec_test.clear()
        gvars.rec_pump.clear()
        gvars.rec_type.clear()


def group_display(group: QGroupBox, record, log=False):
    """ отображает информацию записи в полях группы """
    Journal.log(f"{__name__}::\t заполняет поля группы {group.objectName()}")
    for name, value in record.items():
        if name in ('ID', 'Type', 'Producer'):
            continue
        item = group.findChildren(QWidget, QtCore.QRegExp(name))
        if item:
            if isinstance(item[0], QLineEdit):
                item[0].setText(str(value))
            elif isinstance(item[0], QComboBox):
                item[0].model().select_contains(value)
            if log:
                Journal.log(f"{item[0].objectName()} <== {value}")


def group_save(group: QGroupBox, record, log=False):
    """ сохраняет информацию записи в полях группы """
    Journal.log(f"{__name__}::\t сохраняет значения",
                f"из полей группы {group.objectName()}")
    record['ID'] = None
    for name in record.keys():
        item = group.findChildren(QWidget, QtCore.QRegExp(name))
        if item:
            if isinstance(item[0], QLineEdit):
                record[name] = item[0].text()
            elif isinstance(item[0], QComboBox):
                record[name] = item[0].currentData()['ID'] \
                    if name in ('Type', 'Producer', 'Customer', 'Assembly') \
                    else item[0].currentText()
            if log:
                Journal.log(f"{item[0].objectName()} ==> {record[name]}")


def group_clear(group: QGroupBox):
    """ очищает отображаемую информацию записи в полях группы """
    Journal.log(f"{__name__}::\t очищает поля группы {group.objectName()}")
    widgets = group.findChildren(QWidget)
    for item in widgets:
        if isinstance(item, QLineEdit):
            item.clear()
        elif isinstance(item, QComboBox):
            item.model().resetFilter()
            item.model().select(0)
    group.repaint()


def group_lock(group: QGroupBox, state: bool):
    """ блокирует поля группы от изменений """
    Journal.log(f"{__name__}::\t устанавливает блокировку полей группы",
                f"{group.objectName()} => {state}")
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


def testlist_filter_apply(conditions: dict=None):
    """ применяет фильтр к списку тестов """
    wnd = gvars.wnd_main
    if conditions is None:
        filter_id = wnd.txtFilter_ID.text()
        filter_datetime = wnd.txtFilter_DateTime.text()
        filter_ordernum = wnd.txtFilter_OrderNum.text()
        filter_serial = wnd.txtFilter_Serial.text()
        conditions = [filter_id, filter_datetime, filter_ordernum, filter_serial]
    wnd.tests_filter.applyFilter(conditions)


def testlist_filter_reset():
    """ сбрасывает фильтр списка тестов """
    wnd = gvars.wnd_main
    group_clear(wnd.groupTestList)
    clear_record(True)
    wnd.tests_filter.applyFilter()
    funcsTable.select_row(wnd.tableTests, -1)


def testlist_filter_switch():
    """ переключает список тестов (зав.номер/наряд-заказ) """
    wnd = gvars.wnd_main
    if wnd.radioOrderNum.isChecked():
        wnd.tableTests.horizontalHeader().hideSection(3)
        wnd.tableTests.horizontalHeader().showSection(2)
        wnd.txtFilter_OrderNum.show()
        wnd.txtFilter_Serial.hide()
    else:
        wnd.tableTests.horizontalHeader().hideSection(2)
        wnd.tableTests.horizontalHeader().showSection(3)
        wnd.txtFilter_OrderNum.hide()
        wnd.txtFilter_Serial.show()


def combos_filters_reset():
    """ сбрасывает фильт для комбобоксов насоса """
    wnd = gvars.wnd_main
    wnd.cmbType.model().resetFilter()
    wnd.cmbSerial.model().resetFilter()
