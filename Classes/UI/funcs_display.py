"""
    Модуль содержит функции для отображения данных в главном окне
"""
from AesmaLib.journal import Journal
from Classes.UI.funcs_aux import calculate_eff
from Classes.UI import funcs_table, funcs_table_points
from Classes.UI import funcs_table_vibr, funcs_group


def display_sensors(window, sensors: dict):
    """ отображает показания датчиков """
    window.txtRPM.setText(str(sensors['rpm']))
    window.txtTorque.setText(str(sensors['torque']))
    window.txtPsiIn.setText(str(sensors['pressure_in']))
    window.txtPsiOut.setText(str(sensors['pressure_out']))
    window.txtFlow05.setText(str(sensors['flw05']))
    window.txtFlow1.setText(str(sensors['flw1']))
    window.txtFlow2.setText(str(sensors['flw2']))


@Journal.logged
def display_test(window, data_manager, test_id: int):
    """ отображает информацию о тесте """
    Journal.log(f"{__name__}::\t загружает информацию о тесте --> {test_id}")
    test_data = data_manager.get_testdata()
    if test_data.test_.load(test_id):
        display_test_data(window, test_data)
        funcs_group.group_display(window.groupTestInfo, test_data.test_)
        funcs_group.group_lock(window.groupTestInfo, True)
        display_pump(window, test_data)


def display_test_data(window, test_data):
    """ отображение точек испытания в таблице """
    funcs_table.clear(window.tablePoints)
    for i in range(test_data.test_.num_points()):
        flw = test_data.test_.values_flw[i]
        lft = test_data.test_.values_lft[i]
        pwr = test_data.test_.values_pwr[i]
        eff = calculate_eff(flw, lft, pwr)
        funcs_table_points.add(window, flw, lft, pwr, eff)
    funcs_table_vibr.add(window, test_data.test_.values_vbr)


def display_pump(window, test_info):
    """ отображает информацию о насосе """
    pump_id = test_info.test_['Pump']
    Journal.log(f"{__name__}::\t загружает информацию о насосе --> {pump_id}")
    if test_info.pump_.load(pump_id):
        type_id = test_info.pump_['Type']
        Journal.log(f"{__name__}::\t загружает информацию о типе --> {type_id}")
        if test_info.type_.load(type_id):
            funcs_group.group_display(window.groupPumpInfo, test_info.pump_)
            funcs_group.group_lock(window.groupPumpInfo, True)
            window.groupTestFrame.setTitle(test_info.type_.Name)


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
