from datetime import datetime
from PyQt5.Qt import QModelIndex
from AppClasses.UI.Models import ListModel
from AppClasses.Functions import funcsTable, funcsMessages, funcsWindow, funcsSpinner
from AppClasses import Infos
from AesmaLib import Journal, AesmaFuncs
import vars


class Filters:
    @staticmethod
    def apply(conditions: dict = None):
        if conditions is None:
            filter_id = vars.wnd_main.txtFilter_ID.text()
            filter_datetime = vars.wnd_main.txtFilter_DateTime.text()
            filter_ordernum = vars.wnd_main.txtFilter_OrderNum.text()
            filter_serial = vars.wnd_main.txtFilter_Serial.text()
            conditions = [filter_id, filter_datetime, filter_ordernum, filter_serial]
        vars.wnd_main.tests_filter.applyFilter(conditions)

    @staticmethod
    def reset():
        Infos.Info.clear(vars.wnd_main.groupTestList)
        Infos.Test.clear(vars.wnd_main.groupTestInfo)
        Infos.Pump.clear(vars.wnd_main.groupPumpInfo)
        Infos.Type.clear()
        vars.wnd_main.tests_filter.applyFilter()
        funcsTable.select_row(vars.wnd_main.tableTests, -1)

    @staticmethod
    def switch_others():
        if vars.wnd_main.radioOrderNum.isChecked():
            vars.wnd_main.tableTests.horizontalHeader().hideSection(3)
            vars.wnd_main.tableTests.horizontalHeader().showSection(2)
            vars.wnd_main.txtFilter_OrderNum.show()
            vars.wnd_main.txtFilter_Serial.hide()
        else:
            vars.wnd_main.tableTests.horizontalHeader().hideSection(2)
            vars.wnd_main.tableTests.horizontalHeader().showSection(3)
            vars.wnd_main.txtFilter_OrderNum.hide()
            vars.wnd_main.txtFilter_Serial.show()


def select_test(test_id: int):
    model: ListModel = vars.wnd_main.tableTests.model().sourceModel()
    index: QModelIndex = model.get_row_contains(0, test_id)
    vars.wnd_main.tableTests.selectRow(index.row())


def save_pump():
    if Infos.Pump.save():
        serial = vars.dictPump['Serial']
        funcsMessages.show("Успех", "Насос №", serial, "добавлен в БД.")
        funcsWindow.fill_spinner(vars.wnd_main.cmbSerials, 'Pumps', ['ID', 'Serial', 'Type'], 1, order_by='ID Asc')
        funcsSpinner.select_item_containing(vars.wnd_main.cmbSerials, serial)
        return True
    return False


def set_current_date():
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vars.wnd_main.txtDateTime.setText(today)


def parse_points():
    try:
        vars.dictType['Flows'] = parse_string_to_floats('Flows_String')
        vars.dictType['Lifts'] = parse_string_to_floats('Lifts_String')
        vars.dictType['Powers'] = parse_string_to_floats('Powers_String')
        return True
    except BaseException as error:
        Journal.log(__name__ + " error: " + str(error))
        return False


def parse_string_to_floats(name: str):
    string = vars.dictType[name]
    result = [AesmaFuncs.safe_parse_to_float(value) for value in string.split(',')]
    return result


