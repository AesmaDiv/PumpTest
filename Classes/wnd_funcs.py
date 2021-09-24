from datetime import datetime
from Classes.message import Message


class WindowFunctions:
    def __init__(self, parent) -> None:
        self._parent = parent
        self._wnd = parent._wnd
        self._info = parent._info
        self._gf_m = parent._gf_m
        self._db_m = parent._db_m

    def check_exists_serial(self):
        """ возвращает ID записи с введенным номером наряд-заказа"""
        serial = self._wnd.cmbSerial.currentText()
        pump_id = self._db_m.get_value('Pumps', 'ID', {'Serial': serial})
        if pump_id:
            choice =  Message.ask(
                "Внимание",
                "Насос с таким заводским номером "
                "уже присутствует в базе данных.\n"
                "Хотите выбрать его?",
                "Выбрать", "Отмена"
            )
            return pump_id['ID'], choice
        return 0, False

    def check_exists_ordernum(self, with_select=False):
        """ возвращает ID записи с введенным номером наряд-заказа"""
        order_num = self._wnd.txtOrderNum.text()
        test_id = self._db_m.get_value('Tests', 'ID', {'OrderNum': order_num})
        if test_id:
            if with_select:
                choice =  Message.choice(
                    "Внимание",
                    "Запись с таким наряд-заказом "
                    "уже присутствует в базе данных.\n"
                    "Хотите выбрать её или создать новую?",
                    ("Выбрать", "Создать", "Отмена")
                )
                if not choice == 2:
                    self.select_test(test_id['ID'])
                    if choice == 1:
                        self.set_current_date()
            return test_id['ID']
        return 0


    def select_test(self, test_id: int):
        """ выбирает в списке тестов запись и указаным ID """
        model = self._wnd.tableTests.model().sourceModel()
        index = model.get_row_contains(0, test_id)
        self._wnd.tableTests.selectRow(index.row())


    def set_current_date(self):
        """ устанавливает текущую дату-время в соотв.поле """
        today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._wnd.txtDateTime.setText(today)

    def generate_result_text(self):
        """ генерирует миниотчёт об испытании """
        self._info.dlts_.clear()
        result_lines = []
        if self._info.test_['Flows']:
            self.generate_deltas_report(result_lines)
            self.generate_effs_report(result_lines)
        return '\n'.join(result_lines)


    def generate_deltas_report(self, lines: list):
        """ расчитывает отклонения для напора и мощности """
        for name, title in zip(('lft', 'pwr'),('Напор', 'Мощность')):
            self.calculate_deltas_for(name)
            string = f'\u0394 {title}, %\t'
            string += '\t{:>10.2f}\t{:>10.2f}\t{:>10.2f}'.format(*self._info.dlts_[name])
            lines.append(string)

    def generate_effs_report(self, lines: list):
        """ расчитывает отклонения для кпд """
        chart = self._gf_m.get_chart('test_eff')
        spline = chart.getSpline()
        curve = chart.regenerateCurve()
        nom = self._info.type_['Nom']
        eff_nom = float(spline(nom))
        eff_max = float(max(curve['y']))
        eff_dlt = abs(eff_max - eff_nom)
        string = 'Отклонение КПД от номинального, %\t{:>10.2f}'.format(eff_dlt)
        lines.append(string)
        self._info.dlts_['eff'] = eff_dlt

    def calculate_deltas_for(self, chart_name: str):
        """ расчитывает отклонения для указанной характеристики """
        names = (f'test_{chart_name}', f'{chart_name}')
        ranges = ('Min', 'Nom', 'Max')
        get_val = lambda spl, rng: float(spl(self._info.type_[rng]))
        get_dlt = lambda tst, etl: round((tst / etl * 100 - 100), 2)
        vals = []
        for name in names:
            spln = self._gf_m.get_chart(f'{name}').getSpline()
            vals.append([get_val(spln, rng) for rng in ranges])
        result = [get_dlt(x, y) for x, y in zip(vals[0], vals[1])]
        self._info.dlts_[name] = result
