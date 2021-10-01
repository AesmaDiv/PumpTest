"""
    Модуль содержит функции основного окна программы
"""
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMenu
from PyQt5.QtGui import QCursor

from Classes.UI import funcs_table, funcs_table_points, funcs_table_vibr
from Classes.UI import funcs_testlist, funcs_combo, funcs_group, funcs_display
from Classes.Adam.adam_manager import AdamManager
from Classes.UI import funcs_aux
from Classes.report import Report
from Classes.Data.data_manager import DataManager
from Classes.Graph.graph_manager import GraphManager
from Classes.test import Test

from AesmaLib.message import Message
from AesmaLib.journal import Journal


class MainWindow(QMainWindow):
    """ Класс описания функционала главного окна приложения """
    def __init__(self, pathes, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        try:
            path = pathes['WND']
            uic.loadUi(path, self)
        except IOError as error:
            Journal.log(__name__, "::\t", "ошибка:", str(error))
            return None
        self._is_displaying = dict.fromkeys(['Producer','Type','Serial'], False)
        self._adam = AdamManager()
        self._data_manager = DataManager(pathes['DB'])
        self._testdata = self._data_manager.get_testdata()
        self._graph_manager = GraphManager(self._testdata)
        self._report = Report(pathes['TEMPLATE'], self._graph_manager, self._testdata)

    @Journal.logged
    def prepare(self):
        """ инициализирует и подготавливает компоненты главного окна """
        funcs_testlist.init(self)
        funcs_testlist.fill(self, self._data_manager)
        funcs_combo.fill_combos(self, self._data_manager)
        funcs_table_points.init(self)
        funcs_table_vibr.init(self)
        self.set_color_scheme()
        self.register_events()
        self.init_markers()

    @Journal.logged
    def show(self):
        """ отображает главное окно """
        super().show()
        self.move(1, 1)
        funcs_testlist.filter_switch(self)
        funcs_group.group_lock(self.groupTestInfo, True)
        funcs_group.group_lock(self.groupPumpInfo, True)
        Test.switch_running_state(self, False)

    @Journal.logged
    def set_color_scheme(self):
        """ устанавливает цветовую схему """
        # gvars.wnd_main.stackedWidget.setStyleSheet("QStackedWidget { background: #404040; }")
        # style: str = "QComboBox { color: #ffffff; }" \
        #              "QComboBox:!editable { color: #dddddd; }"
        # gvars.wnd_main.groupTestInfo.setStyleSheet(style)
        # gvars.wnd_main.groupPumpInfo.setStyleSheet(style)

    @Journal.logged
    def register_events(self):
        """ привязывает события элементов формы к обработчикам """
        self.tableTests.selectionModel().currentChanged.connect(self.on_changed_testlist)
        self.tableTests.customContextMenuRequested.connect(self.on_menu_testlist)

        self.cmbProducer.currentIndexChanged.connect(self.on_changed_combo_producers)
        self.cmbType.currentIndexChanged.connect(self.on_changed_combo_types)
        self.cmbSerial.currentIndexChanged.connect(self.on_changed_combo_serials)

        self.btnTest.clicked.connect(self.on_clicked_test)
        self.btnTest_New.clicked.connect(self.on_clicked_test_new)
        self.btnTest_Save.clicked.connect(self.on_clicked_test_info_save)
        self.btnTest_Cancel.clicked.connect(self.on_clicked_test_info_cancel)

        self.btnPump_New.clicked.connect(self.on_clicked_pump_new)
        self.btnPump_Save.clicked.connect(self.on_clicked_pump_save)
        self.btnPump_Cancel.clicked.connect(self.on_clicked_pump_cancel)

        self.btnFilterReset.clicked.connect(self.on_clicked_filter_reset)

        self.txtFilter_ID.textChanged.connect(self.on_changed_filter_apply)
        self.txtFilter_DateTime.textChanged.connect(self.on_changed_filter_apply)
        self.txtFilter_OrderNum.textChanged.connect(self.on_changed_filter_apply)
        self.txtFilter_Serial.textChanged.connect(self.on_changed_filter_apply)

        self.radioOrderNum.toggled.connect(self.on_changed_column_testlist)

        self.btnGoTest.clicked.connect(self.on_clicked_go_test)
        self.btnGoBack.clicked.connect(self.on_clicked_go_back)

        self.txtFlow.textChanged.connect(self.on_changed_sensors)
        self.txtLift.textChanged.connect(self.on_changed_sensors)
        self.txtPower.textChanged.connect(self.on_changed_sensors)

        self.btnAddPoint.clicked.connect(self.on_clicked_add_point)
        self.btnRemovePoint.clicked.connect(self.on_clicked_remove_point)
        self.btnClearCurve.clicked.connect(self.on_clicked_clear_curve)
        self.btnSaveCharts.clicked.connect(self.on_clicked_test_result_save)

        self.checkConnection.clicked.connect(self.on_clicked_adam_connection)
        # funcsAdam.broadcaster.event.connect(self.on_adam_data_received)

        self.radioPointsReal.toggled.connect(self.on_changed_points_mode)
        # gvars.markers.eventMove.connect(self.on_markers_move)
        self.txtFlow.wheelEvent = self.on_mouse_wheel_flow
        self.txtLift.wheelEvent = self.on_mouse_wheel_lift
        self.txtPower.wheelEvent = self.on_mouse_wheel_power

    def init_markers(self):
        params = {
            'test_lft': Qt.blue,
            'test_pwr': Qt.red
        }
        self._graph_manager.init_markers(params, self.gridGraphTest)

    def on_changed_testlist(self):
        """ изменение выбора теста """
        item = funcs_table.get_row(self.tableTests)
        if item:
            # Journal.log('*********************************************************')
            Journal.log('***' * 30)
            Journal.log(__name__, "::\t", __doc__, "-->",
                        item['ID'] if item else "None")
            funcs_combo.filters_reset(self)
            funcs_group.group_clear(self.groupTestInfo)
            funcs_group.group_clear(self.groupPumpInfo)
            self._data_manager.clear_record()
            funcs_display.display_test(self, self._data_manager, item['ID'])
            funcs_display.display_test_deltas(self, self._graph_manager)
            Journal.log('===' * 30)

    def on_menu_testlist(self):
        """ создание контекстрого меню и обработка """
        menu = QMenu()
        print_action = menu.addAction("Распечатать")
        action = menu.exec_(QCursor.pos())
        if action == print_action:
            self._report.generate_report()

    def on_changed_column_testlist(self):
        """ изменён столбец списка тестов """
        Journal.log(__name__, "::\t", __doc__)
        funcs_testlist.filter_switch(self)

    def on_changed_combo_producers(self, index):
        """ изменение выбора производителя """
        item = self.cmbProducer.currentData(Qt.UserRole)
        if item:
            Journal.log(__name__, "::\t", __doc__, "-->",
                        item['Name'] if item else "None")
            # ↓ фильтрует типоразмеры для данного производителя
            condition = {'Producer': item['ID']} if index else None
            if not self.cmbType.model().check_selected(condition):
                self.cmbType.model().applyFilter(condition)

    def on_changed_combo_types(self, index):
        """ изменение выбора типоразмера """
        item = self.cmbType.currentData(Qt.UserRole)
        if item:
            Journal.log(__name__, "::\t", __doc__, "-->",
                        item['Name'] if item else "None")
            # ↑ выбирает производителя для данного типоразмера
            condition = {'ID': item['Producer']} if index else None
            if not self.cmbProducer.model().check_selected(condition) and index:
                self.cmbProducer.model().select_contains(condition)
            # ↓ фильтрует серийники для данного типоразмера
            condition = {'Type': item['ID']} if index else None
            if not self.cmbSerial.model().check_selected(condition):
                self.cmbSerial.model().applyFilter(condition)

    def on_changed_combo_serials(self, index):
        """ изменение выбора заводского номера """
        item = self.cmbSerial.currentData(Qt.UserRole)
        if item:
            Journal.log(__name__, "::\t", __doc__, "-->",
                        item['Serial'] if item else "None")
            # ↑ выбирает типоразмер для данного серийника
            condition = {'ID': item['Type']} if index else None
            if not self.cmbType.model().check_selected(condition) and index:
                self.cmbType.model().select_contains(condition)
            self._graph_manager.draw_charts(self.frameGraphInfo)

    def on_changed_filter_apply(self, text: str):
        """ изменён значение фильтра списка тестов """
        if text:
            Journal.log(__name__, "::\t", __doc__, "-->", text)
        funcs_testlist.filter_apply(self)

    def on_clicked_filter_reset(self):
        """ нажата кнопка сброса фильтра """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        funcs_testlist.filter_reset(self, self._data_manager)
        funcs_group.group_lock(self.groupTestInfo, True)
        funcs_group.group_lock(self.groupPumpInfo, True)

    def on_clicked_pump_new(self):
        """ нажата кнопка добавления нового насоса """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        funcs_group.group_lock(self.groupPumpInfo, False)
        funcs_group.group_clear(self.groupPumpInfo)


    def on_clicked_pump_save(self):
        """ нажата кнопка сохранения нового насоса """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        pump_id, do_select = self._data_manager.check_exists_serial(
            self.cmbSerial.currentText()
        )
        pump_data = self._testdata.pump_
        if do_select:
            funcs_display.display_pump(self, pump_data)
        if not pump_id and funcs_group.group_check(self.groupPumpInfo):
            funcs_group.group_save(self.groupPumpInfo, pump_data)
            funcs_group.group_lock(self.groupPumpInfo, True)
            if self._data_manager.save_pump_info():
                funcs_combo.fill_combos_pump(self, self._data_manager)
                self.cmbSerial.model().select_contains(pump_data.ID)

    def on_clicked_pump_cancel(self):
        """ нажата кнопка отмены добавления нового насоса """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        # self._wnd.display_record()
        funcs_combo.filters_reset(self)
        funcs_group.group_display(
            self.groupPumpInfo, self._testdata.pump_)
        funcs_group.group_lock(self.groupPumpInfo, True)

    def on_clicked_test_new(self):
        """ нажата кнопка добавления нового теста """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        funcs_group.group_lock(self.groupTestInfo, False)
        funcs_group.group_clear(self.groupTestInfo)
        funcs_aux.set_current_date(self)

    def on_clicked_test_info_save(self):
        """ нажата кнопка сохранения нового теста """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        test_id, choice = self._data_manager.check_exists_ordernum(
            self.txtOrderNum.text(), with_select=True
        )
        if choice != 2:
            funcs_testlist.select_test(self, test_id['ID'])
            if choice == 1:
                funcs_aux.set_current_date(self)
        if not test_id and funcs_group.group_check(self.groupTestInfo):
            self._data_manager.clear_test_info()
            funcs_group.group_save(self.groupTestInfo, self._test_data.test_)
            funcs_group.group_lock(self.groupTestInfo, True)
            self._data_manager.save_test_info()
            funcs_testlist.fill(self, self._data_manager)

    def on_clicked_test_info_cancel(self):
        """ нажата кнопка отмены добавления нового теста """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        funcs_group.group_display(self.groupTestInfo, self._testdata.test_)
        funcs_group.group_lock(self.groupTestInfo, True)

    def on_clicked_test_result_save(self):
        """ нажата кнопка сохранения результатов теста """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        title = 'УСПЕХ'
        message = 'Результаты сохранены'
        self._graph_manager.save_test_data()
        if not self._testdata.test_.save():
            title = 'ОШИБКА'
            message = 'Запись заблокирована'
        Message.show(title, message)

    def on_clicked_save(self):
        """ нажата кнопка сохранения """
        # self._parent.__store_record()

    def on_clicked_go_test(self):
        """ нажата кнопка перехода к тестированию """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        self.stackedWidget.setCurrentIndex(1)
        self._graph_manager.display_charts(self.frameGraphTest)
        self._graph_manager.markers_reposition()

    def on_clicked_go_back(self):
        """ нажата кнопка возврата на основное окно """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        self.stackedWidget.setCurrentIndex(0)
        funcs_testlist.select_test(self, self._testdata.test_['ID'])

    def on_clicked_test(self):
        """ нажата кнопка начала/остановки испытания """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        Test.is_running = not Test.is_running
        self._graph_manager.switch_charts_visibility(Test.is_running)
        Test.switch_running_state(self, Test.is_running)

    def on_clicked_add_point(self):
        """ нажата кнопка добавления точки """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        current_vals = Test.get_current_vals(self)
        funcs_table_points.add(self, *current_vals)
        self._graph_manager.markers_add_knots()
        self._graph_manager.add_points_to_charts(*current_vals)
        self._graph_manager.display_charts(self.frameGraphTest)

    def on_clicked_remove_point(self):
        """ нажата кнопка удаления точки """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        funcs_table_points.remove_last(self)
        self._graph_manager.markers_remove_knots()
        self._graph_manager.remove_last_points_from_charts()
        self._graph_manager.display_charts(self.frameGraphTest)

    def on_changed_points_mode(self):
        """ переключение значений точек реальные / на ступень """
        Test.switch_points_stages_real(self, self._testdata)

    def on_clicked_clear_curve(self):
        """ нажата кнопка удаления всех точек """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        funcs_table.clear(self.tablePoints)
        self._graph_manager.markers_clear_knots()
        self._graph_manager.clear_points_from_charts()
        self._graph_manager.display_charts(self.frameGraphTest)

    def on_clicked_adam_connection(self):
        """ нажата кнопка подключения к ADAM5000TCP """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", __doc__)
        state = self._adam.changeConnectionState()
        self.checkConnection.setChecked(state)
        self.checkConnection.setText("подключено" if state else "отключено")

    def on_adam_data_received(self, sensors: dict):
        """ приход данных от ADAM5000TCP """
        Journal.log(__name__, "::\t", __doc__)
        point_data = {key: sensors[key] for key
                    in ['rpm', 'torque', 'pressure_in', 'pressure_out']}
        point_data['flw'] = sensors[self._active_flowmeter]
        funcs_display.display_sensors(self, sensors)

    def on_changed_sensors(self):
        """ изменения значений датчиков """
        vals = Test.get_current_vals(self)
        params = [
            {'name': 'test_lft', 'x': vals[0], 'y': vals[1]},
            {'name': 'test_pwr', 'x': vals[0], 'y': vals[2]}
        ]
        self._graph_manager.markers_move(params)

    def on_markers_move(self, point_data: dict):
        """ изменения позиции маркеров """
        funcs_display.display_current_marker_point(self, point_data)

    def on_mouse_wheel_flow(self, event):
        """ изменяет значение расхода колесиком мышки """
        funcs_aux.process_mouse_wheel(
            self.txtFlow, event, 1)

    def on_mouse_wheel_lift(self, event):
        """ изменяет значение напора колесиком мышки """
        funcs_aux.process_mouse_wheel(
            self.txtLift, event, 0.1)

    def on_mouse_wheel_power(self, event):
        """ изменяет значение мощности колесиком мышки """
        funcs_aux.process_mouse_wheel(
            self.txtPower, event, 0.001)
