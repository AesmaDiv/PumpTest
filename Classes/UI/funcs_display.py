"""
    Модуль содержит функции для отображения данных в главном окне
"""
from AesmaLib.journal import Journal
from Classes.UI.funcs_aux import calculate_eff
from Classes.UI import funcs_table, funcs_table_points
from Classes.UI import funcs_table_vibr, funcs_group, funcs_test


def display_sensors(window, sensors: dict):
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
def display_record(window, data_manager):
    """ отображает информацию о тесте """
    testdata = data_manager.get_testdata()
    display_test_points(window, testdata)
    funcs_group.group_display(window.groupTestInfo, testdata.test_)
    funcs_group.group_lock(window.groupTestInfo, True)
    display_pump_info(window, testdata)


def display_test_points(window, testdata):
    """ отображение точек испытания в таблице """
    funcs_table.clear(window.tablePoints)
    for i in range(testdata.test_.num_points()):
        flw = testdata.test_.values_flw[i]
        lft = testdata.test_.values_lft[i]
        pwr = testdata.test_.values_pwr[i]
        eff = calculate_eff(flw, lft, pwr)
        funcs_table_points.add(window, flw, lft, pwr, eff)
    funcs_table_vibr.add(window, testdata.test_.values_vbr)


def display_pump_info(window, testdata):
    """ отображает информацию о насосе """
    pump_id = testdata.test_['Pump']
    Journal.log(f"{__name__}::\t загружает информацию о насосе --> {pump_id}")
    if testdata.pump_.read(pump_id):
        type_id = testdata.pump_['Type']
        Journal.log(f"{__name__}::\t загружает информацию о типе --> {type_id}")
        if testdata.type_.read(type_id):
            funcs_group.group_display(window.groupPumpInfo, testdata.pump_)
            funcs_group.group_lock(window.groupPumpInfo, True)
            window.groupTestFrame.setTitle(testdata.type_.Name)


def display_test_deltas(window, graph_manager):
    """ отображение результата испытания """
    test_result = graph_manager.generate_result_text()
    window.lblTestResult.setText(test_result)


def display_test_vibrations(window):
    """ отображение показаний вибрации """
    funcs_table.clear(window.tableVibrations)


def display_current_marker_point(window, data: dict):
    """ отображение текущих значений маркера в соотв.полях """
    name = list(data.keys())[0]
    point = list(data.values())[0]
    if name == 'test_lft':
        window.txtFlow.setText('%.4f' % point.x())
        window.txtLift.setText('%.4f' % point.y())
    elif name == 'test_pwr':
        window.txtPower.setText('%.4f' % point.y())
