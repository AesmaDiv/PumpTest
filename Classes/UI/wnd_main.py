"""
    Модуль содержит функции основного окна программы
"""
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QSlider
from PyQt5.QtGui import QCloseEvent
from Classes.UI import funcs_aux
from Classes.UI import funcs_table
from Classes.UI import funcs_combo
from Classes.UI import funcs_group
from Classes.UI import funcs_test
from Classes.UI import funcs_display
from Classes.UI import funcs_info
from Classes.UI.wnd_type import TypeWindow
from Classes.UI.testlist import TestList
from Classes.Adam import adam_config as adam
from Classes.Adam.adam_manager import AdamManager
from Classes.Data.data_manager import DataManager
from Classes.Graph.graph_manager import GraphManager
from Classes.Data.report import Report

from AesmaLib.message import Message
from AesmaLib.journal import Journal


class MainWindow(QMainWindow):
    """ Класс описания функционала главного окна приложения """
    _managers = dict.fromkeys(["adam", "data", "graph"], None)
    _is_displaying = dict.fromkeys(['Producer','Type','Serial'], False)

    def __init__(self, paths, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._is_ready = self._createGUI(paths['WND'])
        if self._is_ready:
            self._managers["adam"] = AdamManager(adam.IP, adam.PORT, adam.ADDRESS)
            self._managers["data"] = DataManager(paths['DB'])
            self._managers["graph"] = GraphManager(self.testdata())
            # self.adam_manager.callback.append(self._onAdam_dataReceived)
            self._testlist = TestList(self, self.db_manager())
            self._type_window = TypeWindow(self, self.db_manager(), paths['TYPE'])
            self._report = Report(paths['TEMPLATE'], self.graph_manager(), self.testdata())

    def adam_manager(self):
        """ возвращает ссылку на менеджер управления адамом """
        return self._managers["adam"]

    def db_manager(self):
        """ возвращает ссылку на менеджер управления базой данных """
        return self._managers["data"]

    def graph_manager(self):
        """ возвращает ссылку на менеджер управления графиком """
        return self._managers["graph"]

    def testdata(self):
        """ возвращает ссылку на данные об испытании """
        return self.db_manager().getTestdata()


    @Journal.logged
    def show(self) -> bool:
        """ отображает главное окно """
        if self._is_ready:
            self._prepare()
            super().show()
            self.move(1, 1)
            funcs_test.switchRunningState(self, False)
            return True
        return False

    def closeEvent(self, close_event: QCloseEvent) -> None:
        """ погдотовка к закрытию приложения """
        if self._is_ready:
            self.adam_manager().dataReceived.disconnect()
            self.adam_manager().setPollingState(False)
        return super().closeEvent(close_event)

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
        self._testlist.initialize()
        self._testlist.refresh()
        self._testlist.filterSwitch()
        funcs_combo.fillCombos(self, self.db_manager())
        funcs_test.prepareSlidersRange(self)
        funcs_table.initTable_points(self)
        funcs_table.initTable_vibrations(self)
        self._registerEvents()
        self._initMarkers()
        self._initSlider(self.sliderFlow)
        self._initSlider(self.sliderSpeed)
        # ВРЕМЕННО ->
        self._initSlider(self.sliderTorque)
        self._initSlider(self.sliderPressure)
        # <- ВРЕМЕННО
        funcs_group.groupLock(self.groupTestInfo, True)
        funcs_group.groupLock(self.groupPumpInfo, True)

    @Journal.logged
    def _registerEvents(self):
        """ привязывает события элементов формы к обработчикам """
        self._testlist.selectionChanged.connect(self._onChangedTestlist)
        self._testlist.menuSelected.connect(self._onMenuTestlist)
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
        self.btnAddPoint.clicked.connect(self._onClicked_addPoint)
        self.btnRemovePoint.clicked.connect(self._onClicked_removePoint)
        self.btnClearCurve.clicked.connect(self._onClicked_clearCurve)
        self.btnSaveCharts.clicked.connect(self._onClickedTestResult_save)
        #
        self.chkConnection.clicked.connect(self._onAdam_connection)
        self.radioFlow0.toggled.connect(self._onChanged_flowmeter)
        self.radioFlow1.toggled.connect(self._onChanged_flowmeter)
        self.radioFlow2.toggled.connect(self._onChanged_flowmeter)
        self.spinPointLines.valueChanged.connect(self._onChanged_pointsNum)
        self.btnEngine.clicked.connect(self._onClicked_engine)
        self.txtFlow.textChanged.connect(self._onChanged_sensors)
        self.txtLift.textChanged.connect(self._onChanged_sensors)
        self.txtPower.textChanged.connect(self._onChanged_sensors)
        self.radioPointsReal.toggled.connect(self._onChanged_pointsMode)
        #
        self.adam_manager().dataReceived.connect(
            self._onAdam_dataReceived, no_receiver_check = True
        )

    def _initMarkers(self):
        """ инициирует маркеры графика испытания """
        params = {
            'test_lft': Qt.blue,
            'test_pwr': Qt.red
        }
        self.graph_manager().initMarkers(params, self.gridGraphTest)

    def _initSlider(self, slider: QSlider):
        setattr(slider, "is_draging", False)
        def onValueChanged(value):
            if not getattr(slider, "is_draging"):
                funcs_test.setAdamValue(slider, self.adam_manager(), value)
        def onPressed():
            setattr(slider, "is_draging", True)
        def onReleased():
            setattr(slider, "is_draging", False)
            funcs_test.setAdamValue(slider, self.adam_manager())
        slider.sliderPressed.connect(onPressed)
        slider.sliderReleased.connect(onReleased)
        slider.valueChanged.connect(onValueChanged)

    def _onChangedTestlist(self, item):
        """ изменение выбора теста """
        if item:
            # если запись уже выбрана и загружена - выходим
            if self.testdata().test_.ID == item['ID']:
                return
            Journal.log('***' * 25)
            Journal.log_func(self._onChangedTestlist, item['ID'])
            # очищаем фильтры, поля и информацию о записи
            funcs_combo.resetFilters_pumpInfo(self)
            funcs_group.groupClear(self.groupTestInfo)
            funcs_group.groupClear(self.groupPumpInfo)
            self.db_manager().clearRecord()
            # загружаем и отображаем информацию о выбранной записи
            if self.db_manager().loadRecord(item['ID']):
                self.graph_manager().clearCharts()
                self.graph_manager().markersClearKnots()
                funcs_display.displayRecord(self, self.db_manager())
            funcs_display.displayTest_deltas(self, self.graph_manager())
            Journal.log('===' * 25)

    def _onChangedTestlist_column(self):
        """ изменён столбец списка тестов (наряд-заказ/серийный номер) """
        Journal.log_func(self._onChangedTestlist_column)
        self._testlist.filterSwitch()

    def _onMenuTestlist(self, action):
        """ выбор в контекстном меню списка тестов """
        # печать протокола
        if action == "print":
            self._report.print()
            return
        # удаление записи
        if action == "delete":
            if funcs_aux.askPassword():
                self.db_manager().removeCurrentRecord()
                self._testlist.refresh()
                Message.show("УСПЕХ", "Запись удалена")
                return
        # обновление записи
        if action == "update":
            if funcs_aux.askPassword():
                self.db_manager().saveTestInfo()
                Message.show("УСПЕХ", "Запись обновлена")
                return

    def _onChangedCombo_producers(self, index):
        """ выбор производителя """
        item = self.cmbProducer.itemData(index, Qt.UserRole)
        Journal.log_func(self._onChangedCombo_producers, item['Name'] if item else "None")
        if item:
            # ↓ фильтрует типоразмеры для данного производителя
            condition = {'Producer': item['ID']} if index else None
            funcs_combo.filterByCondition(self.cmbType, condition)

    def _onChangedCombo_types(self, index):
        """ выбор типоразмера """
        item = self.cmbType.itemData(index, Qt.UserRole)
        Journal.log_func(self._onChangedCombo_types , "None" if not item else item['Name'])
        if item and all(item.values()):
            # ↑ выбирает производителя для данного типоразмера
            condition = {'ID': item['Producer']}
            funcs_combo.selectContains(self.cmbProducer, condition)
            # ↓ фильтрует серийники для данного типоразмера
            condition = {'Type': item['ID']}
            funcs_combo.filterByCondition(self.cmbSerial, condition)
            # перерисовывает эталонный график
            self.db_manager().getTestdata().type_.read(item['ID'])
            self.graph_manager().drawCharts(self.frameGraphInfo)

    def _onChangedCombo_serials(self, index):
        """ выбор заводского номера """
        item = self.cmbSerial.itemData(index, Qt.UserRole)
        Journal.log_func(self._onChangedCombo_serials, item['Serial'] if item else "None")
        # ↑ выбирает типоразмер для данного серийника
        if item and all(item.values()):
            funcs_combo.resetFilter(self.cmbType)
            condition = {'ID': item['Type']}
            funcs_combo.selectContains(self.cmbType, condition)
            self.graph_manager().drawCharts(self.frameGraphInfo)

    def _onChangedFilter_apply(self, text: str):
        """ изменение значения фильтра списка тестов """
        if text:
            Journal.log_func(self._onChangedFilter_apply, text)
        filter_id = self.txtFilter_ID.text()
        filter_datetime = self.txtFilter_DateTime.text()
        filter_ordernum = self.txtFilter_OrderNum.text()
        filter_serial = self.txtFilter_Serial.text()
        conditions = [filter_id, filter_datetime, filter_ordernum, filter_serial]
        self._testlist.filterApply(conditions)

    def _onClickedFilter_reset(self):
        """ нажата кнопка сброса фильтра """
        Journal.log('___' * 25)
        Journal.log_func(self._onClickedFilter_reset)
        funcs_group.groupClear(self.groupTestList)
        funcs_group.groupClear(self.groupTestInfo)
        funcs_group.groupClear(self.groupPumpInfo)
        self.db_manager().clearRecord()
        self._testlist.filterApply()
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
        # если типоразмер не указан, предлагаем добавить новый
        if not self.cmbType.currentText():
            if Message.ask("Внимание", "Типоразмер не указан. Добавить новый?"):
                if self._type_window.addType():
                    funcs_combo.fillCombos_pump(self, self.db_manager())
        funcs_info.savePumpInfo(self)

    def _onClickedPumpInfo_cancel(self):
        """ нажата кнопка отмены добавления нового насоса """
        Journal.log('___' * 25)
        Journal.log_func(self._onClickedPumpInfo_cancel)
        funcs_combo.resetFilters_pumpInfo(self)
        funcs_group.groupDisplay(self.groupPumpInfo, self.testdata().pump_)
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
        funcs_info.saveTestInfo(self, self._testlist)

    def _onClickedTestInfo_cancel(self):
        """ нажата кнопка отмены добавления нового теста """
        Journal.log('___' * 25)
        Journal.log_func(self._onClickedTestInfo_cancel)
        funcs_group.groupDisplay(self.groupTestInfo, self.testdata().test_)
        funcs_group.groupLock(self.groupTestInfo, True)

    def _onClickedTestResult_save(self):
        """ нажата кнопка сохранения результатов теста """
        Journal.log('___' * 25)
        Journal.log_func(self._onClickedTestResult_save)
        self.graph_manager().saveTestdata()
        result = self.testdata().test_.write()
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
        self.graph_manager().displayCharts(self.frameGraphTest)
        self.graph_manager().markersReposition()
        self.graph_manager().switchChartsVisibility(True)

    def _onClicked_goBack(self):
        """ нажата кнопка возврата на основное окно """
        Journal.log('___' * 25)
        Journal.log_func(self._onClicked_goBack)
        self.stackedWidget.setCurrentIndex(0)
        self.graph_manager().displayCharts(self.frameGraphInfo)
        self._testlist.setCurrentTest(self.testdata().test_['ID'])

    def _onClicked_engine(self):
        """ нажата кнопка начала/остановки испытания """
        Journal.log('___' * 25)
        Journal.log_func(self._onClicked_engine)
        state = not funcs_test.states["is_running"]
        self.graph_manager().switchChartsVisibility(not state)
        funcs_test.switchControlsAccessible(self, state)
        funcs_test.switchRunningState(self, state)

    def _onClicked_addPoint(self):
        """ нажата кнопка добавления точки """
        Journal.log('___' * 25)
        Journal.log_func(self._onClicked_addPoint)
        spin = self.spinPointLines
        if spin.value() == 0:
            Message.show("Внимание:", "Достигнуто максимальное кол-во точек.")
            return
        current_vals = funcs_test.getCurrentVals(self)
        if spin.value() == spin.maximum():
            self.graph_manager().setPointLines_max(current_vals[0])
        if not self.graph_manager().checkPointExists(current_vals[0]):
            self.graph_manager().markersAddKnots()
            self.graph_manager().addPointsToCharts(*current_vals)
            self.graph_manager().displayCharts(self.frameGraphTest)
            current_vals.append(self.testdata().pump_.Stages)
            funcs_table.addToTable_points(self.tablePoints, current_vals)
            spin.setValue(int(spin.value()) - 1)

    def _onClicked_removePoint(self):
        """ нажата кнопка удаления точки """
        Journal.log('___' * 25)
        Journal.log_func(self._onClicked_removePoint)
        funcs_table.removeLastRow(self.tablePoints)
        self.graph_manager().markersRemoveKnots()
        self.graph_manager().removeLastPointsFromCharts()
        self.graph_manager().displayCharts(self.frameGraphTest)
        self.spinPointLines.setValue(int(self.spinPointLines.value()) + 1)

    def _onChanged_pointsMode(self):
        """ переключение значений точек реальные / на ступень """
        display = ["flw", "lft", "pwr", "eff"]
        if self.radioPointsReal.isChecked():
            display[1] = "lft_real"
            display[2] = "pwr_real"
        funcs_table.setDisplay(self.tablePoints, display)

    def _onClicked_clearCurve(self):
        """ нажата кнопка удаления всех точек """
        Journal.log('___' * 25)
        Journal.log_func(self._onClicked_clearCurve)
        funcs_table.clear(self.tablePoints)
        self.graph_manager().markersClearKnots()
        self.graph_manager().clearPointsFromCharts()
        self.graph_manager().displayCharts(self.frameGraphTest)

    def _onAdam_connection(self):
        """ нажата кнопка подключения к ADAM5000TCP """
        Journal.log('___' * 25)
        Journal.log_func(self._onAdam_connection)
        state = self.chkConnection.isChecked()
        state = self.adam_manager().setPollingState(state, 0.100)
        funcs_test.switchControlsAccessible(self, False)
        self.chkConnection.setChecked(state)
        self.chkConnection.setStyleSheet(
            "QCheckBox { color: %s; }" % ("lime" if state else "red")
        )
        self.chkConnection.setText(
            "контроллер %s" % ("подключен" if state else "отключен")
        )
        self.pageTestControl.setEnabled(state)
        funcs_group.groupClear(self.groupTestSensors)
        if state:
            funcs_test.setControlsDefaults(self)
            funcs_test.setAdamDefaults(self.adam_manager())

    @pyqtSlot(dict)
    def _onAdam_dataReceived(self, args: dict):
        """ приход данных от ADAM5000TCP """
        # Journal.log_func(self._on_adam_data_received)
        funcs_display.displaySensors(self, args)

    def _onChanged_flowmeter(self):
        """ изменение текущего расходомера """
        # Journal.log_func(self._on_changed_flowmeter)
        sender = self.sender()
        state = sender.isChecked()
        funcs_test.switchActiveFlowmeter(self.adam_manager(), sender, state)

    def _onChanged_pointsNum(self):
        """ изменение порядкового номера отбиваемой точки """
        num = int(self.spinPointLines.value())
        if self.spinPointLines.isEnabled():
            self.graph_manager().setPointLines_num(num)
        else:
            self.graph_manager().setPointLines_cur(num)

    def _onChanged_sensors(self):
        """ изменения значений датчиков """
        vals = funcs_test.getCurrentVals(self)
        params = [
            {'name': 'test_lft', 'x': vals[0], 'y': vals[1]},
            {'name': 'test_pwr', 'x': vals[0], 'y': vals[2]}
        ]
        self.graph_manager().markersMove(params)
