"""
    Модуль содержит функции для процесса испытания
"""
from Classes.UI import funcs_table
from Classes.UI.funcs_aux import parseFloat, calculateEff
from Classes.Adam.adam_manager import AdamManager
from Classes.Adam.adam_config import params


states = {
    "is_running": False,
    "active_flowmeter": "flw2",
    "points_limit": 10
}

def prepareSlidersRange(window):
    """ установка диапазона слайдеров """
    window.radioFlow2.setChecked(True)
    window.sliderFlow.setMaximum(0x0FFF)
    window.sliderSpeed.setMaximum(0x0FFF)
    # ВРЕМЕННО
    window.sliderTorque.setMaximum(0x0FFF)
    window.sliderPressure.setMaximum(0x0FFF)


def switchConnection(adam_manager: AdamManager, state: bool) -> bool:
    """ переключение состояния подключения и опроса устройства """
    return adam_manager.setPollingState(state, 0.100)


def switchRunningState(window, adam_manager: AdamManager, state: bool):
    """ переключение состояния испытания (запущен/остановлен) """
    # if is_logged: Journal.log(__name__, "::\tпереключение состояния теста в",
    #     str(state))
    states["is_running"] = state
    msg = {False: 'ЗАПУСК ДВИГАТЕЛЯ', True: 'ОСТАНОВКА ДВИГАТЕЛЯ'}
    window.btnEngine.setText(msg[state])
    window.btnGoBack.setEnabled(not state)
    window.spinPointLines.setEnabled(not state)
    window.spinPointLines.setMaximum(
        int(window.spinPointLines.value()) if state else states["points_limit"]
    )
    window.spinPointLines.setValue(window.spinPointLines.maximum())
    adam_manager.setValue(params["engine"], state)


def switchActiveFlowmeter(window):
    """ переключение текущего расходомера """
    if window.radioFlow0.isChecked():
        states["active_flowmeter"] = "flw0"
    elif window.radioFlow1.isChecked():
        states["active_flowmeter"] = "flw1"
    else:
        states["active_flowmeter"] = "flw2"


def changeFlow(window, adam_manager: AdamManager):
    """ ВРЕМЕННО управление расходом """
    value = window.sliderFlow.value()
    adam_manager.setValue(params["valve"], value)


def changeSpeed(window, adam_manager: AdamManager):
    """ управление двигателем """
    value = window.sliderSpeed.value()
    adam_manager.setValue(params["speed"], value)


def changeTorque(window, adam_manager: AdamManager):
    """ ВРЕМЕННО управление крутящим моментом """
    value = window.sliderTorque.value()
    adam_manager.setValue(params["torque_"], value)


def changePressure(window, adam_manager: AdamManager):
    """ ВРЕМЕННО управление давлением на выходе """
    value = window.sliderPressure.value()
    adam_manager.setValue(params["pressure_"], value)


def getCurrentVals(window):
    """ получение значений расхода, напора и мощности из соотв.полей """
    flw = parseFloat(window.txtFlow.text())
    lft = parseFloat(window.txtLift.text())
    pwr = parseFloat(window.txtPower.text())
    eff = calculateEff(flw, lft, pwr)
    return (flw, lft, pwr, eff)


def switchPointsStagesReal(window, test_info):
    """ переключение таблицы точек на ступень / реальные """
    data = funcs_table.getData(window.tablePoints)
    if data:
        if window.radioPointsReal.isChecked():
            func = lambda x: (x * test_info.pump_['Stages'])
        else:
            func = lambda x: (x / test_info.pump_['Stages'])
        for item in data:
            item['lft'] = round(func(item['lft']), 2)
            item['pwr'] = round(func(item['pwr']), 2)
        funcs_table.setData(window.tablePoints, data)
