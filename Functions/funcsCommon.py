from datetime import datetime
from PyQt5.Qt import QModelIndex
from GUI.Models import ListModel
from Functions import funcsTable, funcsMessages, funcs_wnd, funcsSpinner
from AesmaLib import aesma_funcs
from AesmaLib.journal import Journal
from Globals import gvars


def select_test(test_id: int):
    model: ListModel = gvars.wnd_main.tableTests.model().sourceModel()
    index: QModelIndex = model.get_row_contains(0, test_id)
    gvars.wnd_main.tableTests.selectRow(index.row())


def save_pump():
    wnd = gvars.wnd_main
    if gvars.rec_pump.save():
        serial = gvars.rec_pump['Serial']
        funcsMessages.show("Успех", "Насос №", serial, "добавлен в БД.")
        db_params = {'columns': ['ID', 'Serial', 'Type'], 'order': 'ID Asc'}
        funcs_wnd.fill_spinner(wnd.cmbSerial, 'Pumps', db_params, 1)
        funcsSpinner.select_item_containing(wnd.cmbSerial, serial)
        return True
    return False


def set_current_date():
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gvars.wnd_main.txtDateTime.setText(today)


def parse_points():
    try:
        gvars.rec_type['Flows'] = parse_string_to_floats('Flows_String')
        gvars.rec_type['Lifts'] = parse_string_to_floats('Lifts_String')
        gvars.rec_type['Powers'] = parse_string_to_floats('Powers_String')
        return True
    except BaseException as error:
        Journal.log(__name__ + " error: " + str(error))
        return False


def parse_string_to_floats(name: str):
    string = gvars.rec_type[name]
    result = [aesma_funcs.safe_parse_to_float(value) for value in string.split(',')]
    return result


