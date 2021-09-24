"""
    Модуль содержащий функции обработки событий
"""
from Classes.combo_manager import ComboManager
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu

from Functions import funcs_temp
from Functions import funcsAdam
from AesmaLib.journal import Journal
from Classes.table_manager import TableManager
from Classes.message import Message


class EventManager:
    def __init__(self, parent) -> None:
        self._wnd_m = parent
        self._gf_m = parent._gf_m
        self._wnd = parent._wnd
        self._markers = self._gf_m.markers()
        self._info = parent._info
        self._report = parent._rprt
        self._active_flowmeter = 'flw2'
        self._test_is_running = False

    @Journal.logged
    def register_events(self):
        """ привязывает события элементов формы к обработчикам """
        wnd = self._wnd
        wnd.tableTests.selectionModel().currentChanged.connect(self.on_changed_testlist)
        wnd.tableTests.customContextMenuRequested.connect(self.on_menu_testlist)

        wnd.cmbProducer.currentIndexChanged.connect(self.on_changed_combo_producers)
        wnd.cmbType.currentIndexChanged.connect(self.on_changed_combo_types)
        wnd.cmbSerial.currentIndexChanged.connect(self.on_changed_combo_serials)

        wnd.btnTest.clicked.connect(self.on_clicked_test)
        wnd.btnTest_New.clicked.connect(self.on_clicked_test_new)
        wnd.btnTest_Save.clicked.connect(self.on_clicked_test_info_save)
        wnd.btnTest_Cancel.clicked.connect(self.on_clicked_test_info_cancel)

        wnd.btnPump_New.clicked.connect(self.on_clicked_pump_new)
        wnd.btnPump_Save.clicked.connect(self.on_clicked_pump_save)
        wnd.btnPump_Cancel.clicked.connect(self.on_clicked_pump_cancel)

        wnd.btnFilterReset.clicked.connect(self.on_clicked_filter_reset)

        wnd.txtFilter_ID.textChanged.connect(self.on_changed_filter_apply)
        wnd.txtFilter_DateTime.textChanged.connect(self.on_changed_filter_apply)
        wnd.txtFilter_OrderNum.textChanged.connect(self.on_changed_filter_apply)
        wnd.txtFilter_Serial.textChanged.connect(self.on_changed_filter_apply)

        wnd.radioOrderNum.toggled.connect(self.on_changed_testlist_column)

        wnd.btnGoTest.clicked.connect(self.on_clicked_go_test)
        wnd.btnGoBack.clicked.connect(self.on_clicked_go_back)

        wnd.txtFlow.textChanged.connect(self.on_changed_sensors)
        wnd.txtLift.textChanged.connect(self.on_changed_sensors)
        wnd.txtPower.textChanged.connect(self.on_changed_sensors)

        wnd.btnAddPoint.clicked.connect(self.on_clicked_add_point)
        wnd.btnRemovePoint.clicked.connect(self.on_clicked_remove_point)
        wnd.btnClearCurve.clicked.connect(self.on_clicked_clear_curve)
        wnd.btnSaveCharts.clicked.connect(self.on_clicked_test_data_save)

        wnd.checkConnection.clicked.connect(self.on_clicked_adam_connection)
        funcsAdam.broadcaster.event.connect(self.on_adam_data_received)

        wnd.radioPointsReal.toggled.connect(self.on_changed_points_mode)
        # gvars.markers.eventMove.connect(self.on_markers_move)
        wnd.txtFlow.wheelEvent = self.on_mouse_wheel_flow
        wnd.txtLift.wheelEvent = self.on_mouse_wheel_lift
        wnd.txtPower.wheelEvent = self.on_mouse_wheel_power

    def on_changed_testlist(self):
        """ изменение выбора теста """
        item = TableManager.get_row(self._wnd.tableTests)
        if item:
            # Journal.log('*********************************************************')
            Journal.log('***' * 30)
            Journal.log(__name__, "::\t", self.on_changed_testlist.__doc__, "-->",
                        item['ID'] if item else "None")
            ComboManager.filters_reset(self._wnd)
            self._wnd_m.clear_record(True)
            self._wnd_m.display_test(item['ID'])
            self._wnd_m.display_test_deltas()
            Journal.log('===' * 30)


    def on_menu_testlist(self):
        """ создание контекстрого меню и обработка """
        menu = QMenu()
        print_action = menu.addAction("Распечатать")
        action = menu.exec_(QtGui.QCursor.pos())
        if action == print_action:
            self._report.generate_report()


    def on_changed_combo_producers(self, index):
        """ изменение выбора производителя """
        item = self._wnd.cmbProducer.currentData(Qt.UserRole)
        if item:
            Journal.log(__name__, "::\t", self.on_changed_combo_producers.__doc__, "-->",
                        item['Name'] if item else "None")
            # ↓ фильтрует типоразмеры для данного производителя
            condition = {'Producer': item['ID']} if index else None
            if not self._wnd.cmbType.model().check_selected(condition):
                self._wnd.cmbType.model().applyFilter(condition)


    def on_changed_combo_types(self, index):
        """ изменение выбора типоразмера """
        wnd = self._wnd
        item = wnd.cmbType.currentData(Qt.UserRole)
        if item:
            Journal.log(__name__, "::\t", self.on_changed_combo_types.__doc__, "-->",
                        item['Name'] if item else "None")
            # ↑ выбирает производителя для данного типоразмера
            condition = {'ID': item['Producer']} if index else None
            if not wnd.cmbProducer.model().check_selected(condition) and index:
                wnd.cmbProducer.model().select_contains(condition)
            # ↓ фильтрует серийники для данного типоразмера
            condition = {'Type': item['ID']} if index else None
            if not wnd.cmbSerial.model().check_selected(condition):
                wnd.cmbSerial.model().applyFilter(condition)


    def on_changed_combo_serials(self, index):
        """ изменение выбора заводского номера """
        wnd = self._wnd
        item = wnd.cmbSerial.currentData(Qt.UserRole)
        if item:
            Journal.log(__name__, "::\t", self.on_changed_combo_serials.__doc__, "-->",
                        item['Serial'] if item else "None")
            # ↑ выбирает типоразмер для данного серийника
            condition = {'ID': item['Type']} if index else None
            if not wnd.cmbType.model().check_selected(condition) and index:
                wnd.cmbType.model().select_contains(condition)
            self._gf_m.draw_charts(wnd.frameGraphInfo)


    def on_changed_testlist_column(self):
        """ изменён столбец списка тестов """
        Journal.log(__name__, "::\t", self.on_changed_testlist_column.__doc__)
        self._wnd_m.testlist_filter_switch()


    def on_changed_filter_apply(self, text: str):
        """ изменён значение фильтра списка тестов """
        if text:
            Journal.log(__name__, "::\t", self.on_changed_filter_apply.__doc__, "-->",
                        text)
        self._wnd_m.testlist_filter_apply()


    def on_clicked_filter_reset(self):
        """ нажата кнопка сброса фильтра """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_filter_reset.__doc__)
        self._wnd_m.testlist_filter_reset()
        self._wnd_m.group_lock(self._wnd.groupTestInfo, True)
        self._wnd_m.group_lock(self._wnd.groupPumpInfo, True)


    def on_clicked_pump_new(self):
        """ нажата кнопка добавления нового насоса """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_pump_new.__doc__)
        self._wnd_m.group_lock(self._wnd.groupPumpInfo, False)
        self._wnd_m.group_clear(self._wnd.groupPumpInfo)


    def on_clicked_pump_save(self):
        """ нажата кнопка сохранения нового насоса """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_pump_save.__doc__)
        pump_id, do_select = self._wnd_m.funcs.check_exists_serial()
        if do_select:
            self._wnd_m.display_pump(pump_id)
        if not pump_id and self._wnd_m.group_check(self._wnd.groupPumpInfo):
            if self._wnd_m.save_pump_info():
                self._wnd_m.fill_combos_pump()
                self._wnd.cmbSerial.model().select_contains(self._info.pump_.ID)


    def on_clicked_pump_cancel(self):
        """ нажата кнопка отмены добавления нового насоса """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_pump_cancel.__doc__)
        wnd = self._wnd
        # self._wnd_m.display_record()
        self._wnd_m.combos_filters_reset()
        self._wnd_m.group_display(wnd.groupPumpInfo, self._info.pump_)
        self._wnd_m.group_lock(wnd.groupPumpInfo, True)


    def on_clicked_test_new(self):
        """ нажата кнопка добавления нового теста """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_test_new.__doc__)
        wnd = self._wnd
        self._wnd_m.group_lock(wnd.groupTestInfo, False)
        self._wnd_m.group_clear(wnd.groupTestInfo)
        self._wnd_m.funcs.set_current_date()


    def on_clicked_test_info_save(self):
        """ нажата кнопка сохранения нового теста """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_test_info_save.__doc__)
        test_id = self._wnd_m.funcs.check_exists_ordernum(with_select=True)
        if not test_id and self._wnd_m.group_check(self._wnd.groupTestInfo):
            self._wnd_m.save_test_info()
            self._wnd_m.fill_test_list()


    def on_clicked_test_info_cancel(self):
        """ нажата кнопка отмены добавления нового теста """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_test_info_cancel.__doc__)
        wnd = self._wnd
        self._wnd_m.group_display(wnd.groupTestInfo, self._info.test_)
        self._wnd_m.group_lock(wnd.groupTestInfo, True)


    def on_clicked_test_data_save(self):
        """ нажата кнопка сохранения результатов теста """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_test_data_save.__doc__)
        title = 'УСПЕХ'
        message = 'Результаты сохранены'
        self._gf_m.save_test_data()
        if not self._info.test_.save():
            title = 'ОШИБКА'
            message = 'Запись заблокирована'
        Message.show(title, message)


    def on_clicked_save(self):
        """ нажата кнопка сохранения """
        # self._parent.__store_record()


    def on_clicked_go_test(self):
        """ нажата кнопка перехода к тестированию """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_go_test.__doc__)
        self._wnd.stackedWidget.setCurrentIndex(1)
        self._gf_m.display_charts(self._markers)
        self._markers.repositionFor(self._gf_m)


    def on_clicked_go_back(self):
        """ нажата кнопка возврата на основное окно """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_go_back.__doc__)
        self._wnd.stackedWidget.setCurrentIndex(0)
        self._wnd_m.funcs.select_test(self._info.test_['ID'])


    def on_clicked_test(self):
        """ нажата кнопка начала/остановки испытания """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_test.__doc__)
        self._test_is_running = not self._test_is_running
        self._gf_m.switch_charts_visibility(self._test_is_running)
        self._wnd_m.switch_test_running_state(self._test_is_running)


    def on_clicked_add_point(self):
        """ нажата кнопка добавления точки """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_add_point.__doc__)
        self._markers.addKnots()
        current_vals = self._wnd_m.get_current_vals()
        self._wnd_m.add_point_to_table(*current_vals)
        self._gf_m.add_points_to_charts(*current_vals)
        self._gf_m.display_charts(self._markers)


    def on_clicked_remove_point(self):
        """ нажата кнопка удаления точки """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_remove_point.__doc__)
        self._markers.removeKnots()
        self._wnd_m.remove_last_point_from_table()
        self._gf_m.remove_last_points_from_charts()
        self._gf_m.display_charts(self._markers)


    def on_changed_points_mode(self):
        self._wnd_m.switch_points_stages_real()


    def on_clicked_clear_curve(self):
        """ нажата кнопка удаления всех точек """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_clear_curve.__doc__)
        self._markers.clearAllKnots()
        self._wnd_m.clear_points_from_table(self._wnd.tablePoints)
        self._gf_m.clear_points_from_charts()
        self._gf_m.display_charts(self._markers)


    def on_clicked_adam_connection(self):
        """ нажата кнопка подключения к ADAM5000TCP """
        Journal.log('___' * 30)
        Journal.log(__name__, "::\t", self.on_clicked_adam_connection.__doc__)
        state = funcsAdam.changeConnectionState()
        self._wnd.checkConnection.setChecked(state)
        self._wnd.checkConnection.setText("подключено" if state else "отключено")


    def on_adam_data_received(self, sensors: dict):
        """ приход данных от ADAM5000TCP """
        Journal.log(__name__, "::\t", self.on_adam_data_received.__doc__)
        point_data = {key: sensors[key] for key 
                    in ['rpm', 'torque', 'pressure_in', 'pressure_out']}
        point_data['flw'] = sensors[self._active_flowmeter]
        self._wnd_m.display_sensors(sensors)


    def on_changed_sensors(self):
        """ изменения значений датчиков """
        vals = self._wnd_m.get_current_vals()
        self._gf_m.move_markers(vals)


    def on_markers_move(self, point_data: dict):
        """ изменения позиции маркеров """
        self._wnd_m.display_current_marker_point(point_data)


    def on_mouse_wheel_flow(self, event):
        """ изменяет значение расхода колесиком мышки """
        funcs_temp.process_mouse_wheel(
            self._wnd.txtFlow, event, 1)


    def on_mouse_wheel_lift(self, event):
        """ изменяет значение напора колесиком мышки """
        funcs_temp.process_mouse_wheel(
            self._wnd.txtLift, event, 0.1)


    def on_mouse_wheel_power(self, event):
        """ изменяет значение мощности колесиком мышки """
        funcs_temp.process_mouse_wheel(
            self._wnd.txtPower, event, 0.001)
