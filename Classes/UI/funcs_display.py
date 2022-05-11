"""
    Модуль содержит функции для отображения данных в главном окне
"""
from PyQt5.QtWidgets import QLineEdit
from AesmaLib.journal import Journal
from Classes.UI import funcs_table, funcs_group, funcs_test


def displaySensors(window, sensors: dict):
    """ отображает показания датчиков """
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


@Journal.logged
async def displayRecord(window, data_manager):
    """ отображает информацию о тесте """
    testdata = data_manager.testdata
    funcs_group.groupDisplay(window.groupTestInfo, testdata.test_)
    funcs_group.groupLock(window.groupTestInfo, True)
    displayPumpInfo(window, testdata)
    displayTest_points(window, testdata)


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
            # window.lblPumpInfo.setText(testdata.type_.Name)
            window.groupTestFrame.setTitle(testdata.type_.Name)


def displayMarkerValues(window, data: dict):
    """ отображение текущих значений маркера в соотв.полях """
    name = list(data.keys())[0]
    point = list(data.values())[0]
    if name == 'tst_lft':
        window.txtFlow.setText('%.4f' % point.x())
        window.txtLift.setText('%.4f' % point.y())
    elif name == 'tst_pwr':
        window.txtPower.setText('%.4f' % point.y())


def displayTest_points(wnd, testdata):
    """ отображение точек испытания в таблице """
    funcs_table.clear(wnd.tablePoints)
    test = testdata.test_
    for p in testdata.test_.points:
        point_data = (p.Flw, p.Lft, p.Pwr, p.Eff, testdata.pump_.Stages)
        funcs_table.addToTable_points(wnd.tablePoints, point_data)
    funcs_table.addToTable_vibrations(wnd.tableVibrations, test.values_vbr)


def displayTest_results(window, context):
    """ отображение итоговых результатов испытания """
    lmt = context['limits']
    dlt = context['deltas']
    color = lambda name: "green" if dlt[name] and \
        lmt[name][0]  <= dlt[name] <= lmt[name][1] else "red"
    window.lblTestResult_1.setText(
f"""<table width=200 cellspacing=2>
    <thead>
        <tr>
            <th width=200>параметр</th>
            <th width=70>допуск</th>
            <th width=70>данные</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Отклонение оптимальной подачи, %</td>
            <td>{lmt['flw'][0]} .. {lmt['flw'][1]}</td>
            <td style='color: {color('flw')};'>{dlt['flw']}</td>
        </tr>
        <tr>
            <td>Отклонение напора, %</td>
            <td>{lmt['lft'][0]} .. {lmt['lft'][1]}</td>
            <td style='color: {color('lft')};'>{dlt['lft']}</td>
        </tr>
        <tr>
            <td>Отклонение мощности, %</td>
            <td>{lmt['pwr'][0]} .. {lmt['pwr'][1]}</td>
            <td style='color: {color('pwr')};'>{dlt['pwr']}</td>
        </tr>
        <tr>
            <td>Отклонение КПД, %</td>
            <td>{lmt['eff'][0]} .. {lmt['eff'][1]}</td>
            <td style='color: {color('eff')};'>{dlt['eff']}</td>
        </tr>
    </tbody>
</table>""")
    color = lambda name: "green" if dlt[name] and (dlt[name] <= lmt[name]) else "red"
    window.lblTestResult_2.setText(
f"""<table width=200 cellspacing=2>
    <thead>
        <tr>
            <th width=200>параметр</th>
            <th width=70>допуск</th>
            <th width=70>данные</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Вибрация, мм</td>
            <td>&#8804; {lmt['vbr']}</td>
            <td style='color: {color('vbr')};'>{dlt['vbr']}</td>
            
        </tr>
        <tr>
            <td>Радиальное биение, мм</td>
            <td>&#8804; {lmt['wob']}</td>
            <td style='color: {color('wob')};'>{dlt['wob']}</td>
            
        </tr>
        <tr>
            <td>Момент проворота, кВт</td>
            <td>&#8804; {lmt['mom']}</td>
            <td style='color: {color('mom')};'>{dlt['mom']}</td>
            
        </tr>
        <tr>
            <td>Энергоэффективность</td>
            <td/>
            <td style='color: black;'>{context['efficiency']}</td>
        </tr>
    </tbody>
</table>""")

def displayTest_vibrations(window):
    """ отображение показаний вибрации """
    funcs_table.clear(window.tableVibrations)
