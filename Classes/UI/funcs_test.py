"""
    Модуль содержит функции для процесса испытания
"""
from PyQt5.QtWidgets import QMainWindow, QSlider
from Classes.UI import funcs_table, funcs_aux
from Classes.UI.funcs_aux import parseFloat, calculateEff
from Classes.Adam.adam_manager import AdamManager
from Classes.Adam.adam_config import params


states = {
    "is_running": False,
    "active_flowmeter": "flw2_",
    "points_limit": 10
}
sliders = {
    "sliderFlow": params["valve"],
    "sliderSpeed": params["speed"],
    # ВРЕМЕННО
    "sliderTorque": params["torque_"],
    "sliderPressure": params["pressure_"]
}

def prepareSlidersRange(wnd):
    """ установка диапазона слайдеров """
    wnd.radioFlow2.setChecked(True)
    for key, param in sliders.items():
        item = wnd.findChild(QSlider, key)
        if item:
            item.setMaximum(param.dig_max)


def switchRunningState(wnd, state: bool):
    """ переключение состояния испытания (запущен/остановлен) """
    # if is_logged: Journal.log(__name__, "::\tпереключение состояния теста в",
    #     str(state))
    states["is_running"] = state
    msg = {False: 'ЗАПУСК ДВИГАТЕЛЯ', True: 'ОСТАНОВКА ДВИГАТЕЛЯ'}
    wnd.btnEngine.setText(msg[state])
    wnd.btnGoBack.setEnabled(not state)
    wnd.spinPointLines.setEnabled(not state)
    wnd.spinPointLines.setMaximum(
        int(wnd.spinPointLines.value()) if state else states["points_limit"]
    )
    wnd.spinPointLines.setValue(wnd.spinPointLines.maximum())
    wnd.adam_manager.setValue(params["engine_"], state)


def switchActiveFlowmeter(wnd):
    """ переключение текущего расходомера """
    wnd.adam_manager.setValue(params[states["active_flowmeter"]], False)
    if wnd.radioFlow0.isChecked():
        states["active_flowmeter"] = "flw0_"
    elif wnd.radioFlow1.isChecked():
        states["active_flowmeter"] = "flw1_"
    else:
        states["active_flowmeter"] = "flw2_"
    wnd.adam_manager.setValue(params[states["active_flowmeter"]], True)


def setAdamValue(slider: QSlider, adam_manager: AdamManager, value=-1):
    """ установка значения для канала в соответствии со значением слайдера """
    param = sliders.get(slider.objectName())
    adam_manager.setValue(param, slider.value() if value < 0 else value)


def getCurrentVals(wnd):
    """ получение текущий значений (расход, напор, мощность) из соотв.полей """
    flw = parseFloat(wnd.txtFlow.text())
    lft = parseFloat(wnd.txtLift.text())
    pwr = parseFloat(wnd.txtPower.text())
    eff = calculateEff(flw, lft, pwr)
    return (flw, lft, pwr, eff)


def getCalculatedVals(sensors: dict):
    """ получение расчётных значений  """
    flw = sensors[states["active_flowmeter"].rstrip("_")]
    lft = funcs_aux.calculateLift(sensors)
    pwr = funcs_aux.calculatePower(sensors)
    rpm = sensors.get('rpm', 0)
    flw, lft, pwr = funcs_aux.applySpeedFactor(flw, lft, pwr, rpm)
    return flw, lft, pwr


def switchPointsStagesReal(wnd, test_info):
    """ переключение таблицы точек на ступень / реальные """
    data = funcs_table.getData(wnd.tablePoints)
    if data:
        if wnd.radioPointsReal.isChecked():
            func = lambda x: (x * test_info.pump_['Stages'])
        else:
            func = lambda x: (x / test_info.pump_['Stages'])
        for item in data:
            item['lft'] = round(func(item['lft']), 2)
            item['pwr'] = round(func(item['pwr']), 2)
        funcs_table.setData(wnd.tablePoints, data)