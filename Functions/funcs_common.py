"""
    Модуль содержит функции общего назначения
    всякое-разное
"""
from datetime import datetime
from Functions import funcs_messages, funcs_db
from Globals import gvars


def check_exists_serial():
    """ возвращает ID записи с введенным номером наряд-заказа"""
    wnd = gvars.wnd_main
    serial = wnd.cmbSerial.currentText()
    pump_id = funcs_db.get_value('Pumps', 'ID', {'Serial': serial})
    if pump_id:
        choice =  funcs_messages.ask(
            "Внимание",
            "Насос с таким заводским номером "
            "уже присутствует в базе данных.\n"
            "Хотите выбрать его?",
            "Выбрать", "Отмена"
        )
        return pump_id['ID'], choice
    return 0, False


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
    """ устанавливает текущую дату-время в соотв.поле """
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gvars.wnd_main.txtDateTime.setText(today)

def generate_result_text():
    """ генерирует миниотчёт об испытании """
    result = ""
    chart = gvars.pump_graph.get_chart('test_eff')
    if gvars.rec_test['Flows'] and chart:
        spline = chart.getSpline()
        curve = chart.regenerateCurve()
        nom = gvars.rec_type['Nom']
        eff_nom = float(spline(nom))
        eff_max = float(max(curve[1]))
        eff_del = abs(eff_max - eff_nom)
        result = \
        f"КПД.ном = {round(eff_nom, 2)}%\n" + \
        f"КПД.мах = {round(eff_max, 2)}%\n" + \
        f"КПД.Δ   = {round(eff_del, 2)}%"
    return result
