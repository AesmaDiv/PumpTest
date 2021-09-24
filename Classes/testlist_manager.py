from PyQt5.QtWidgets import QHeaderView, QGroupBox, QWidget, QTableView
from PyQt5.QtWidgets import QPushButton, QLineEdit, QComboBox
from PyQt5.QtCore import Qt, QRegExp, QPointF
from Classes.table_manager import TableManager
from Classes.group_manager import GroupManager

from AesmaLib.journal import Journal
from AesmaLib.database import QueryParams
from GUI import models

class TestListManager:
    # sql запрос для списка тестов

    @staticmethod
    @Journal.logged
    def init(window):
        """ инициализирует список тестов """
        for i, val in enumerate((50, 150, 80)):
            window.tableTests.setColumnWidth(i, val)
        tests_display = ['ID', 'DateTime', 'OrderNum', 'Serial']
        tests_headers = ['№', 'Дата-Время', 'Наряд-Заказ', 'Заводской номер']
        tests_headers_sizes = [50, 150, 200, 200]
        tests_resizes = [QHeaderView.Fixed, QHeaderView.Fixed,
                        QHeaderView.Stretch, QHeaderView.Stretch]
        tests_data = None
        window.tests_filter = models.FilterModel(window)
        window.tests_filter.setDynamicSortFilter(True)
        TableManager.create(window.tableTests, display=tests_display,
                        filter_proxy=window.tests_filter, data=tests_data,
                        headers=tests_headers, headers_sizes=tests_headers_sizes,
                        headers_resizes=tests_resizes)
        window.tableTests.setContextMenuPolicy(Qt.CustomContextMenu)

    @staticmethod
    @Journal.logged
    def fill(window, db_manager):
        """ заполняет список тестов """
        testlist_query: str =\
        """Select Tests.ID, Tests.DateTime, Tests.OrderNum, Pumps.Serial
        From Tests
        Inner Join Pumps on Pumps.ID = Tests.Pump
        Order by Tests.ID Desc
        Limit 100"""
        tests_data = None
        tests_data = db_manager.execute_query(testlist_query)
        TableManager.set_data(window.tableTests, tests_data)
        TableManager.select_row(window.tableTests, 0)
        # gvars.db.set_permission('Tests', False)

    @staticmethod
    def filter_apply(window, conditions: dict=None):
        """ применяет фильтр к списку тестов """
        if conditions is None:
            filter_id = window.txtFilter_ID.text()
            filter_datetime = window.txtFilter_DateTime.text()
            filter_ordernum = window.txtFilter_OrderNum.text()
            filter_serial = window.txtFilter_Serial.text()
            conditions = [filter_id, filter_datetime, filter_ordernum, filter_serial]
        window.tests_filter.applyFilter(conditions)

    @staticmethod
    def filter_reset(window):
        """ сбрасывает фильтр списка тестов """
        GroupManager.group_clear(window.groupTestList)
        window.clear_record(True)
        window.tests_filter.applyFilter()
        TableManager.select_row(window.tableTests, -1)

    @staticmethod
    def filter_switch(window):
        """ переключает список тестов (зав.номер/наряд-заказ) """
        if window.radioOrderNum.isChecked():
            window.tableTests.horizontalHeader().hideSection(3)
            window.tableTests.horizontalHeader().showSection(2)
            window.txtFilter_OrderNum.show()
            window.txtFilter_Serial.hide()
        else:
            window.tableTests.horizontalHeader().hideSection(2)
            window.tableTests.horizontalHeader().showSection(3)
            window.txtFilter_OrderNum.hide()
            window.txtFilter_Serial.show()
