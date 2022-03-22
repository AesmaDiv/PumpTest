from Classes.UI.funcs_group import groupLock, groupCheck, groupSave
from Classes.UI.funcs_display import displayPumpInfo
from Classes.UI.funcs_combo import fillCombos_pump
from Classes.UI.funcs_aux import setCurrentDate
from AesmaLib.message import Message

def savePumpInfo(wnd):
    """ сохранения нового насоса """
    data_manager = wnd.data_manager()
    testdata = wnd.testdata()
    # проверяем есть ли такой серийник в базе
    pump_id, do_select = data_manager.checkExists_serial(
        wnd.cmbSerial.currentText(),
        data_manager.getTestdata().type_.ID
    )
    # если есть - выбираем
    if pump_id and do_select:
        testdata.test_['Pump'] = pump_id
        displayPumpInfo(wnd, testdata)
    # проверяем заполение полей и сохраняем
    elif groupCheck(wnd.groupPumpInfo):
        pump_info = testdata.pump_
        groupLock(wnd.groupPumpInfo, True)
        groupSave(wnd.groupPumpInfo, pump_info)
        if data_manager.savePumpInfo():
            fillCombos_pump(wnd, data_manager)
            wnd.cmbSerial.model().selectContains(pump_info.ID)


def saveTestInfo(wnd, testlist):
    """ сохранения нового теста """
    data_manager = wnd.data_manager()
    graph_manager = wnd.graph_manager()
    testdata = wnd.testdata()
    test_id = data_manager.findRecord_ordernum(wnd.txtOrderNum.text())
    if test_id:
        # если есть - выбираем
        choice =  Message.choice(
            "Внимание",
            "Запись с таким наряд-заказом "
            "уже присутствует в базе данных.\n"
            "Хотите выбрать её или создать новую?",
            ("Выбрать", "Создать", "Отмена")
        )
        if choice != 2:
            testlist.setCurrentTest(wnd, test_id)
            if choice == 1:
                setCurrentDate(wnd)
    # сохраняем новый тест
    elif groupCheck(wnd.groupTestInfo):
        data_manager.clearTestInfo()
        groupSave(wnd.groupTestInfo, testdata.test_)
        groupLock(wnd.groupTestInfo, True)
        data_manager.saveTestInfo()
        graph_manager.markersClearKnots()
        graph_manager.drawCharts(wnd.frameGraphInfo)
        testlist.refresh(wnd, data_manager)