"""
    Модуль содержит классы фильтрации отображаемой информации
"""
from Functions import funcs_wnd, funcsTable
from Globals import gvars

class TestListFilters:
    """ Класс фильтрации для списка испытаний """
    @staticmethod
    def apply(conditions: dict = None):
        """ применяет фильтры """
        wnd = gvars.wnd_main
        if conditions is None:
            filter_id = wnd.txtFilter_ID.text()
            filter_datetime = wnd.txtFilter_DateTime.text()
            filter_ordernum = wnd.txtFilter_OrderNum.text()
            filter_serial = wnd.txtFilter_Serial.text()
            conditions = [filter_id, filter_datetime, filter_ordernum, filter_serial]
        wnd.tests_filter.applyFilter(conditions)

    @staticmethod
    def reset():
        """ сбрасывает фильтры """
        wnd = gvars.wnd_main
        funcs_wnd.group_clear(wnd.groupTestList)
        funcs_wnd.clear_record(True)
        wnd.tests_filter.applyFilter()
        funcsTable.select_row(wnd.tableTests, -1)

    @staticmethod
    def switch_others():
        """ переключает отображение заводской номер/наряд заказ """
        wnd = gvars.wnd_main
        if wnd.radioOrderNum.isChecked():
            wnd.tableTests.horizontalHeader().hideSection(3)
            wnd.tableTests.horizontalHeader().showSection(2)
            wnd.txtFilter_OrderNum.show()
            wnd.txtFilter_Serial.hide()
        else:
            wnd.tableTests.horizontalHeader().hideSection(2)
            wnd.tableTests.horizontalHeader().showSection(3)
            wnd.txtFilter_OrderNum.hide()
            wnd.txtFilter_Serial.show()
