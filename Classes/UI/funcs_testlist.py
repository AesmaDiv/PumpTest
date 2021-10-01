"""
    Модуль содержит функции для работы со списком тестов
"""
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtCore import Qt
from Classes.UI import funcs_table, funcs_group
from AesmaLib.journal import Journal


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
    window.tests_filter = funcs_table.models.FilterModel(window)
    window.tests_filter.setDynamicSortFilter(True)
    funcs_table.create(window.tableTests, display=tests_display,
                    filter_proxy=window.tests_filter, data=tests_data,
                    headers=tests_headers, headers_sizes=tests_headers_sizes,
                    headers_resizes=tests_resizes)
    window.tableTests.setContextMenuPolicy(Qt.CustomContextMenu)


@Journal.logged
def fill(window, db_manager):
    """ заполняет список тестов """
    tests_data = db_manager.get_tests_list()
    funcs_table.set_data(window.tableTests, tests_data)
    funcs_table.select_row(window.tableTests, 0)
    # gvars.db.set_permission('Tests', False)


def filter_apply(window, conditions: dict=None):
    """ применяет фильтр к списку тестов """
    if conditions is None:
        filter_id = window.txtFilter_ID.text()
        filter_datetime = window.txtFilter_DateTime.text()
        filter_ordernum = window.txtFilter_OrderNum.text()
        filter_serial = window.txtFilter_Serial.text()
        conditions = [filter_id, filter_datetime, filter_ordernum, filter_serial]
    window.tests_filter.applyFilter(conditions)


def filter_reset(window, data_manager):
    """ сбрасывает фильтр списка тестов """
    funcs_group.group_clear(window.groupTestList)
    funcs_group.group_clear(window.groupTestInfo)
    funcs_group.group_clear(window.groupPumpInfo)
    data_manager.clear_record()
    window.tests_filter.applyFilter()
    funcs_table.select_row(window.tableTests, -1)


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


def select_test(window, test_id: int):
    """ выбирает в списке тестов запись и указаным ID """
    model = window.tableTests.model().sourceModel()
    index = model.get_row_contains(0, test_id)
    window.tableTests.selectRow(index.row())
