"""
    Модуль содержит функции для процесса испытания
"""
from asyncio import run
from tokenize import group

from Classes.UI.funcs import funcs_table
from Classes.UI.funcs.funcs_aux import parseFloat, calculateEff


def switchControlsAccessible(wnd, state: bool):
    """переключение доступности кнопок добавления / удаления точек"""
    wnd.btnAddPoint.setEnabled(state)
    wnd.btnRemovePoint.setEnabled(state)
    wnd.btnClearCurve.setEnabled(state)
    wnd.btnSaveCharts.setEnabled(not state)
    # wnd.btnGoInfo.setEnabled(not state)
    wnd.btnPurge.setEnabled(not state)
    wnd.spinPointLines.setEnabled(not state)
    wnd.spinPointLines.setMaximum(int(wnd.spinPointLines.value()) if state else 10)
    wnd.spinPointLines.setValue(wnd.spinPointLines.maximum())
    wnd.groupTestList.setEnabled(not state)
    wnd.groupRotation.setEnabled(not state)


def getCurrentVals(wnd):
    """получение текущий значений (расход, напор, мощность) из соотв.полей"""
    flw = parseFloat(wnd.txtFlow.text())
    lft = parseFloat(wnd.txtLift.text())
    pwr = parseFloat(wnd.txtPower.text())
    eff = calculateEff(flw, lft, pwr)
    return [flw, lft, pwr, eff]


def switchPointsStagesReal(wnd, test_info):
    """переключение таблицы точек на ступень / реальные"""
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
