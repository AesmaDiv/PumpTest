"""
    Модуль содержит методы проверки и сохранения записей
"""
from Classes.UI.funcs_group import (groupValidate, groupSave, groupLock)
from Classes.UI.funcs_display import displayPumpInfo
from Classes.UI.funcs_combo import fillCombos_Pump


def saveInfo_Pump(wnd, check_exists=True):
    """ сохранение нового насоса """
    # проверяем присутствие серийника в БД
    if check_exists and checkExists_Pump(wnd):
        return
    # проверяем заполение полей и сохраняем
    if validateAndSave_Pump(wnd):
        fillCombos_Pump(wnd, wnd.db_manager)
        wnd.cmbSerial.model().selectContains(wnd.testdata.pump_.ID)


def saveInfo_Test(wnd, already_selected=False):
    """ сохранение нового теста """
    if not already_selected:
        if findAndSelect_Test(wnd, wnd.txtOrderNum.text()):
            return
    if validateAndSave_Test(wnd, already_selected):
        wnd.graph_manager.markersClearKnots()
        wnd.graph_manager.drawCharts(wnd.frameGraphInfo)
        # wnd.graph_manager.drawCharts(wnd.frameGraphTest)
        wnd.testlist.refresh()


def checkExists_Pump(wnd) -> bool:
    """ проверка присутствия серийника в базе """
    pump_id, do_select = wnd.db_manager.checkExists_Serial(
        wnd.cmbSerial.currentText(),
        wnd.testdata.type_.ID
    )
    # если есть - выбираем
    if pump_id and do_select:
        wnd.testdata.test_['Pump'] = pump_id
        displayPumpInfo(wnd, wnd.testdata)
        return True
    return False


def findAndSelect_Test(wnd, order_num) -> bool:
    """ проверка присутствия наряд-заказа в базе """
    test_id, do_select = wnd.db_manager.checkExists_OrderNum(order_num)
    if test_id and do_select:
        wnd.testlist.setCurrentTest(test_id)
    return test_id > 0

def validateAndSave_Pump(wnd) -> bool:
    """ запись значений из полей в класс насоса """
    if groupValidate(wnd.groupPumpInfo):
        groupSave(wnd.groupPumpInfo, wnd.testdata.pump_)
        groupLock(wnd.groupPumpInfo, True)
        return wnd.db_manager.saveInfo_Pump()
    return False


def validateAndSave_Test(wnd, already_selected) -> bool:
    """ запись значений из полей в класс теста """
    if groupValidate(wnd.groupTestInfo):
        groupSave(wnd.groupTestInfo, wnd.testdata.test_, keep_id=already_selected)
        groupLock(wnd.groupTestInfo, True)
        return wnd.db_manager.saveInfo_Test()
    return False


def checkAndSave(group, record) -> bool:
    if groupValidate(group):
        # clear
        groupSave(group, record)
        groupLock(group, True)
        return record.write()
    return False
