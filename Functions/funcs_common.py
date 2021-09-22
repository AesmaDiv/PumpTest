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
    gvars.rec_deltas.clear()
    result_lines = []
    if gvars.rec_test['Flows']:
        generate_deltas_report(result_lines)
        generate_effs_report(result_lines)
    return '\n'.join(result_lines)


def generate_deltas_report(lines: list):
    """ расчитывает отклонения для напора и мощности """
    for name, title in zip(('lft', 'pwr'),('Напор', 'Мощность')):
        calculate_deltas_for(name)
        string = f'\u0394 {title}, %\t'
        string += '\t{:>10.2f}\t{:>10.2f}\t{:>10.2f}'.format(*gvars.rec_deltas[name])
        lines.append(string)


def generate_effs_report(lines: list):
    """ расчитывает отклонения для кпд """
    chart = gvars.pump_graph.get_chart('test_eff')
    spline = chart.getSpline()
    curve = chart.regenerateCurve()
    nom = gvars.rec_type['Nom']
    eff_nom = float(spline(nom))
    eff_max = float(max(curve['y']))
    eff_dlt = abs(eff_max - eff_nom)
    string = 'Отклонение КПД от номинального, %\t{:>10.2f}'.format(eff_dlt)
    lines.append(string)
    gvars.rec_deltas['eff'] = eff_dlt


def calculate_deltas_for(chart_name: str):
    """ расчитывает отклонения для указанной характеристики """
    names = (f'test_{chart_name}', f'{chart_name}')
    ranges = ('Min', 'Nom', 'Max')
    get_val = lambda spl, rng: float(spl(gvars.rec_type[rng]))
    get_dlt = lambda tst, etl: round((tst / etl * 100 - 100), 2)
    vals = []
    for name in names:
        spln = gvars.pump_graph.get_chart(f'{name}').getSpline()
        vals.append([get_val(spln, rng) for rng in ranges])
    result = [get_dlt(x, y) for x, y in zip(vals[0], vals[1])]
    gvars.rec_deltas[name] = result
