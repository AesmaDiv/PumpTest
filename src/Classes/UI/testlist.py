"""
    Модуль содержит класс списка тестов
"""
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtWidgets import QHeaderView, QMenu
from PyQt6.QtGui import QCursor

from Classes.UI.funcs import funcs_table


class TestList(QObject):
    """Класс списка тестов"""
    _signalSelection = pyqtSignal(dict, name="selectionChanged")
    _signalMenu = pyqtSignal(str, name="menuSelected")

    def __init__(self, parent) -> None:
        super().__init__(parent=parent)
        self._table = None

    def build(self):
        """создание структуры списока тестов"""
        wnd = self.parent()
        self._table = wnd.tableTests
        for i, val in enumerate((50, 150, 80)):
            self._table.setColumnWidth(i, val)
        tests_display = ['ID', 'DateTime', 'OrderNum', 'Serial']
        tests_headers = ['№', 'Дата-Время', 'Наряд-Заказ', 'Заводской номер']
        tests_headers_sizes = [50, 150, 200, 200]
        tests_resizes = [QHeaderView.ResizeMode.Fixed, QHeaderView.ResizeMode.Fixed,
                        QHeaderView.ResizeMode.Stretch, QHeaderView.ResizeMode.Stretch]
        tests_data = None
        wnd.tests_filter = funcs_table.models.FilterModel(wnd)
        wnd.tests_filter.setDynamicSortFilter(True)
        funcs_table.create(
            self._table,
            funcs_table.TableParams(
                display=tests_display,
                filter_proxy=wnd.tests_filter,
                data=tests_data,
                headers=tests_headers,
                headers_sizes=tests_headers_sizes,
                headers_resizes=tests_resizes
            )
        )
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.selectionModel().currentChanged.connect(self._onSelectionChanged)
        self._table.customContextMenuRequested.connect(self._onMenuSelected)

    def refresh(self, db_manager):
        """заполняет список тестов"""
        tests_data = db_manager.getTestsList()
        funcs_table.setData(self._table, tests_data)
        funcs_table.selectRow(self._table, 0)
        # gvars.db.set_permission('Tests', False)

    def filterApply(self, conditions=None):
        """применяет фильтр к списку тестов"""
        self.parent().tests_filter.applyFilter(conditions)
        if not conditions:
            funcs_table.selectRow(self._table, -1)

    def filterSwitch(self):
        """переключает список тестов (зав.номер/наряд-заказ)"""
        if self.parent().radioOrderNum.isChecked():
            self._table.horizontalHeader().hideSection(3)
            self._table.horizontalHeader().showSection(2)
            self.parent().txtFilter_OrderNum.show()
            self.parent().txtFilter_Serial.hide()
        else:
            self._table.horizontalHeader().hideSection(2)
            self._table.horizontalHeader().showSection(3)
            self.parent().txtFilter_OrderNum.hide()
            self.parent().txtFilter_Serial.show()

    def setCurrentTest(self, test_id: int):
        """выбирает в списке тестов запись и указаным ID"""
        row = 0
        if test_id:
            model = self._table.model().sourceModel()
            index = model.getRowContains(0, test_id)
            row = index.row()
        self._table.selectRow(row)

    def _onSelectionChanged(self):
        item = funcs_table.getRow(self._table)
        if item:
            self._signalSelection.emit(item)

    def _onMenuSelected(self):
        """создание контекстрого меню и обработка"""
        menu = QMenu()
        action = {
            menu.addAction("Распечатать"): "print",
            menu.addAction("Удалить"): "delete",
            menu.addAction("Переписать"): "update"
        }.get(menu.exec(QCursor.pos()), "")
        self._signalMenu.emit(action)
