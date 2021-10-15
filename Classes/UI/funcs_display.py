"""
    Модуль содержит функции для отображения данных в главном окне
"""
from AesmaLib.journal import Journal
from Classes.UI.funcs_aux import calculateEff
from Classes.UI import funcs_table, funcs_group, funcs_test


def displaySensors(window, sensors: dict):
    """ отображает показания датчиков """
    window.txtRPM.setText(str(sensors['rpm']))
    window.txtTorque.setText(str(sensors['torque']))
    window.txtPsiIn.setText(str(sensors['pressure_in']))
    window.txtPsiOut.setText(str(sensors['pressure_out']))
    window.txtFlow0.setText(str(sensors['flw0']))
    window.txtFlow1.setText(str(sensors['flw1']))
    window.txtFlow2.setText(str(sensors['flw2']))
    window.txtFlow.setText(
        str(sensors[funcs_test.states["active_flowmeter"]])
    )


@Journal.logged
def displayRecord(window, data_manager):
    """ отображает информацию о тесте """
    testdata = data_manager.getTestdata()
    displayTest_points(window, testdata)
    funcs_group.groupDisplay(window.groupTestInfo, testdata.test_)
    funcs_group.groupLock(window.groupTestInfo, True)
    displayPumpInfo(window, testdata)


def displayPumpInfo(window, testdata):
    """ отображает информацию о насосе """
    pump_id = testdata.test_['Pump']
    Journal.log(f"{__name__}::\t загружает информацию о насосе --> {pump_id}")
    if testdata.pump_.read(pump_id):
        type_id = testdata.pump_['Type']
        Journal.log(f"{__name__}::\t загружает информацию о типе --> {type_id}")
        if testdata.type_.read(type_id):
            funcs_group.groupDisplay(window.groupPumpInfo, testdata.pump_)
            funcs_group.groupLock(window.groupPumpInfo, True)
            window.groupTestFrame.setTitle(testdata.type_.Name)


def displayMarkerValues(window, data: dict):
    """ отображение текущих значений маркера в соотв.полях """
    name = list(data.keys())[0]
    point = list(data.values())[0]
    if name == 'test_lft':
        window.txtFlow.setText('%.4f' % point.x())
        window.txtLift.setText('%.4f' % point.y())
    elif name == 'test_pwr':
        window.txtPower.setText('%.4f' % point.y())


def displayTest_points(window, testdata):
    """ отображение точек испытания в таблице """
    funcs_table.clear(window.tablePoints)
    for i in range(testdata.test_.num_points()):
        flw = testdata.test_.values_flw[i]
        lft = testdata.test_.values_lft[i]
        pwr = testdata.test_.values_pwr[i]
        eff = calculateEff(flw, lft, pwr)
        funcs_table.addToTable_points(window, flw, lft, pwr, eff)
    funcs_table.addToTable_vibrations(window, testdata.test_.values_vbr)


def displayTest_deltas(window, graph_manager):
    """ отображение результата испытания """
    test_result = graph_manager.generate_result_text()
    window.lblTestResult.setText(test_result)


def displayTest_vibrations(window):
    """ отображение показаний вибрации """
    funcs_table.clear(window.tableVibrations)
