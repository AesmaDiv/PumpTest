"""
    Модуль содержит функции основного окна программы
"""
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMenu
from PyQt5.QtGui import QCursor, QCloseEvent
from Classes.Adam import adam_config as adam

from Classes.UI import funcs_table, funcs_table_points, funcs_table_vibr
from Classes.UI import funcs_testlist, funcs_combo, funcs_group, funcs_display
from Classes.UI import funcs_aux, funcs_test
from Classes.Data.report import Report
from Classes.Data.data_manager import DataManager
from Classes.Graph.graph_manager import GraphManager
from Classes.Adam.adam_manager import AdamManager

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
        self._data_manager = DataManager(pathes['DB'])
        self._testdata = self._data_manager.get_testdata()
        self._graph_manager = GraphManager(self._testdata)
        self._adam_manager = AdamManager(adam.IP, adam.PORT, adam.ADDRESS)
        self._report = Report(pathes['TEMPLATE'], self._graph_manager, self._testdata)

    @Journal.logged
    def show(self):
        """ отображает главное окно """
        self._prepare()
        super().show()
        self.move(1, 1)
        funcs_test.switch_running_state(self, self._adam_manager, False)

    def closeEvent(self, a0: QCloseEvent) -> None:
        """ погдотовка к закрытию приложения """
        self._adam_manager.disconnect()
        # print("main window prepared for closing")
        return super().closeEvent(a0)

    @Journal.logged
    def set_color_scheme(self):
        """ устанавливает цветовую схему """
        # gvars.wnd_main.stackedWidget.setStyleSheet("QStackedWidget { background: #404040; }")
        # style: str = "QComboBox { color: #ffffff; }" \
        #              "QComboBox:!editable { color: #dddddd; }"
        # gvars.wnd_main.groupTestInfo.setStyleSheet(style)
        # gvars.wnd_main.groupPumpInfo.setStyleSheet(style)

    @Journal.logged
    def _prepare(self):
        """ инициализирует и подготавливает компоненты главного окна """
        funcs_testlist.init(self)
        funcs_testlist.refresh(self, self._data_manager)
        funcs_testlist.filter_switch(self)
        funcs_combo.fill_combos(self, self._data_manager)
        funcs_test.prepare_sliders_range(self)
        funcs_table_points.init(self)
        funcs_table_vibr.init(self)
        self.set_color_scheme()
        self._register_events()
        self._init_markers()
        funcs_group.group_lock(self.groupTestInfo, True)
        funcs_group.group_lock(self.groupPumpInfo, True)

    @Journal.logged
    def _register_events(self):
        """ привязывает события элементов формы к обработчикам """
        self.tableTests.selectionModel().currentChanged.connect(self.on_changed_testlist)
        self.tableTests.customContextMenuRequested.connect(self.on_menu_testlist)
        #
        self.txtFilter_ID.textChanged.connect(self.on_changed_filter_apply)
        self.txtFilter_DateTime.textChanged.connect(self.on_changed_filter_apply)
        self.txtFilter_OrderNum.textChanged.connect(self.on_changed_filter_apply)
        self.txtFilter_Serial.textChanged.connect(self.on_changed_filter_apply)
        self.btnFilterReset.clicked.connect(self.on_clicked_filter_reset)
        self.radioOrderNum.toggled.connect(self.on_changed_column_testlist)
        #
        self.cmbProducer.currentIndexChanged.connect(self.on_changed_combo_producers)
        self.cmbType.currentIndexChanged.connect(self.on_changed_combo_types)
        self.cmbSerial.currentIndexChanged.connect(self.on_changed_combo_serials)
        #
        self.btnTest_New.clicked.connect(self.on_clicked_test_info_new)
        self.btnTest_Save.clicked.connect(self.on_clicked_test_info_save)
        self.btnTest_Cancel.clicked.connect(self.on_clicked_test_info_cancel)
        #
        self.btnPump_New.clicked.connect(self.on_clicked_pump_info_new)
        self.btnPump_Save.clicked.connect(self.on_clicked_pump_info_save)
        self.btnPump_Cancel.clicked.connect(self.on_clicked_pump_info_cancel)
        #
        self.btnGoTest.clicked.connect(self.on_clicked_go_test)
        self.btnGoBack.clicked.connect(self.on_clicked_go_back)
        #
        self.txtFlow.textChanged.connect(self.on_changed_sensors)
        self.txtLift.textChanged.connect(self.on_changed_sensors)
        self.txtPower.textChanged.connect(self.on_changed_sensors)
        #
        self.btnAddPoint.clicked.connect(self.on_clicked_add_point)
        self.btnRemovePoint.clicked.connect(self.on_clicked_remove_point)
        self.btnClearCurve.clicked.connect(self.on_clicked_clear_curve)
        self.btnSaveCharts.clicked.connect(self.on_clicked_test_result_save)
        #
        self.radioPointsReal.toggled.connect(self.on_changed_points_mode)
        # gvars.markers.eventMove.connect(self.on_markers_move)
        self.txtFlow.wheelEvent = self.on_mouse_wheel_flow
        self.txtLift.wheelEvent = self.on_mouse_wheel_lift
        self.txtPower.wheelEvent = self.on_mouse_wheel_power
        #
        self.checkConnection.clicked.connect(self.on_clicked_adam_connection)
        self.btnEngine.clicked.connect(self.on_clicked_engine)
        self.sliderPressure.sliderReleased.connect(self.on_changed_pressure)
        self.sliderSpeed.sliderReleased.connect(self.on_changed_speed)
        self.radioFlow0.toggled.connect(self.on_changed_flowmeter)
        self.radioFlow1.toggled.connect(self.on_changed_flowmeter)
        self.radioFlow2.toggled.connect(self.on_changed_flowmeter)
        self._adam_manager.data_received().connect(self.on_adam_data_received)

    def _init_markers(self):
        """ инициирует маркеры графика испытания """
        params = {
            'test_lft': Qt.blue,
            'test_pwr': Qt.red
        }
        self._graph_manager.init_markers(params, self.gridGraphTest)

    def on_changed_testlist(self):
        """ изменение выбора теста """
        item = funcs_table.get_row(self.tableTests)
        if item:
            # если запись уже выбрана и загружена - выходим
            if self._testdata.test_.ID == item['ID']:
                return
            Journal.log('***' * 30)
            Journal.log_func(self.on_changed_testlist, item['ID'])
            # очищаем фильтры, поля и информацию о записи
            funcs_combo.filters_reset(self)
            funcs_group.group_clear(self.groupTestInfo)
            funcs_group.group_clear(self.groupPumpInfo)
            self._data_manager.clear_record()
            # загружаем и отображаем информацию о выбранной записи
            if self._data_manager.load_record(item['ID']):
                funcs_display.display_record(self, self._data_manager)
                funcs_display.display_test_deltas(self, self._graph_manager)
            Journal.log('===' * 30)

    def on_menu_testlist(self):
        """ создание контекстрого меню и обработка """
        menu = QMenu()
        action_print = menu.addAction("Распечатать")
        action_remove = menu.addAction("Удалить")
        action_rewrite = menu.addAction("Переписать")
        action = menu.exec_(QCursor.pos())
        # печать протокола
        if action == action_print:
            self._report.generate_report()
        # удаление записи
        elif action == action_remove:
            if funcs_aux.ask_password():
                self._data_manager.remove_current_record()
                funcs_testlist.refresh(self, self._data_manager)
        # обновление записи
        elif action == action_rewrite:
            if funcs_aux.ask_password():
                self._data_manager.save_test_info()

    def on_changed_column_testlist(self):
        """ изменён столбец списка тестов (наряд-заказ/серийный номер) """
        Journal.log_func(self.on_changed_column_testlist)
        funcs_testlist.filter_switch(self)

    def on_changed_combo_producers(self, index):
        """ выбор производителя """
        item = self.cmbProducer.itemData(index, Qt.UserRole)
        if item:
            Journal.log_func(self.on_changed_combo_producers, item['Name'] if item else "None")
            # ↓ фильтрует типоразмеры для данного производителя
            condition = {'Producer': item['ID']} if index else None
            if not self.cmbType.model().check_already_selected(condition):
                self.cmbType.model().applyFilter(condition)

    def on_changed_combo_types(self, index):
        """ выбор типоразмера """
        item = self.cmbType.itemData(index, Qt.UserRole)
        Journal.log_func(self.on_changed_combo_types , "None" if not item else item['Name'])
        if item and all(item.values()):
            # ↑ выбирает производителя для данного типоразмера
            condition = {'ID': item['Producer']} if index else None
            if not self.cmbProducer.model().check_already_selected(condition) and index:
                self.cmbProducer.model().select_contains(condition)
            # ↓ фильтрует серийники для данного типоразмера
            condition = {'Type': item['ID']} if index else None
            if not self.cmbSerial.model().check_already_selected(condition):
                self.cmbSerial.model().applyFilter(condition)
            # перерисовывает эталонный график
            self._data_manager.get_testdata().type_.read(item['ID'])
            self._graph_manager.draw_charts(self.frameGraphInfo)

    def on_changed_combo_serials(self, index):
        """ выбор заводского номера """
        item = self.cmbSerial.itemData(index, Qt.UserRole)
        if item:
            Journal.log_func(self.on_changed_combo_serials, item['Serial'] if item else "None")
            # ↑ выбирает типоразмер для данного серийника
            funcs_combo.select_contains(self.cmbType, {'ID': item['Type']})
            self._graph_manager.draw_charts(self.frameGraphInfo)

    def on_changed_filter_apply(self, text: str):
        """ изменение значения фильтра списка тестов """
        if text:
            Journal.log_func(self.on_changed_filter_apply, text)
        funcs_testlist.filter_apply(self)

    def on_clicked_filter_reset(self):
        """ нажата кнопка сброса фильтра """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_filter_reset)
        funcs_testlist.filter_reset(self, self._data_manager)
        funcs_group.group_lock(self.groupTestInfo, True)
        funcs_group.group_lock(self.groupPumpInfo, True)

    def on_clicked_pump_info_new(self):
        """ нажата кнопка добавления нового насоса """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_pump_info_new)
        funcs_group.group_lock(self.groupPumpInfo, False)
        funcs_group.group_clear(self.groupPumpInfo)

    def on_clicked_pump_info_save(self):
        """ нажата кнопка сохранения нового насоса """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_pump_info_save)
        # проверяем есть ли такой серийник в базе
        pump_id, do_select = self._data_manager.check_exists_serial(
            self.cmbSerial.currentText()
        )
        # если есть - выбираем
        if pump_id and do_select:
            self._testdata.test_['Pump'] = pump_id
            funcs_display.display_pump_info(self, self._testdata)
        # проверяем заполение полей и сохраняем
        elif funcs_group.group_check(self.groupPumpInfo):
            pump_info = self._testdata.pump_
            funcs_group.group_lock(self.groupPumpInfo, True)
            funcs_group.group_save(self.groupPumpInfo, pump_info)
            if self._data_manager.save_pump_info():
                funcs_combo.fill_combos_pump(self, self._data_manager)
                self.cmbSerial.model().select_contains(pump_info.ID)

    def on_clicked_pump_info_cancel(self):
        """ нажата кнопка отмены добавления нового насоса """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_pump_info_cancel)
        funcs_combo.filters_reset(self)
        funcs_group.group_display(self.groupPumpInfo, self._testdata.pump_)
        funcs_group.group_lock(self.groupPumpInfo, True)

    def on_clicked_test_info_new(self):
        """ нажата кнопка добавления нового теста """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_test_info_new)
        funcs_group.group_clear(self.groupTestInfo)
        funcs_group.group_lock(self.groupTestInfo, False)
        funcs_aux.set_current_date(self)

    def on_clicked_test_info_save(self):
        """ нажата кнопка сохранения нового теста """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_test_info_save)
        # проверяем есть ли такой наряд-заказ в БД
        test_id, choice = self._data_manager.check_exists_ordernum(
            self.txtOrderNum.text(), with_select=True
        )
        # если есть - выбираем
        if choice != 2:
            funcs_testlist.select_test(self, test_id)
            if choice == 1:
                funcs_aux.set_current_date(self)
        # сохраняем новый тест
        if not test_id and funcs_group.group_check(self.groupTestInfo):
            self._data_manager.clear_test_info()
            funcs_group.group_save(self.groupTestInfo, self._testdata.test_)
            funcs_group.group_lock(self.groupTestInfo, True)
            self._data_manager.save_test_info()
            funcs_testlist.refresh(self, self._data_manager)

    def on_clicked_test_info_cancel(self):
        """ нажата кнопка отмены добавления нового теста """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_test_info_cancel)
        funcs_group.group_display(self.groupTestInfo, self._testdata.test_)
        funcs_group.group_lock(self.groupTestInfo, True)

    def on_clicked_test_result_save(self):
        """ нажата кнопка сохранения результатов теста """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_test_result_save)
        self._graph_manager.save_testdata()
        result = self._testdata.test_.write()
        title = 'УСПЕХ' if result else 'ОШИБКА'
        message = 'Результаты сохранены' if result else 'Запись заблокирована'
        Message.show(title, message)

    def on_clicked_save(self):
        """ нажата кнопка сохранения """
        # self._parent.__store_record()

    def on_clicked_go_test(self):
        """ нажата кнопка перехода к тестированию """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_go_test)
        self.stackedWidget.setCurrentIndex(1)
        self._graph_manager.display_charts(self.frameGraphTest)
        self._graph_manager.markers_reposition()

    def on_clicked_go_back(self):
        """ нажата кнопка возврата на основное окно """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_go_back)
        self.stackedWidget.setCurrentIndex(0)
        self._graph_manager.display_charts(self.frameGraphInfo)
        funcs_testlist.select_test(self, self._testdata.test_['ID'])

    def on_clicked_engine(self):
        """ нажата кнопка начала/остановки испытания """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_engine)
        state = not funcs_test.states["is_running"]
        self._graph_manager.switch_charts_visibility(state)
        funcs_test.switch_running_state(self, self._adam_manager, state)

    def on_clicked_add_point(self):
        """ нажата кнопка добавления точки """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_add_point)
        current_vals = funcs_test.get_current_vals(self)
        funcs_table_points.add(self, *current_vals)
        self._graph_manager.markers_add_knots()
        self._graph_manager.add_points_to_charts(*current_vals)
        self._graph_manager.display_charts(self.frameGraphTest)

    def on_clicked_remove_point(self):
        """ нажата кнопка удаления точки """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_remove_point)
        funcs_table_points.remove_last(self)
        self._graph_manager.markers_remove_knots()
        self._graph_manager.remove_last_points_from_charts()
        self._graph_manager.display_charts(self.frameGraphTest)

    def on_changed_points_mode(self):
        """ переключение значений точек реальные / на ступень """
        funcs_test.switch_points_stages_real(self, self._testdata)

    def on_clicked_clear_curve(self):
        """ нажата кнопка удаления всех точек """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_clear_curve)
        funcs_table.clear(self.tablePoints)
        self._graph_manager.markers_clear_knots()
        self._graph_manager.clear_points_from_charts()
        self._graph_manager.display_charts(self.frameGraphTest)

    def on_clicked_adam_connection(self):
        """ нажата кнопка подключения к ADAM5000TCP """
        Journal.log('___' * 30)
        Journal.log_func(self.on_clicked_adam_connection)
        state = self.checkConnection.isChecked()
        state = funcs_test.switch_connection(self._adam_manager, state)
        self.checkConnection.setChecked(state)
        self.checkConnection.setText("подключено" if state else "отключено")

    def on_adam_data_received(self, sensors: dict):
        """ приход данных от ADAM5000TCP """
        # Journal.log_func(self.on_adam_data_received)
        point_data = {key: sensors[key] for key
                    in ['rpm', 'torque', 'pressure_in', 'pressure_out']}
        # point_data['flw'] = sensors[self._active_flowmeter]
        funcs_display.display_sensors(self, sensors)

    def on_changed_pressure(self):
        """ изменение положение задвижки """
        funcs_test.change_flow_valve(self, self._adam_manager)

    def on_changed_speed(self):
        """ изменение скорости вращения двигателя """
        funcs_test.change_engine_rpm(self, self._adam_manager)

    def on_changed_flowmeter(self):
        """ изменение текущего расходомера """
        Journal.log_func(self.on_changed_flowmeter)
        funcs_test.switch_active_flowmeter(self)

    def on_changed_sensors(self):
        """ изменения значений датчиков """
        vals = funcs_test.get_current_vals(self)
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
