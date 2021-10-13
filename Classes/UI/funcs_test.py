"""
    Модуль содержит функции для процесса испытания
"""
from Classes.UI import funcs_table
from Classes.UI.funcs_aux import parse_float, calculate_eff
from Classes.Adam.adam_manager import AdamManager
from Classes.Adam.adam_config import params


states = {
    "is_running": False,
    "active_flowmeter": "flw2"
}

def prepare_sliders_range(window):
    """ установка диапазона слайдеров """
    window.sliderPressure.setMaximum(0x0FFF)
    window.sliderSpeed.setMaximum(0x0FFF)
    window.radioFlow2.setChecked(True)


def switch_connection(adam_manager: AdamManager, state: bool) -> bool:
    """ переключение состояния подключения и опроса устройства """
    return adam_manager.set_polling_state(state, 0.100)


def switch_running_state(window, adam_manager: AdamManager, state: bool):
    """ переключение состояния испытания (запущен/остановлен) """
    # if is_logged: Journal.log(__name__, "::\tпереключение состояния теста в",
    #     str(state))
    states["is_running"] = state
    msg = {False: 'ЗАПУСК ДВИГАТЕЛЯ', True: 'ОСТАНОВКА ДВИГАТЕЛЯ'}
    window.btnEngine.setText(msg[state])
    window.btnGoBack.setEnabled(not state)
    adam_manager.set_value(params["engine"], state)


def switch_active_flowmeter(window):
    """ переключение текущего расходомера """
    if window.radioFlow0.isChecked():
        states["active_flowmeter"] = "flw0"
    elif window.radioFlow1.isChecked():
        states["active_flowmeter"] = "flw1"
    else:
        states["active_flowmeter"] = "flw2"


def change_flow_valve(window, adam_manager: AdamManager):
    """ управление задвижкой """
    value = window.sliderPressure.value()
    adam_manager.set_value(params["valve"], value)


def change_engine_rpm(window, adam_manager: AdamManager):
    """ управление двигетелем """
    value = window.sliderSpeed.value()
    adam_manager.set_value(params["speed"], value)


def get_current_vals(window):
    """ получение значений расхода, напора и мощности из соотв.полей """
    flw = parse_float(window.txtFlow.text())
    lft = parse_float(window.txtLift.text())
    pwr = parse_float(window.txtPower.text())
    eff = calculate_eff(flw, lft, pwr)
    return (flw, lft, pwr, eff)


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
