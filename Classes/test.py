from Classes.UI import funcs_table
from Classes.UI.funcs_aux import parse_float, calculate_eff


class Test:
    is_running: bool = False
    @staticmethod
    def switch_running_state(window, state):
        """ переключение состояния испытания (запущен/остановлен) """
        # if is_logged: Journal.log(__name__, "::\tпереключение состояния теста в",
        #     str(state))
        msg = {False: 'ЗАПУСК ДВИГАТЕЛЯ', True: 'ОСТАНОВКА ДВИГАТЕЛЯ'}
        window.btnTest.setText(msg[state])
        window.btnGoBack.setEnabled(not state)

    @staticmethod
    def get_current_vals(window):
        """ получение значений расхода, напора и мощности из соотв.полей """
        flw = parse_float(window.txtFlow.text())
        lft = parse_float(window.txtLift.text())
        pwr = parse_float(window.txtPower.text())
        eff = calculate_eff(flw, lft, pwr)
        return (flw, lft, pwr, eff)

    @staticmethod
    def switch_points_stages_real(window, test_info):
        """ переключение таблицы точек на ступень / реальные """
        data = funcs_table.get_data(window.tablePoints)
        if data:
            if window.radioPointsReal.isChecked():
                func = lambda x: (x * test_info.pump_['Stages'])
            else:
                func = lambda x: (x / test_info.pump_['Stages'])
            for item in data:
                item['lft'] = round(func(item['lft']), 2)
                item['pwr'] = round(func(item['pwr']), 2)
            funcs_table.set_data(window.tablePoints, data)
