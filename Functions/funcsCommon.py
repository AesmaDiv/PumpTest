from datetime import datetime
from PyQt5.Qt import QModelIndex
from GUI.models import ListModel
from Functions import funcsTable, funcs_messages, funcs_wnd, funcs_db
from AesmaLib import aesma_funcs
from AesmaLib.journal import Journal
from Globals import gvars


def check_exists_serial(with_select=False):
    """ возвращает ID записи с введенным номером наряд-заказа"""
    wnd = gvars.wnd_main
    serial = wnd.cmbSerial.currentText()
    pump_id = funcs_db.get_value('Pumps', 'ID', {'Serial': serial})
    if pump_id:
        if with_select:
            choice =  funcs_messages.ask(
                "Внимание",
                "Насос с таким заводским номером "
                "уже присутствует в базе данных.\n"
                "Хотите выбрать его?",
                "Выбрать", "Отмена"
            )
            if choice:
                funcs_wnd.display_pump(pump_id['ID'])
        return pump_id['ID']
    return 0


def check_exists_ordernum(with_select=False):
    """ возвращает ID записи с введенным номером наряд-заказа"""
    wnd = gvars.wnd_main
    order_num = wnd.txtOrderNum.text()
    test_id = funcs_db.get_value('Tests', 'ID', {'OrderNum': order_num})
    if test_id:
        if with_select:
            choice =  funcs_messages.choice(
                "Внимание",
                "Запись с таким наряд-заказом "
                "уже присутствует в базе данных.\n"
                "Хотите выбрать её или создать новую?",
                ("Выбрать", "Создать", "Отмена")
            )
            if not choice == 2:
                select_test(test_id['ID'])
                if choice == 1:
                    set_current_date()
        return test_id['ID']
    return 0


def select_test(test_id: int):
    """ выбирает в списке тестов запись и указаным ID """
    model = gvars.wnd_main.tableTests.model().sourceModel()
    index = model.get_row_contains(0, test_id)
    gvars.wnd_main.tableTests.selectRow(index.row())


def set_current_date():
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gvars.wnd_main.txtDateTime.setText(today)
