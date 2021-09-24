"""
    Модуль содержит функции основного окна программы
"""
import os
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtWidgets import QHeaderView, QGroupBox, QMainWindow, QWidget, QTableView
from PyQt5.QtWidgets import QPushButton, QLineEdit, QComboBox
from PyQt5.QtCore import Qt, QRegExp, QPointF
from Classes.report import Report
from Classes.event_manager import EventManager
from Classes.wnd_funcs import WindowFunctions
from Classes.record import TestInfo
from Classes.graph_manager import GraphManager
from Classes.db_manager import DBManager
from Classes.table_manager import TableManager
from Classes.table_vibr_manager import VibrationTableManager
from Classes.table_points_manager import PointsTableManager
from Classes.combo_manager import ComboManager
from Classes.testlist_manager import TestListManager
from Classes.group_manager import GroupManager

from AesmaLib.journal import Journal


class WindowManager(QMainWindow):
    """ Класс описания функционала главного окна приложения """
    def __init__(self, pathes, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.is_displaying = dict.fromkeys(['Producer','Type','Serial'], False)
        try:
            path = os.path.dirname(__file__)
            path += "/UI/mainwindow.ui"
            uic.loadUi(path, self)
        except IOError as error:
            Journal.log(__name__, "::\t", "ошибка:", str(error))
        self._db_m = DBManager(pathes['DB'])
        self._info = TestInfo(self._db_m)
        self._gf_m = GraphManager(self._info)
        self._rprt = Report(pathes['TEMPLATE'], self._gf_m, self._info)
        self._ev_m = EventManager(self)
        self.funcs = WindowFunctions(self)

    @Journal.logged
    def prepare(self):
        """ инициализирует и подготавливает компоненты главного окна """
        TestListManager.init(self._wnd)
        TestListManager.fill(self._wnd, self._db_m)
        ComboManager.fill(self._wnd, self._db_m)
        PointsTableManager.init(self._wnd)
        VibrationTableManager.init(self._wnd)
        self.init_graph_markers()
        self._ev_m.register_events()
        self.set_color_scheme()

    @Journal.logged
    def show(self):
        """ отображает главное окно """
        self._wnd.show()
        self._wnd.move(1, 1)
        TestListManager.filter_switch(self._wnd)
        GroupManager.group_lock(self._wnd.groupTestInfo, True)
        GroupManager.group_lock(self._wnd.groupPumpInfo, True)
        self.switch_test_running_state(False)

    @Journal.logged
    def set_color_scheme(self):
        """ устанавливает цветовую схему """
        # gvars.wnd_main.stackedWidget.setStyleSheet("QStackedWidget { background: #404040; }")
        # style: str = "QComboBox { color: #ffffff; }" \
        #              "QComboBox:!editable { color: #dddddd; }"
        # gvars.wnd_main.groupTestInfo.setStyleSheet(style)
        # gvars.wnd_main.groupPumpInfo.setStyleSheet(style)
        pass

    def init_graph_markers(self):
        """ добавление маркеров на график """
        self._wnd.gridGraphTest.addWidget(self._gf_m.markers(), 0, 0)

    def display_sensors(self, sensors: dict):
        """ отображает показания датчиков """
        self._wnd.txtRPM.setText(str(sensors['rpm']))
        self._wnd.txtTorque.setText(str(sensors['torque']))
        self._wnd.txtPsiIn.setText(str(sensors['pressure_in']))
        self._wnd.txtPsiOut.setText(str(sensors['pressure_out']))
        self._wnd.txtFlow05.setText(str(sensors['flw05']))
        self._wnd.txtFlow1.setText(str(sensors['flw1']))
        self._wnd.txtFlow2.setText(str(sensors['flw2']))

    @Journal.logged
    def display_test(self, test_id: int):
        """ отображает информацию о тесте """
        Journal.log(f"{__name__}::\t загружает информацию о тесте --> {test_id}")
        if self._info.test_.load(test_id):
            self.display_test_data()
            GroupManager.group_display(self._wnd.groupTestInfo, self._info.test_)
            GroupManager.group_lock(self._wnd.groupTestInfo, True)
            self.display_pump(self._info.test_['Pump'])

    def display_test_data(self):
        """ отображение точек испытания в таблице """
        TableManager.clear(self._wnd.tablePoints)
        for i in range(self._info.test_.num_points()):
            flw = self._info.test_.values_flw[i]
            lft = self._info.test_.values_lft[i]
            pwr = self._info.test_.values_pwr[i]
            eff = self._gf_m.calculate_effs([flw], [lft], [pwr])[0]
            PointsTableManager.add(self._wnd, flw, lft, pwr, eff)
        VibrationTableManager.add(self._wnd, self._info.test_.values_vbr)

    def display_pump(self, pump_id: int):
        """ отображает информацию о насосе """
        Journal.log(f"{__name__}::\t загружает информацию о насосе --> {pump_id}")
        if self._info.pump_.load(pump_id):
            type_id = self._info.pump_['Type']
            Journal.log(f"{__name__}::\t загружает информацию о типе --> {type_id}")
            if self._info.type_.load(type_id):
                GroupManager.group_display(self._wnd.groupPumpInfo, self._info.pump_)
                GroupManager.group_lock(self._wnd.groupPumpInfo, True)
                self._wnd.groupTestFrame.setTitle(self._info.type_.Name)

    def display_test_deltas(self):
        """ отображение результата испытания """
        test_result = self.funcs.generate_result_text()
        self._wnd.lblTestResult.setText(test_result)

    def display_test_vibrations(self):
        """ отображение показаний вибрации """
        TableManager.clear(self._wnd.tableVibrations)

    @Journal.logged
    def save_test_info(self):
        """ сохраняет информацию о насосе """
        Journal.log(f"{__name__}::\t сохраняет информацию о новом тесте")
        self._info.test_.clear()
        self._info.test_['Pump'] = self._info.pump_['ID']
        GroupManager.group_save(self._wnd.groupTestInfo, self._info.test_)
        GroupManager.group_lock(self._wnd.groupTestInfo, True)
        self._info.test_.save()

    @Journal.logged
    def save_pump_info(self) -> bool:
        """ сохраняет информацию о насосе """
        GroupManager.group_save(self._wnd.groupPumpInfo, self._info.pump_)
        GroupManager.group_lock(self._wnd.groupPumpInfo, True)
        return self._info.pump_.save()

    def clear_record(self, also_clear_classes: bool):
        """ очищает отображаемую информацию и сами записи """
        GroupManager.group_clear(self._wnd.groupTestInfo)
        GroupManager.group_clear(self._wnd.groupPumpInfo)
        if also_clear_classes:
            self._info.test_.clear()
            self._info.pump_.clear()
            self._info.type_.clear()

    def switch_test_running_state(self, state):
        """ переключение состояния испытания (запущен/остановлен) """
        # if is_logged: Journal.log(__name__, "::\tпереключение состояния теста в",
        #     str(state))
        msg = {False: 'ЗАПУСК ДВИГАТЕЛЯ', True: 'ОСТАНОВКА ДВИГАТЕЛЯ'}
        wnd = self._wnd
        wnd.btnTest.setText(msg[state])
        wnd.btnGoBack.setEnabled(not state)

    def get_current_vals(self):
        """ получение значений расхода, напора и мощности из соотв.полей """
        flw = self._parse_float(self._wnd.txtFlow.text())
        lft = self._parse_float(self._wnd.txtLift.text())
        pwr = self._parse_float(self._wnd.txtPower.text())
        eff = self._gf_m.calculate_effs([flw], [lft], [pwr])[0]
        return (flw, lft, pwr, eff)

    def display_current_marker_point(self, data: dict):
        """ отображение текущих значений маркера в соотв.полях """
        name = list(data.keys())[0]
        point: QPointF = list(data.values())[0]
        if name == 'test_lft':
            self._wnd.txtFlow.setText('%.4f' % point.x())
            self._wnd.txtLift.setText('%.4f' % point.y())
        elif name == 'test_pwr':
            self._wnd.txtPower.setText('%.4f' % point.y())

    def switch_points_stages_real(self):
        """ переключение таблицы точек на ступень / реальные """
        wnd = self._wnd
        data = TableManager.get_data(wnd.tablePoints)
        if data:
            if wnd.radioPointsReal.isChecked():
                func = lambda x: (x * self._info.pump_['Stages'])
            else:
                func = lambda x: (x / self._info.pump_['Stages'])
            for item in data:
                item['lft'] = round(func(item['lft']), 2)
                item['pwr'] = round(func(item['pwr']), 2)
            TableManager.set_data(wnd.tablePoints, data)

    @staticmethod
    def _parse_float(text: str):
        """ безопасная конвертация строки в число с пл.запятой """
        try:
            result = float(text)
        except (ValueError, TypeError):
            result = 0.0
        return result
