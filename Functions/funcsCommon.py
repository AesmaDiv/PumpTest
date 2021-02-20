from datetime import datetime
from PyQt5.Qt import QModelIndex
from GUI.Models import ListModel
from Functions import funcsTable, funcsMessages, funcsWindow, funcsSpinner
from AppClasses import Infos
from AesmaLib import aesma_funcs
from AesmaLib.journal import Journal
from Globals import gvars


class Filters:
    @staticmethod
    def apply(conditions: dict = None):
        if conditions is None:
            filter_id = gvars.wnd_main.txtFilter_ID.text()
            filter_datetime = gvars.wnd_main.txtFilter_DateTime.text()
            filter_ordernum = gvars.wnd_main.txtFilter_OrderNum.text()
            filter_serial = gvars.wnd_main.txtFilter_Serial.text()
            conditions = [filter_id, filter_datetime, filter_ordernum, filter_serial]
        gvars.wnd_main.tests_filter.applyFilter(conditions)

    @staticmethod
    def reset():
        Infos.Info.clear(gvars.wnd_main.groupTestList)
        Infos.Test.clear(gvars.wnd_main.groupTestInfo)
        Infos.Pump.clear(gvars.wnd_main.groupPumpInfo)
        Infos.Type.clear()
        gvars.wnd_main.tests_filter.applyFilter()
        funcsTable.select_row(gvars.wnd_main.tableTests, -1)

    @staticmethod
    def switch_others():
        if gvars.wnd_main.radioOrderNum.isChecked():
            gvars.wnd_main.tableTests.horizontalHeader().hideSection(3)
            gvars.wnd_main.tableTests.horizontalHeader().showSection(2)
            gvars.wnd_main.txtFilter_OrderNum.show()
            gvars.wnd_main.txtFilter_Serial.hide()
        else:
            gvars.wnd_main.tableTests.horizontalHeader().hideSection(2)
            gvars.wnd_main.tableTests.horizontalHeader().showSection(3)
            gvars.wnd_main.txtFilter_OrderNum.hide()
            gvars.wnd_main.txtFilter_Serial.show()


def select_test(test_id: int):
    model: ListModel = gvars.wnd_main.tableTests.model().sourceModel()
    index: QModelIndex = model.get_row_contains(0, test_id)
    gvars.wnd_main.tableTests.selectRow(index.row())


def save_pump():
    if Infos.Pump.save():
        serial = gvars.dictPump['Serial']
        funcsMessages.show("Успех", "Насос №", serial, "добавлен в БД.")
        funcsWindow.fill_spinner(gvars.wnd_main.cmbSerials, 'Pumps', ['ID', 'Serial', 'Type'], 1, order_by='ID Asc')
        funcsSpinner.select_item_containing(gvars.wnd_main.cmbSerials, serial)
        return True
    return False


def set_current_date():
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gvars.wnd_main.txtDateTime.setText(today)


def parse_points():
    try:
        gvars.dictType['Flows'] = parse_string_to_floats('Flows_String')
        gvars.dictType['Lifts'] = parse_string_to_floats('Lifts_String')
        gvars.dictType['Powers'] = parse_string_to_floats('Powers_String')
        return True
    except BaseException as error:
        Journal.log(__name__ + " error: " + str(error))
        return False


def parse_string_to_floats(name: str):
    string = gvars.dictType[name]
    result = [aesma_funcs.safe_parse_to_float(value) for value in string.split(',')]
    return result


