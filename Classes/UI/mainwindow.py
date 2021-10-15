"""
    Модуль содержит функции основного окна программы
"""
import os
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMenu
from PyQt5.QtGui import QCursor, QCloseEvent
from Classes.Adam import adam_config as adam
from Classes.UI import funcs_table, funcs_testlist, funcs_combo, funcs_group
from Classes.UI import funcs_aux, funcs_test, funcs_display
from Classes.Data.report import Report
from Classes.Data.data_manager import DataManager
from Classes.Graph.graph_manager import GraphManager
from Classes.Adam.adam_manager import AdamManager

from AesmaLib.message import Message
from AesmaLib.journal import Journal


class MainWindow(QMainWindow):
    """ Класс описания функционала главного окна приложения """
    def __init__(self, paths, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._is_ready = self._createGUI(paths['WND'])
        if self._is_ready:
            self._is_displaying = dict.fromkeys(
                ['Producer','Type','Serial'], False
            )
            self._data_manager = DataManager(paths['DB'])
            self._testdata = self._data_manager.getTestdata()
            self._graph_manager = GraphManager(self._testdata)
            self._adam_manager = AdamManager(adam.IP, adam.PORT, adam.ADDRESS)
            self._report = Report(
                paths['TEMPLATE'], self._graph_manager, self._testdata
            )

    @Journal.logged
    def show(self):
        """ отображает главное окно """
        if self._is_ready:
            self._prepare()
            super().show()
            self.move(1, 1)
            funcs_test.switchRunningState(self, self._adam_manager, False)

    def closeEvent(self, a0: QCloseEvent) -> None:
        """ погдотовка к закрытию приложения """
        if self._is_ready:
            self._adam_manager.disconnect()
        # print("main window prepared for closing")
        return super().closeEvent(a0)

    @Journal.logged
    def setColorScheme(self):
        """ устанавливает цветовую схему """
        # gvars.wnd_main.stackedWidget.setStyleSheet("QStackedWidget { background: #404040; }")
        # style: str = "QComboBox { color: #ffffff; }" \
        #              "QComboBox:!editable { color: #dddddd; }"
        # gvars.wnd_main.groupTestInfo.setStyleSheet(style)
        # gvars.wnd_main.groupPumpInfo.setStyleSheet(style)

    def _createGUI(self, path_to_ui):
        """ загружает файл графического интерфейса """
        try:
            return uic.loadUi(path_to_ui, self) is not None
        except IOError as error:
            Journal.log(__name__, "::\t", "ошибка:", str(error))
        return False

    @Journal.logged
    def _prepare(self):
        """ инициализирует и подготавливает компоненты главного окна """
        funcs_testlist.init(self)
        funcs_testlist.refresh(self, self._data_manager)
        funcs_testlist.filterSwitch(self)
        funcs_combo.fillCombos(self, self._data_manager)
        funcs_test.prepareSlidersRange(self)
        funcs_table.initTable_points(self)
        funcs_table.initTable_vibrations(self)
        self.setColorScheme()
        self._registerEvents()
        self._initMarkers()
        funcs_group.groupLock(self.groupTestInfo, True)
        funcs_group.groupLock(self.groupPumpInfo, True)

    @Journal.logged
    def _registerEvents(self):
        """ привязывает события элементов формы к обработчикам """
        self.tableTests.selectionModel().currentChanged.connect(self._onChangedTestlist)
        self.tableTests.customContextMenuRequested.connect(self._onMenuTestlist)
        #
        self.txtFilter_ID.textChanged.connect(self._onChangedFilter_apply)
        self.txtFilter_DateTime.textChanged.connect(self._onChangedFilter_apply)
        self.txtFilter_OrderNum.textChanged.connect(self._onChangedFilter_apply)
        self.txtFilter_Serial.textChanged.connect(self._onChangedFilter_apply)
        self.btnFilterReset.clicked.connect(self._onClickedFilter_reset)
        self.radioOrderNum.toggled.connect(self._onChangedTestlist_column)
        #
        self.cmbProducer.currentIndexChanged.connect(self._onChangedCombo_producers)
        self.cmbType.currentIndexChanged.connect(self._onChangedCombo_types)
        self.cmbSerial.currentIndexChanged.connect(self._onChangedCombo_serials)
        #
        self.btnTest_New.clicked.connect(self._onClickedTestInfo_new)
        self.btnTest_Save.clicked.connect(self._onClickedTestInfo_save)
        self.btnTest_Cancel.clicked.connect(self._onClickedTestInfo_cancel)
        #
        self.btnPump_New.clicked.connect(self._onClickedPumpInfo_new)
        self.btnPump_Save.clicked.connect(self._onClickedPumpInfo_save)
        self.btnPump_Cancel.clicked.connect(self._onClickedPumpInfo_cancel)
        #
        self.btnGoTest.clicked.connect(self._onClicked_goTest)
        self.btnGoBack.clicked.connect(self._onClicked_goBack)
        #
        self.txtFlow.textChanged.connect(self._onChanged_sensors)
        self.txtLift.textChanged.connect(self._onChanged_sensors)
        self.txtPower.textChanged.connect(self._onChanged_sensors)
        #
        self.btnAddPoint.clicked.connect(self._onClicked_addPoint)
        self.btnRemovePoint.clicked.connect(self._onClicked_removePoint)
        self.btnClearCurve.clicked.connect(self._onClicked_clearCurve)
        self.btnSaveCharts.clicked.connect(self._onClickedTestResult_save)
        #
        self.radioPointsReal.toggled.connect(self._onChanged_pointsMode)
        # gvars.markers.eventMove.connect(self._on_markers_move)
        self.txtFlow.wheelEvent = self._onMouseWheel_flow
        self.txtLift.wheelEvent = self._onMouseWheel_lift
        self.txtPower.wheelEvent = self._onMouseWheel_power
        #
        self.checkConnection.clicked.connect(self._onClicked_adamConnection)
        self._adam_manager.dataReceived().connect(self._onAdam_dataReceived)
        self.radioFlow0.toggled.connect(self._onChanged_flowmeter)
        self.radioFlow1.toggled.connect(self._onChanged_flowmeter)
        self.radioFlow2.toggled.connect(self._onChanged_flowmeter)
        self.spinPointLines.valueChanged.connect(self._onChanged_pointsNum)
        self.btnEngine.clicked.connect(self._onClicked_engine)
        self.sliderFlow.sliderReleased.connect(self._onChanged_flow)
        self.sliderSpeed.sliderReleased.connect(self._onChanged_speed)
        # ВРЕМЕННО
        self.sliderTorque.sliderReleased.connect(self._onChanged_torque)
        self.sliderPressure.sliderReleased.connect(self._onChanged_pressure)

    def _initMarkers(self):
        """ инициирует маркеры графика испытания """
        params = {
            'test_lft': Qt.blue,
            'test_pwr': Qt.red
        }
        self._graph_manager.init_markers(params, self.gridGraphTest)

    def _onChangedTestlist(self):
        """ изменение выбора теста """
        item = funcs_table.getRow(self.tableTests)
        if item:
            # если запись уже выбрана и загружена - выходим
            if self._testdata.test_.ID == item['ID']:
                return
            Journal.log('***' * 25)
            Journal.log_func(self._onChangedTestlist, item['ID'])
            # очищаем фильтры, поля и информацию о записи
            funcs_combo.filtersReset(self)
            funcs_group.groupClear(self.groupTestInfo)
            funcs_group.groupClear(self.groupPumpInfo)
            self._data_manager.clearRecord()
            # загружаем и отображаем информацию о выбранной записи
            if self._data_manager.loadRecord(item['ID']):
                funcs_display.displayRecord(self, self._data_manager)
                funcs_display.displayTest_deltas(self, self._graph_manager)
            Journal.log('===' * 25)

    def _onChangedTestlist_column(self):
        """ изменён столбец списка тестов (наряд-заказ/серийный номер) """
        Journal.log_func(self._onChangedTestlist_column)
        funcs_testlist.filterSwitch(self)

    def _onMenuTestlist(self):
        """ создание контекстрого меню и обработка """
        menu = QMenu()
        action_print = menu.addAction("Распечатать")
        action_remove = menu.addAction("Удалить")
        action_rewrite = menu.addAction("Переписать")
        action = menu.exec_(QCursor.pos())
        # печать протокола
        if action == action_print:
            self._report.generate()
        # удаление записи
        elif action == action_remove:
            if funcs_aux.askPassword():
                self._data_manager.removeCurrentRecord()
                funcs_testlist.refresh(self, self._data_manager)
        # обновление записи
        elif action == action_rewrite:
            if funcs_aux.askPassword():
                self._data_manager.saveTestInfo()

    def _onChangedCombo_producers(self, index):
        """ выбор производителя """
        item = self.cmbProducer.itemData(index, Qt.UserRole)
        if item:
            Journal.log_func(self._onChangedCombo_producers, item['Name'] if item else "None")
            # ↓ фильтрует типоразмеры для данного производителя
            condition = {'Producer': item['ID']} if index else None
            if not self.cmbType.model().checkAlreadySelected(condition):
                self.cmbType.model().applyFilter(condition)

    def _onChangedCombo_types(self, index):
        """ выбор типоразмера """
        item = self.cmbType.itemData(index, Qt.UserRole)
        Journal.log_func(self._onChangedCombo_types , "None" if not item else item['Name'])
        if item and all(item.values()):
            # ↑ выбирает производителя для данного типоразмера
            condition = {'ID': item['Producer']} if index else None
            if not self.cmbProducer.model().checkAlreadySelected(condition) and index:
                self.cmbProducer.model().selectContains(condition)
            # ↓ фильтрует серийники для данного типоразмера
            condition = {'Type': item['ID']} if index else None
            if not self.cmbSerial.model().checkAlreadySelected(condition):
                self.cmbSerial.model().applyFilter(condition)
            # перерисовывает эталонный график
            self._data_manager.getTestdata().type_.read(item['ID'])
            self._graph_manager.draw_charts(self.frameGraphInfo)

    def _onChangedCombo_serials(self, index):
        """ выбор заводского номера """
        item = self.cmbSerial.itemData(index, Qt.UserRole)
        if item:
            Journal.log_func(self._onChangedCombo_serials, item['Serial'] if item else "None")
            # ↑ выбирает типоразмер для данного серийника
            funcs_combo.selectContains(self.cmbType, {'ID': item['Type']})
            self._graph_manager.draw_charts(self.frameGraphInfo)

    def _onChangedFilter_apply(self, text: str):
        """ изменение значения фильтра списка тестов """
        if text:
            Journal.log_func(self._onChangedFilter_apply, text)
        funcs_testlist.filterApply(self)

    def _onClickedFilter_reset(self):
        """ нажата кнопка сброса фильтра """
        Journal.log('___' * 25)
        Journal.log_func(self._onClickedFilter_reset)
        funcs_testlist.filterReset(self, self._data_manager)
        funcs_group.groupLock(self.groupTestInfo, True)
        funcs_group.groupLock(self.groupPumpInfo, True)

    def _onClickedPumpInfo_new(self):
        """ нажата кнопка добавления нового насоса """
        Journal.log('___' * 25)
        Journal.log_func(self._onClickedPumpInfo_new)
        funcs_group.groupLock(self.groupPumpInfo, False)
        funcs_group.groupClear(self.groupPumpInfo)

    def _onClickedPumpInfo_save(self):
        """ нажата кнопка сохранения нового насоса """
        Journal.log('___' * 25)
        Journal.log_func(self._onClickedPumpInfo_save)
        # проверяем есть ли такой серийник в базе
        pump_id, do_select = self._data_manager.checkExists_serial(
            self.cmbSerial.currentText()
        )
        # если есть - выбираем
        if pump_id and do_select:
            self._testdata.test_['Pump'] = pump_id
            funcs_display.displayPumpInfo(self, self._testdata)
        # проверяем заполение полей и сохраняем
        elif funcs_group.groupCheck(self.groupPumpInfo):
            pump_info = self._testdata.pump_
            funcs_group.groupLock(self.groupPumpInfo, True)
            funcs_group.groupSave(self.groupPumpInfo, pump_info)
            if self._data_manager.savePumpInfo():
                funcs_combo.fillCombos_pump(self, self._data_manager)
                self.cmbSerial.model().selectContains(pump_info.ID)

    def _onClickedPumpInfo_cancel(self):
        """ нажата кнопка отмены добавления нового насоса """
        Journal.log('___' * 25)
        Journal.log_func(self._onClickedPumpInfo_cancel)
        funcs_combo.filtersReset(self)
        funcs_group.groupDisplay(self.groupPumpInfo, self._testdata.pump_)
        funcs_group.groupLock(self.groupPumpInfo, True)

    def _onClickedTestInfo_new(self):
        """ нажата кнопка добавления нового теста """
        Journal.log('___' * 25)
        Journal.log_func(self._onClickedTestInfo_new)
        funcs_group.groupClear(self.groupTestInfo)
        funcs_group.groupLock(self.groupTestInfo, False)
        funcs_aux.setCurrentDate(self)

    def _onClickedTestInfo_save(self):
        """ нажата кнопка сохранения нового теста """
        Journal.log('___' * 25)
        Journal.log_func(self._onClickedTestInfo_save)
        # проверяем есть ли такой наряд-заказ в БД
        test_id, choice = self._data_manager.checkExists_ordernum(
            self.txtOrderNum.text(), with_select=True
        )
        # если есть - выбираем
        if choice != 2:
            funcs_testlist.setCurrentTest(self, test_id)
            if choice == 1:
                funcs_aux.setCurrentDate(self)
        # сохраняем новый тест
        if not test_id and funcs_group.groupCheck(self.groupTestInfo):
            self._data_manager.clearTestInfo()
            funcs_group.groupSave(self.groupTestInfo, self._testdata.test_)
            funcs_group.groupLock(self.groupTestInfo, True)
            self._data_manager.saveTestInfo()
            funcs_testlist.refresh(self, self._data_manager)

    def _onClickedTestInfo_cancel(self):
        """ нажата кнопка отмены добавления нового теста """
        Journal.log('___' * 25)
        Journal.log_func(self._onClickedTestInfo_cancel)
        funcs_group.groupDisplay(self.groupTestInfo, self._testdata.test_)
        funcs_group.groupLock(self.groupTestInfo, True)

    def _onClickedTestResult_save(self):
        """ нажата кнопка сохранения результатов теста """
        Journal.log('___' * 25)
        Journal.log_func(self._onClickedTestResult_save)
        self._graph_manager.save_testdata()
        result = self._testdata.test_.write()
        title = 'УСПЕХ' if result else 'ОШИБКА'
        message = 'Результаты сохранены' if result else 'Запись заблокирована'
        Message.show(title, message)

    def _onClicked_save(self):
        """ нажата кнопка сохранения """
        # self._parent.__store_record()

    def _onClicked_goTest(self):
        """ нажата кнопка перехода к тестированию """
        Journal.log('___' * 25)
        Journal.log_func(self._onClicked_goTest)
        self.stackedWidget.setCurrentIndex(1)
        self._graph_manager.display_charts(self.frameGraphTest)
        self._graph_manager.markers_reposition()
        self._graph_manager.set_point_lines_max()

    def _onClicked_goBack(self):
        """ нажата кнопка возврата на основное окно """
        Journal.log('___' * 25)
        Journal.log_func(self._onClicked_goBack)
        self.stackedWidget.setCurrentIndex(0)
        self._graph_manager.display_charts(self.frameGraphInfo)
        funcs_testlist.setCurrentTest(self, self._testdata.test_['ID'])

    def _onClicked_engine(self):
        """ нажата кнопка начала/остановки испытания """
        Journal.log('___' * 25)
        Journal.log_func(self._onClicked_engine)
        state = not funcs_test.states["is_running"]
        self._graph_manager.switch_charts_visibility(state)
        funcs_test.switchRunningState(self, self._adam_manager, state)

    def _onClicked_addPoint(self):
        """ нажата кнопка добавления точки """
        Journal.log('___' * 25)
        Journal.log_func(self._onClicked_addPoint)
        current_vals = funcs_test.getCurrentVals(self)
        funcs_table.addToTable_points(self, *current_vals)
        self._graph_manager.markers_add_knots()
        self._graph_manager.add_points_to_charts(*current_vals)
        self._graph_manager.display_charts(self.frameGraphTest)
        self.spinPointLines.setValue(int(self.spinPointLines.value()) - 1)

    def _onClicked_removePoint(self):
        """ нажата кнопка удаления точки """
        Journal.log('___' * 25)
        Journal.log_func(self._onClicked_removePoint)
        funcs_table.removeLastRow(self.tablePoints)
        self._graph_manager.markers_remove_knots()
        self._graph_manager.remove_last_points_from_charts()
        self._graph_manager.display_charts(self.frameGraphTest)
        self.spinPointLines.setValue(int(self.spinPointLines.value()) + 1)

    def _onChanged_pointsMode(self):
        """ переключение значений точек реальные / на ступень """
        funcs_test.switchPointsStagesReal(self, self._testdata)

    def _onClicked_clearCurve(self):
        """ нажата кнопка удаления всех точек """
        Journal.log('___' * 25)
        Journal.log_func(self._onClicked_clearCurve)
        funcs_table.clear(self.tablePoints)
        self._graph_manager.markers_clear_knots()
        self._graph_manager.clear_points_from_charts()
        self._graph_manager.display_charts(self.frameGraphTest)

    def _onClicked_adamConnection(self):
        """ нажата кнопка подключения к ADAM5000TCP """
        Journal.log('___' * 25)
        Journal.log_func(self._onClicked_adamConnection)
        state = self.checkConnection.isChecked()
        state = funcs_test.switchConnection(self._adam_manager, state)
        self.checkConnection.setChecked(state)
        self.checkConnection.setText("подключено" if state else "отключено")
        funcs_group.groupClear(self.groupTestSensors)

    def _onAdam_dataReceived(self, sensors: dict):
        """ приход данных от ADAM5000TCP """
        # Journal.log_func(self._on_adam_data_received)
        funcs_display.displaySensors(self, sensors)

    def _onChanged_flowmeter(self):
        """ изменение текущего расходомера """
        # Journal.log_func(self._on_changed_flowmeter)
        funcs_test.switchActiveFlowmeter(self)

    def _onChanged_flow(self):
        """ изменение положение задвижки """
        funcs_test.changeFlow(self, self._adam_manager)

    def _onChanged_speed(self):
        """ изменение скорости вращения двигателя """
        funcs_test.changeSpeed(self, self._adam_manager)

    def _onChanged_torque(self):
        """ ВРЕМЕННО изменение крутящего момента """
        funcs_test.changeTorque(self, self._adam_manager)

    def _onChanged_pressure(self):
        """ ВРЕМЕННО изменение давления на выходе """
        funcs_test.changePressure(self, self._adam_manager)

    def _onChanged_pointsNum(self):
        """ изменение порядкового номера отбиваемой точки """
        num = int(self.spinPointLines.value())
        if self.spinPointLines.isEnabled():
            self._graph_manager.set_point_lines_num(num)
        else:
            self._graph_manager.set_point_lines_cur(num)

    def _onChanged_sensors(self):
        """ изменения значений датчиков """
        vals = funcs_test.getCurrentVals(self)
        params = [
            {'name': 'test_lft', 'x': vals[0], 'y': vals[1]},
            {'name': 'test_pwr', 'x': vals[0], 'y': vals[2]}
        ]
        self._graph_manager.markers_move(params)

    def _onMarkers_move(self, point_data: dict):
        """ изменения позиции маркеров """
        funcs_display.displayMarkerValues(self, point_data)

    def _onMouseWheel_flow(self, event):
        """ изменяет значение расхода колесиком мышки """
        funcs_aux.processMouseWheel(
            self.txtFlow, event, 1)

    def _onMouseWheel_lift(self, event):
        """ изменяет значение напора колесиком мышки """
        funcs_aux.processMouseWheel(
            self.txtLift, event, 0.1)

    def _onMouseWheel_power(self, event):
        """ изменяет значение мощности колесиком мышки """
        funcs_aux.processMouseWheel(
            self.txtPower, event, 0.001)
