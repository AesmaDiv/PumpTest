"""
    Модуль содержит функции для отображения данных в главном окне
"""
from PyQt5.QtWidgets import QLineEdit

from Classes.UI import funcs_table, funcs_group, funcs_test


def displaySensors(window, sensors: dict):
    """отображает показания датчиков"""
    # датчики
    pairs = {
        "txtRPM": "rpm", "txtTorque": "torque",
        "txtPsiIn": "psi_in", "txtPsiOut": "psi_out",
        "txtFlow0": "flw0", "txtFlow1": "flw1", "txtFlow2": "flw2"
    }
    for name, key in pairs.items():
        item = window.findChild(QLineEdit, name)
        if item:
            item.setText(str(round(sensors[key], 2)))
    # расчётные значения
    flw, lft, pwr = funcs_test.getCalculatedVals(sensors)
    window.txtFlow.setText(str(round(flw, 2)))
    window.txtLift.setText(str(round(lft, 2)))
    window.txtPower.setText(str(round(pwr, 4)))


def displayRecord(window, testdata):
    """отображает полную информацию об испытании"""
    displayPumpInfo(window, testdata)
    displayTestInfo(window, testdata)
    displayTestPoints(window, testdata)


def displayPumpInfo(window, testdata):
    """отображает информацию о насосе"""
    # x1 = time.time_ns()
    funcs_group.groupDisplay(window.groupPumpInfo, testdata.pump_)
    funcs_group.groupLock(window.groupPumpInfo, True)
    window.groupTestFrame.setTitle(testdata.type_.Name)
    # print(f"1 displayPumpInfo\t\t{(time.time_ns() - x1) / 1000000}")


def displayTestInfo(window, testdata):
    """отображает информацию о тесте"""
    # x2 = time.time_ns()
    funcs_group.groupDisplay(window.groupTestInfo, testdata.test_)
    funcs_group.groupLock(window.groupTestInfo, True)
    # print(f"2 displayTestInfo\t\t{(time.time_ns() - x2) / 1000000}")


def displayTestPoints(wnd, testdata):
    """отображение точек испытания в таблице"""
    # x3 = time.time_ns()
    funcs_table.clear(wnd.tablePoints)
    test = testdata.test_
    for p in testdata.test_.points:
        point_data = (p.Flw, p.Lft, p.Pwr, p.Eff, testdata.pump_.Stages)
        funcs_table.addToTable_points(wnd.tablePoints, point_data)
    funcs_table.addToTable_vibrations(wnd.tableVibrations, test.values_vbr)
    # print(f"3 displayTestPoints\t\t{(time.time_ns() - x3) / 1000000}")


def displayTest_vibrations(window):
    """отображение показаний вибрации"""
    funcs_table.clear(window.tableVibrations)


def displayMarkerValues(window, data: dict):
    """отображение текущих значений маркера в соотв.полях"""
    name = list(data.keys())[0]
    point = list(data.values())[0]
    if name == 'tst_lft':
        window.txtFlow.setText('%.4f' % point.x())
        window.txtLift.setText('%.4f' % point.y())
    elif name == 'tst_pwr':
        window.txtPower.setText('%.4f' % point.y())
