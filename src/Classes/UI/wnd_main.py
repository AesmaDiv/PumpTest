"""
    Модуль содержит функции основного окна программы
"""
import time
from loguru import logger

from PyQt6 import uic
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QSlider, QLabel, QPushButton, QToolButton
from PyQt6.QtGui import QCloseEvent

from Classes.UI.funcs import funcs_table
from Classes.UI.funcs import funcs_combo
from Classes.UI.funcs import funcs_group
from Classes.UI.funcs import funcs_test
from Classes.UI.funcs import funcs_info
from Classes.UI.funcs import funcs_aux
from Classes.UI.testlist import TestList
from Classes.UI.bindings import Binding
from Classes.UI.progress import PurgeProgress
from Classes.Test.test_manager import TestManager, TestMode
from Classes.Adam.adam_manager import AdamManager
from Classes.Adam.adam_names import ChannelNames as CN
from Classes.Data.db_manager import DataManager
from Classes.Data.record import Record, TestData
from Classes.Data.report import Report
from Classes.Graph.graph_manager import GraphManager

from AesmaLib.message import Message

class MainWindow(QMainWindow):
    """Класс описания функционала основного окна приложения"""
    signalTypeChangeRequest = pyqtSignal(dict, name='onTypeChangeRequest')

    def __init__(self, path_to_ui, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._path_to_ui: str = path_to_ui
        self._testlist: TestList = TestList(self)
        self._testdata: TestData = None
        self._report: Report = None
        self._managers = {
            'Adam': None,
            'Data': None,
            'Graf': None,
            'Test': None
        }
        self._bindings = {
            'test': None,
            'pump': None,
            'sens': None
        }
        self._states = {
            'editing': {
                'pump': False,
                'test': False
            }
        }

    def show(self) -> bool:
        """запуск основного окна приложения"""
        logger.debug(self.show.__doc__)
        if not self._createGUI():
            return False
        if not self._createBindings():
            return False
        self._prepare()
        super().show()
        self.move(1, 1)
        return True

    def closeEvent(self, close_event: QCloseEvent) -> None:
        """погдотовка к закрытию приложения"""
        if self._managers['Adam']:
            # отключение ADAM 5000 TCP
            self.adam_manager.dataReceived.disconnect()
            self.adam_manager.setPollingState(False)
        return super().closeEvent(close_event)

    def initConnections(self):
        """инициализация подключений"""
        # подключение к базе данных
        self._displayLabelState(self.statusDb, self.db_manager.isConnected)
        # подключение к Adam5000TCP
        self.chkConnection.click()

    def displayMessage(self, message: str):
        self.statusMessage.setText(message)

#region СВОЙСТВА =>>
    def setTestData(self, testdata: TestData):
        """привязка класса данных об испытании"""
        self._testdata = testdata

    def setDataManager(self, db_manager: DataManager):
        """привязка менеджера базы данных"""
        self._managers.update({'Data': db_manager})

    def setGraphManager(self, graph_manager: GraphManager):
        """привязка менеджера графиков"""
        self._managers.update({'Graf': graph_manager})

    def setTestManager(self, test_manager: TestManager):
        """привязка менеджера управления испытание"""
        self._managers.update({'Test': test_manager})

    def setAdamManager(self, adam_manager: AdamManager):
        """привязка менеджера управления адамом"""
        self._managers.update({'Adam': adam_manager})

    def setReport(self, report: Report):
        """привязка класса протокола"""
        self._report = report

    @property
    def db_manager(self) -> DataManager:
        """возвращает ссылку на менеджер управления базой данных"""
        return self._managers["Data"]

    @property
    def graph_manager(self) -> GraphManager:
        """возвращает ссылку на менеджер управления графиком"""
        return self._managers["Graf"]

    @property
    def adam_manager(self) -> AdamManager:
        """возвращает ссылку на менеджер управления адамом"""
        return self._managers["Adam"]

    @property
    def test_manager(self) -> TestManager:
        """возвращает ссылку на менеджер управления адамом"""
        return self._managers["Test"]
#endregion <<= СВОЙСТВА

#region ИНИЦИАЛИЗАЦИЯ =>
    def _createGUI(self) -> bool:
        """инициализация графического интерфейса"""
        try:
            logger.debug({self._createGUI.__doc__})
            if uic.loadUi(self._path_to_ui, self):
                return True
            logger.error("Не удалось загрузить файл графического интерфейса")
        except IOError as error:
            logger.error("\tОшибка загрузки файла графического интерфейса")
            logger.error(error.strerror)
        return False

    def _createBindings(self):
        """создание привязок значений из testdata к виджетам"""
        logger.debug({self._createBindings.__doc__})
        if not self._testdata:
            logger.error("Отсутствует привязка к классу данных об испытании")
            return False
        self._bindings['test'] = Binding(self.groupTestInfo, self._testdata.test_)
        self._bindings['pump'] = Binding(self.groupPumpInfo, self._testdata.pump_)
        self._bindings['sens'] = Binding(self.groupTestSensors, self.test_manager.sensors)
        self._bindings['test'].generate()
        self._bindings['pump'].generate()
        self._bindings['sens'].generate()
        return True

    def _prepare(self):
        """инициализация и подготовка компонентов главного окна"""
        logger.debug(self._prepare.__doc__)
        if not self.db_manager:
            logger.error("Отсутствует привязка к менеджеру базы данных")
            return
        if not self.graph_manager:
            logger.error("Отсутствует привязка к менеджеру графиков")
            return
        self._initTestList()
        funcs_combo.fillCombos(self, self.db_manager)
        self._registerEvents()
        self._initSliders()
        self._initStatusBar()
        funcs_table.initTable_points(self)
        funcs_table.initTable_vibrations(self)
        self.tabWidget.setTabVisible(0, False)
        self.graph_manager.initMarkers(self.gridGraphTest)
        funcs_group.groupLock(self.groupTestInfo, True)
        funcs_group.groupLock(self.groupPumpInfo, True)

    def _initTestList(self):
        """инициализация списка тестов"""
        self._testlist.build()
        self._testlist.refresh(self.db_manager)
        self._testlist.filterSwitch()

    def _initSliders(self):
        self._initSlider(self.sliderFlow)
        self._initSlider(self.sliderSpeed)

    def _initSlider(self, slider: QSlider):
        """инициализация слайдеров управления ходом испытания"""
        setattr(slider, "is_draging", False)
        def onValueChanged(value):
            if not getattr(slider, "is_draging"):
                self.test_manager.sliderToAdam(slider.objectName(), value)
        def onPressed():
            setattr(slider, "is_draging", True)
        def onReleased():
            setattr(slider, "is_draging", False)
            self.test_manager.sliderToAdam(slider.objectName(), slider.value())
        slider.sliderPressed.connect(onPressed)
        slider.sliderReleased.connect(onReleased)
        slider.valueChanged.connect(onValueChanged)

    def _initStatusBar(self):
        """инициализация статусбара"""
        self._addConnectionIcons()
        self._addPurgeElements()
        self._addMessageString()
        self._addValveIndicators()
        self._addReloadConfig()

    def _addConnectionIcons(self):
        """добавление индикаторов подключений"""
        for name, text in zip(('statusDb', 'statusAdam'),('DB', 'ADAM')):
            lbl = QLabel(self, objectName=name, text=text)
            lbl.setFixedWidth(80)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.statusBar().addWidget(lbl)
            setattr(self, name, lbl)

    def _addPurgeElements(self):
        """добавление элементов управления продувкой"""
        # кнопка начала/остановки продувки
        btn = QPushButton(self, text="Продувка", checkable=True)
        btn.setFixedSize(80, 20)
        btn.clicked.connect(self._onClicked_Purge)
        self.statusBar().addWidget(btn)
        setattr(self, "btnPurge", btn)
        # прогрессбар для индикации продувки
        prg = PurgeProgress(self, delay=100, minimum=0, maximum=0)
        prg.onTick.connect(self._onTick_Purge)
        prg.setFixedSize(80, 20)
        prg.hide()
        self.statusBar().addWidget(prg)
        setattr(self, "progressPurge", prg)

    def _addMessageString(self):
        """добавление строки сообщений"""
        lbl = QLabel(self, objectName='statusMessage', text='...')
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("#statusMessage { background-color: 'grey'; padding-left: 5px;}")
        self.statusBar().addWidget(lbl, 1)
        setattr(self, 'statusMessage', lbl)

    def _addValveIndicators(self):
        """добавление индикаторов кранов"""
        valves = ('vlvAir', 'vlvWater', 'vlvTest', 'vlvF1', 'vlvF2')
        names = ('Вздх', 'Вода', 'Тест', 'Крн0', 'Крн1')
        for name, text in zip(valves, names):
            lbl = QLabel(self, objectName=name, text=text)
            lbl.setFixedWidth(30)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.statusBar().addWidget(lbl)
            setattr(self, name, lbl)

    def _addReloadConfig(self):
        btn = QToolButton(self, width=20, height=20)
        btn.clicked.connect(self.adam_manager.reloadConfig)
        self.statusBar().addPermanentWidget(btn, 1)
        setattr(self, 'btnReloadConfig', btn)

    def _displayLabelState(self, label: QLabel, state: bool):
        color = "'green'" if state else "'red'"
        style = "#" + label.objectName() + "{ color: 'white'; background-color:" + color +";}"
        label.setStyleSheet(style)


    def _registerEvents(self):
        """привязка событий элементов формы к обработчикам"""
        self._testlist.selectionChanged.connect(self._onChanged_Testlist)
        self._testlist.menuSelected.connect(self._onMenuTestlist)
        #
        self.txtFilter_ID.textChanged.connect(self._onChangedFilter_Apply)
        self.txtFilter_DateTime.textChanged.connect(self._onChangedFilter_Apply)
        self.txtFilter_OrderNum.textChanged.connect(self._onChangedFilter_Apply)
        self.txtFilter_Serial.textChanged.connect(self._onChangedFilter_Apply)
        self.btnFilterReset.clicked.connect(self._onClickedFilter_Reset)
        self.radioOrderNum.toggled.connect(self._onToggled_TestlistColumn)
        #
        self.cmbProducer.currentIndexChanged.connect(self._onChangedCombo_Producers)
        self.cmbType.currentIndexChanged.connect(self._onChangedCombo_Types)
        self.cmbSerial.currentIndexChanged.connect(self._onChangedCombo_Serials)
        self.cmbSerial.currentTextChanged.connect(self._onChangedCombo_SerialsText)
        #
        self.btnPump_Edit.clicked.connect(self._onClicked_InfoPump)
        self.btnPump_Save.clicked.connect(self._onClicked_InfoPump)
        self.btnPump_Cancel.clicked.connect(self._onClicked_InfoPump)
        #
        self.btnTest_Edit.clicked.connect(self._onClicked_InfoTest)
        self.btnTest_Save.clicked.connect(self._onClicked_InfoTest)
        self.btnTest_Cancel.clicked.connect(self._onClicked_InfoTest)
        self.btnTest_Order.clicked.connect(self._onClicked_InfoTest)
        #
        self.btnGoTest.clicked.connect(self._onClicked_SwitchMode)
        self.btnGoInfo.clicked.connect(self._onClicked_SwitchMode)
        #
        self.btnAddPoint.clicked.connect(self._onClicked_PointAdd)
        self.btnRemovePoint.clicked.connect(self._onClicked_PointRemove)
        self.btnClearCurve.clicked.connect(self._onClicked_ClearCurve)
        self.btnSaveCharts.clicked.connect(self._onClickedTestResult_Save)
        #
        self.chkConnection.clicked.connect(self._onAdam_Connection)
        self.radioFlow0.toggled.connect(self._onToggled_Flowmeter)
        self.radioFlow1.toggled.connect(self._onToggled_Flowmeter)
        self.radioFlow2.toggled.connect(self._onToggled_Flowmeter)
        self.radioRotationL.toggled.connect(self._onToggled_Rotation)
        self.radioRotationR.toggled.connect(self._onToggled_Rotation)
        self.radioModeO.toggled.connect(self._onToggled_TestMode)
        self.radioModeT.toggled.connect(self._onToggled_TestMode)
        self.spinPointLines.valueChanged.connect(self._onChanged_PointsNum)
        self.btnEngine.clicked.connect(self._onClicked_Engine)
        self.txtFlow.textChanged.connect(self._onChanged_Sensors)
        self.txtLift.textChanged.connect(self._onChanged_Sensors)
        self.txtPower.textChanged.connect(self._onChanged_Sensors)
        self.radioPointsReal.toggled.connect(self._onToggled_PointsMode)
        #
        self.adam_manager.dataReceived.connect(
            self._onAdam_DataReceived, no_receiver_check = True
        )
#endregion <<= ИНИЦИАЛИЗАЦИЯ

#region ОБРАБОТЧИКИ СОБЫТИЙ =>>

#region     СПИСОК ТЕСТОВ ->
    def _onChanged_Testlist(self, item: dict):
        """изменение выбора теста"""
        if not item:
            return
        logger.info(f"{'***' * 25}")
        logger.info(f"Выбор теста № {item['ID']}")
        self._states['editing'].update({
            'pump': False,
            'test': False,
        })
        # если запись уже выбрана и загружена - выходим
        x = time.time_ns()
        if self._testdata.test_.ID == item['ID']:
            return
        self._clearInfo()
        self._loadInfo(item['ID'])
        if self._report:
            self._report.show(self, self._testdata)
            # self._report.show(self, self._testdata, self.webEngineView)
        logger.info(f"{'===' * 25}")
        print(f"TEST SELECT {(time.time_ns() - x) / 1000000}")

    def _onToggled_TestlistColumn(self):
        """изменение столбца отображения в списке тестов (наряд-заказ/серийный номер)"""
        logger.debug(self._onToggled_TestlistColumn.__doc__)
        self._testlist.filterSwitch()

    def _onMenuTestlist(self, action):
        """выбор в контекстном меню списка тестов"""
        try:
            {
                "print": self._printInfo,
                "delete": self._deleteInfo,
                "update": self._updateInfo
            }[action]()
        except KeyError:
            logger.error("Ошибка определения элемента контестного меню")

    def _onChangedFilter_Apply(self, text: str):
        """изменение значения фильтра списка тестов"""
        logger.debug(f"{self._onChangedFilter_Apply.__doc__} -> '{text}'")
        conditions = [
            self.txtFilter_ID.text(),
            self.txtFilter_DateTime.text(),
            self.txtFilter_OrderNum.text(),
            self.txtFilter_Serial.text()
        ]
        self._testlist.filterApply(conditions)

    def _onClickedFilter_Reset(self):
        """нажатие кнопки сброса фильтра"""
        logger.debug(self._onClickedFilter_Reset.__doc__)
        funcs_group.groupClear(self.groupTestList)
        funcs_group.groupClear(self.groupTestInfo)
        funcs_group.groupClear(self.groupPumpInfo)
        self.db_manager.clearRecord()
        self._testlist.filterApply()
        funcs_group.groupLock(self.groupTestInfo, True)
        funcs_group.groupLock(self.groupPumpInfo, True)
#endregion      <- СПИСОК ТЕСТОВ

#region     КОМБОБОКСЫ ->
    def _onChangedCombo_Producers(self, index):
        """выбор производителя"""
        item = self.cmbProducer.itemData(index, Qt.ItemDataRole.UserRole)
        logger.debug(f"выбор производителя -> {item['Name'] if item else 'None'}")
        # ↓ фильтрует типоразмеры для данного производителя
        # if self._states['editing']['pump'] and item:
        #     self._flags['producer'] = True
        #     self.cmbType.setCurrentIndex(0)
        #     condition = {'Producer': item['ID']} if index else None
        #     funcs_combo.filterByCondition(self.cmbType, condition)

    def _onChangedCombo_Types(self, index):
        """выбор типоразмера"""
        item = self.cmbType.itemData(index, Qt.ItemDataRole.UserRole)
        logger.debug(f"выбор типоразмера -> {item['Name'] if item else 'None'}")
        if not item or not all(item.values()):
            return
        # ↑ выбирает производителя для данного типоразмера
        condition = {'ID': item['Producer']}
        funcs_combo.selectContains(self.cmbProducer, condition)
        if self._states['editing']['pump']:
            # ↓ фильтрует серийники для данного типоразмера
            # condition = {'Type': item['ID']}
            # funcs_combo.filterByCondition(self.cmbSerial, condition)
            # читает и отображает данные об типоразмере
            self._loadRecord(self._testdata.type_, item['ID'])
        self.graph_manager.displayCharts(self.frameGraphInfo)
        self.lblPumpInfo.setText(f"{self.cmbProducer.currentText()} : {self.cmbType.currentText()}")

    def _onChangedCombo_Serials(self, index):
        """выбор заводского номера"""
        item = self.cmbSerial.itemData(index, Qt.ItemDataRole.UserRole)
        logger.debug(f"выбор заводского номера -> {item['Serial'] if item else 'None'}")
        # ↑ выбирает типоразмер для данного серийника
        if item and all(item.values()):
            funcs_combo.resetFilter(self.cmbType)
            condition = {'ID': item['Type']}
            funcs_combo.selectContains(self.cmbType, condition)

    def _onChangedCombo_SerialsText(self, text):
        """выбор заводского номера"""
        if not self._states['editing']['pump']:
            logger.debug(f"выбор заводского номера '{text}' по названию")
            index = self.cmbSerial.findText(text)
            self.cmbSerial.setCurrentIndex(index)
#endregion      КОМБОБОКСЫ ->

#region     ГРУППЫ ИНФОРМАЦИИ О НАСОСЕ И ИСПЫТАНИИ ->
    def _onClicked_InfoPump(self):
        """обработка нажания кнопки группы данных о насосе"""
        logger.debug(self._onClicked_InfoPump.__doc__)
        {
            self.btnPump_Edit: self._editInfo_Pump,
            self.btnPump_Save: self._saveInfo_Pump,
            self.btnPump_Cancel: self._cancelInfo_Pump
        }[self.sender()]()

    def _onClicked_InfoTest(self):
        """обработка нажания кнопки данных об испытании"""
        logger.debug(self._onClicked_InfoTest.__doc__)
        {
            self.btnTest_Edit: self._editInfo_Test,
            self.btnTest_Save: self._saveInfo_Test,
            self.btnTest_Cancel: self._cancelInfo_Test,
            self.btnTest_Order: self._lockOrder_Test
        }[self.sender()]()

    def _onClicked_SwitchMode(self):
        """нажата кнопка перехода между страницами"""
        logger.debug(self._onClicked_SwitchMode.__doc__)
        {
            self.btnGoTest: self._goToTest,
            self.btnGoInfo: self._goToInfo
        }[self.sender()]()
#endregion      <- ГРУППЫ ИНФОРМАЦИИ О НАСОСЕ И ИСПЫТАНИИ

#region     УПРАВЛЕНИЕ ИСПЫТАНИЕМ ->
    def _onClicked_PointAdd(self):
        """нажата кнопка добавления точки"""
        logger.debug(self._onClicked_PointAdd.__doc__)
        spin = self.spinPointLines
        if spin.value() == 0:
            Message.show("Внимание:", "Достигнуто максимальное кол-во точек.")
            return
        current_vals = funcs_test.getCurrentVals(self)
        if spin.value() == spin.maximum():
            self.graph_manager.setPointLines_max(current_vals[0])
        if not self.graph_manager.checkPointExists(current_vals[0]):
            self.graph_manager.markersAddKnots()
            self.graph_manager.addPointsToCharts(*current_vals)
            self.graph_manager.drawCharts(self.frameGraphTest)
            current_vals.append(self._testdata.pump_.Stages)
            funcs_table.addToTable_points(self.tablePoints, current_vals)
            spin.setValue(int(spin.value()) - 1)

    def _onClicked_PointRemove(self):
        """нажата кнопка удаления точки"""
        logger.debug(self._onClicked_PointRemove.__doc__)
        funcs_table.removeLastRow(self.tablePoints)
        if self.spinPointLines.value() == self.spinPointLines.maximum():
            self.graph_manager.setPointLines_max(0)
        self.graph_manager.markersRemoveKnots()
        self.graph_manager.removeLastPointsFromCharts()
        self.graph_manager.drawCharts(self.frameGraphTest)
        self.spinPointLines.setValue(int(self.spinPointLines.value()) + 1)

    def _onToggled_PointsMode(self):
        """переключение значений точек реальные / на ступень"""
        display = ["flw", "lft", "pwr", "eff"]
        if self.radioPointsReal.isChecked():
            display[1] = "lft_real"
            display[2] = "pwr_real"
        funcs_table.setDisplay(self.tablePoints, display)

    def _onChanged_PointsNum(self):
        """изменение порядкового номера отбиваемой точки"""
        num = int(self.spinPointLines.value())
        if self.spinPointLines.isEnabled():
            self.graph_manager.setPointLines_num(num)
        else:
            self.graph_manager.setPointLines_cur(num)

    def _onClicked_ClearCurve(self):
        """нажата кнопка удаления всех точек"""
        logger.debug(self._onClicked_ClearCurve.__doc__)
        funcs_table.clear(self.tablePoints)
        self.graph_manager.markersClearKnots()
        self.graph_manager.clearPointsFromCharts()
        self.graph_manager.drawCharts(self.frameGraphTest)

    def _onClickedTestResult_Save(self):
        """нажата кнопка сохранения результатов теста"""
        logger.debug(self._onClickedTestResult_Save.__doc__)
        self.graph_manager.saveTestdata()
        test_ = self._testdata.test_
        result = self.db_manager.writeRecord(test_.subclass, dict(test_))
        title = 'УСПЕХ' if result else 'ОШИБКА'
        message = 'Результаты сохранены' if result else 'Запись заблокирована'
        Message.show(title, message)
#endregion      <- УПРАВЛЕНИЕ ИСПЫТАНИЕМ

#region     РАБОТА С ОБОРУДОВАНИЕМ ->
    def _onAdam_Connection(self):
        """нажата кнопка подключения к ADAM5000TCP"""
        logger.debug(self._onAdam_Connection.__doc__)
        state = self.chkConnection.isChecked()
        state = self.test_manager.switchConnection(state)
        if state:
            funcs_test.switchControlsAccessible(self, False)
        self.chkConnection.setChecked(state)
        self.chkConnection.setStyleSheet(
            "QCheckBox { color: %s; }" % ("lime" if state else "red")
        )
        self.chkConnection.setText(
            "контроллер %s" % ("подключен" if state else "отключен")
        )
        self.statusAdam.setStyleSheet(
            "#statusAdam { color: 'white'; background-color: %s; }" % ("green" if state else "red")
        )
        self.pageTestControl.setEnabled(state)
        funcs_group.groupClear(self.groupTestSensors)

    def _onClicked_Engine(self):
        """нажата кнопка начала/остановки испытания"""
        logger.debug(self._onClicked_Engine.__doc__)
        state = not self.test_manager.isEngineRunning
        if not {
                True: self.test_manager.startTesting,
                False: self.test_manager.stopTesting
            }[state]():
            return
        self.btnEngine.setText({False: 'ЗАПУСК ДВИГАТЕЛЯ', True: 'ОСТАНОВКА ДВИГАТЕЛЯ'}[state])
        self.graph_manager.switchChartsVisibility(not state)
        funcs_test.switchControlsAccessible(self, state)

    def _onClicked_Purge(self):
        """нажата кнопка начала/остановки продувки"""
        logger.debug(self._onClicked_Purge.__doc__)
        state = self.btnPurge.isChecked()
        if state:
            self.radioModeO.toggle()
        self.test_manager.switchTestMode(TestMode.PURGE)
        if self.test_manager.testMode == TestMode.PURGE:
            self.progressPurge.show()
            self.progressPurge.start()
            self.pageTestControl.setToolTip("Заблокировано во время продувки")
            self.pageTestControl.setEnabled(False)
            self.statusMessage.setText("Идёт продувка ... ")
        else:
            self.progressPurge.hide()
            self.progressPurge.stop()
            self.pageTestControl.setToolTip("")
            self.pageTestControl.setEnabled(True)
            self.statusMessage.setText("...")

    def _onTick_Purge(self):
        text = self.statusMessage.text()
        text = text[1::] + text[0]
        self.statusMessage.setText(text)

    @pyqtSlot(dict)
    def _onAdam_DataReceived(self, adam_data: dict):
        """приход данных от ADAM5000TCP"""
        self.test_manager.updateSensors(adam_data, self._testdata.pump_['Stages'], self._testdata.type_['Rpm'])
        self._bindings['sens'].toWidgets()
        labels = (self.vlvAir, self.vlvWater, self.vlvTest, self.vlvF1, self.vlvF2)
        keys = (CN.VLV_AIR, CN.VLV_WTR, CN.VLV_TST, CN.VLV_1, CN.VLV_2)
        for label, key in zip(labels, keys):
            self._displayLabelState(label, adam_data[key])

    def _onToggled_Flowmeter(self, state: bool):
        """изменение текущего расходомера"""
        if not state:
            return
        logger.debug(self._onToggled_Flowmeter.__doc__)
        {
            self.radioFlow0: self.test_manager.setFlowmeter_0,
            self.radioFlow1: self.test_manager.setFlowmeter_1,
            self.radioFlow2: self.test_manager.setFlowmeter_2
        }[self.sender()]()

    def _onToggled_Rotation(self, state: bool):
        """изменение направления вращения"""
        if not state:
            return
        logger.debug(self._onToggled_Rotation.__doc__)
        self.test_manager.setEngineRotation(self.sender() is self.radioRotationR)

    def _onToggled_TestMode(self, state: bool):
        """изменение режима работы стенда"""
        if not state:
            return
        logger.debug(self._onToggled_TestMode.__doc__)
        if self.sender() == self.radioModeT:
            mode = TestMode.TEST
        else:
            mode = TestMode.IDLING
            self.radioFlow2.toggle()
        self.test_manager.switchTestMode(mode)

    def _onChanged_Sensors(self):
        """изменения значений датчиков"""
        vals = funcs_test.getCurrentVals(self)
        params = [
            {'name': 'tst_lft', 'x': vals[0], 'y': vals[1]},
            {'name': 'tst_pwr', 'x': vals[0], 'y': vals[2]}
        ]
        self.graph_manager.markersMove(params)
#endregion      <- РАБОТА С ОБОРУДОВАНИЕМ

#endregion <<= ОБРАБОТЧИКИ СОБЫТИЙ

#region ФУНКЦИИ К ОБРАБОТЧИКАМ СОБЫТИЙ =>>

#region     ДЕЙСТВИЯ С ДАННЫМИ ->
    def _loadRecord(self, record: Record, rec_id: int):
        data = self.db_manager.loadRecord(record.subclass, rec_id)
        record.load(data)

    def _clearInfo(self):
        """очистка фильтров, полей и информации о записи"""
        logger.debug(self._clearInfo.__doc__)
        funcs_combo.resetFilters_pumpInfo(self)
        funcs_group.groupClear(self.groupTestInfo)
        funcs_group.groupClear(self.groupPumpInfo)
        self.graph_manager.clearCharts()
        self.graph_manager.markersClearKnots()
        self._testdata.clear()

    def _loadInfo(self, test_id: int):
        """загрузка и отображаем информации о выбранной записи"""
        logger.debug(f"{self._loadInfo.__doc__} -> {test_id}")
        data = self.db_manager.loadRecord_All(test_id)
        self._testdata.load(data)
        self._bindings['test'].toWidgets()
        self._bindings['pump'].toWidgets()

    def _printInfo(self):
        """вывод протокола на печать"""
        logger.debug(self._printInfo.__doc__)
        if self._report:
            self._report.print(self._testdata)

    def _deleteInfo(self):
        """запрос на удаление текущей записи"""
        logger.debug(self._deleteInfo.__doc__)
        if funcs_aux.askPassword():
            test_ = self._testdata.test_
            self.db_manager.removeRecord(test_.subclass, test_.ID)
            logger.debug(f"запись № {test_.ID} удалена")
            Message.show("УСПЕХ", "Запись удалена")
            self._testlist.refresh(self.db_manager)

    def _updateInfo(self):
        """запрос на обновление текущей записи"""
        logger.debug(self._updateInfo.__doc__)
        if funcs_aux.askPassword():
            self._bindings['test'].toData()
            self.db_manager.saveInfo_Test()
            logger.debug(f"запись № {self._testdata.test_.ID} обновлена")
            Message.show("УСПЕХ", "Запись обновлена")

    def _editInfo_Pump(self):
        """запрос на редактирование данных о насосе"""
        logger.debug(self._editInfo_Pump.__doc__)
        self._states.update({
            'typeId': self._testdata.type_.ID,
            'pumpId': self._testdata.pump_.ID,
            'serial': self._testdata.pump_.Serial
        })
        self._states['editing']['pump'] = True
        funcs_group.groupClear(self.groupPumpInfo)
        funcs_group.groupLock(self.groupPumpInfo, False)
        funcs_group.groupLock(self.groupTestList, True)

    def _saveInfo_Pump(self):
        """запрос на сохранение данных о насосе"""
        logger.debug(self._saveInfo_Pump.__doc__)
        # проверка типоразмера
        type_name = self.cmbType.currentText()
        if not funcs_info.checkExists_Type(self, type_name):
            producer_name = self.cmbProducer.currentText()
            funcs_info.addNew_Type(self, type_name, producer_name)
            return
        # проверка насоса по серийному номеру
        serial = self.cmbSerial.currentText()
        pump = funcs_info.findInfo_Pump(self, serial, self._testdata.type_.ID)
        if pump:
            self._testdata.pump_.load(pump)
            self._bindings['pump'].toWidgets()
        # выполнение процедуры сохранения
        elif not funcs_info.saveInfo_Pump(self, self._bindings['pump'], self._testdata.pump_):
            return
        self._states['editing']['pump'] = False
        funcs_group.groupLock(self.groupPumpInfo, True)
        funcs_group.groupLock(self.groupTestList, any(self._states['editing'].values()))

    def _cancelInfo_Pump(self):
        """отмена изменений данных о насосе"""
        logger.debug(self._cancelInfo_Pump.__doc__)
        funcs_combo.resetFilters_pumpInfo(self)
        data = self.db_manager.loadRecord_Pump(self._states['pumpId'])
        self._testdata.pump_.load(data[0])
        self._testdata.type_.load(data[1])
        self._states.update({
            'typeId': self._testdata.type_.ID,
            'pumpId': self._testdata.pump_.ID,
            'serial': self._testdata.pump_.Serial
        })
        self._bindings['pump'].toWidgets()
        self._states['editing']['pump'] = False
        funcs_group.groupLock(self.groupPumpInfo, True)
        funcs_group.groupLock(self.groupTestList, any(self._states['editing'].values()))

    def _editInfo_Test(self):
        """запрос на редактирование данных об испытании"""
        logger.debug(self._editInfo_Test.__doc__)
        self._states['editing']['test'] = True
        self._states.update({'testId': self._testdata.test_.ID})
        funcs_group.groupLock(self.groupTestInfo, False)
        funcs_group.groupLock(self.groupTestList, True)
        self.txtOrderNum.setEnabled(False)

    def _saveInfo_Test(self):
        """запрос на сохранение данных об испытании"""
        logger.debug(self._saveInfo_Test.__doc__)
        # проверка номера наряд-заказа
        order_num = self.txtOrderNum.text()
        test, action = funcs_info.findInfo_Test(self, order_num)
        if test and action == "select":
            self._testdata.test_.load(test)
            self._bindings['test'].toWidgets()
        # выполнение процедуры сохранения
        elif not funcs_info.saveInfo_Test(
            self, self._bindings['test'], self._testdata.test_, action=="update"
            ):
            return
        self._states['editing']['test'] = False
        self._testlist.refresh(self.db_manager)
        self.graph_manager.displayCharts(self.frameGraphInfo)
        funcs_group.groupLock(self.groupTestInfo, True)
        funcs_group.groupLock(self.groupTestList, any(self._states['editing'].values()))

    def _cancelInfo_Test(self):
        """отмена изменений данных об насосе"""
        logger.debug(self._cancelInfo_Test.__doc__)
        self._states['editing']['test'] = False
        self._bindings['test'].toWidgets()
        funcs_group.groupLock(self.groupTestInfo, True)
        funcs_group.groupLock(self.groupTestList, any(self._states['editing'].values()))

    def _lockOrder_Test(self, state=None):
        """переключение блокировки поля наряд-заказа"""
        if state is None:
            state = not self.txtOrderNum.isEnabled()
        logger.debug(f"{self._lockOrder_Test.__doc__} -> {state}")
        self.txtOrderNum.setEnabled(state)
#endregion      <-- ДЕЙСТВИЯ С ДАННЫМИ

#region     ДЕЙСТВИЯ ОТНОСЯЩИЕСЯ К ИСПЫТАНИЮ ->
    def _goToTest(self):
        """переход к испытанию"""
        logger.debug(self._goToTest.__doc__)
        self.stackedWidget.setCurrentIndex(1)
        self.graph_manager.drawCharts(self.frameGraphTest)
        self.graph_manager.markersReposition()
        self.graph_manager.switchChartsVisibility(True)

    def _goToInfo(self):
        """возврат к информации"""
        logger.debug(self._goToInfo.__doc__)
        self.stackedWidget.setCurrentIndex(0)
        self._testlist.setCurrentTest(self._testdata.test_['ID'])
        self._testlist.refresh(self.db_manager)
        self.graph_manager.drawCharts(self.frameGraphInfo)
#endregion      <-- ДЕЙСТВИЯ ОТНОСЯЩИЕСЯ К ИСПЫТАНИЮ

#endregion <<= ФУНКЦИИ К ОБРАБОТЧИКАМ СОБЫТИЙ
