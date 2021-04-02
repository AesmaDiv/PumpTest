"""
    Модуль содержащий функции обработки событий
"""
from PyQt5.QtCore import Qt

from Functions import funcsCommon, funcsSpinner, funcsGraph, funcsMessages
from Functions import funcsTest, funcs_wnd, funcsAdam, funcsTable
from AesmaLib.journal import Journal
from Globals import gvars


def on_changed_testlist():
    """ выбор теста """
    wnd = gvars.wnd_main
    Journal.log("Event::", "\ttest list changed",
                funcsTable.get_row(wnd.tableTests)['ID'])
    funcs_wnd.group_lock(wnd.groupTestInfo, True)
    funcs_wnd.group_lock(wnd.groupPumpInfo, True)
    funcs_wnd.clear_record(True)
    funcs_wnd.display_record()


def on_changed_combo_producers(index):
    """ выбор производителя """
    item = gvars.wnd_main.cmbProducer.currentData(Qt.UserRole)
    Journal.log("Event::", "\tproducer changed to ",
                item['Name'] if item else "None")
    if isinstance(item, dict) and 'ID' in item:
        db_params = {'columns': ['ID', 'Name', 'Producer'],
                     'conditions': {'Producer': item['ID']}}
        funcs_wnd.fill_spinner(gvars.wnd_main.cmbType, 'Types', db_params, 1)


def on_changed_combo_types(index):
    """ выбор типоразмера """
    if index:
        wnd = gvars.wnd_main
        item = wnd.cmbType.currentData(Qt.UserRole)
        Journal.log("Event::", "\ttype changed to", item['Name'])
        if isinstance(item, dict) and 'ID' in item:
            type_id = item['ID']
            prod_id = item['Producer']
            wnd.groupTestFrame.setTitle(item['Name'])
            if not funcsSpinner.get_current_value(wnd.cmbProducer):
                funcsSpinner.select_item_containing(wnd.cmbProducer, prod_id)
                funcsSpinner.select_item_containing(wnd.cmbType, type_id)
            # elif gvars.rec_type.load(type_id):
            #     funcsGraph.draw_charts()


def on_changed_combo_serials(index):
    """ выбор заводского номера """
    Journal.log("Event::", "\tserial changed")
    wnd = gvars.wnd_main
    if index:
        item = wnd.cmbSerial.currentData(Qt.UserRole)
        if isinstance(item, dict) and 'ID' in item:
            pump_id = item['ID']
            if gvars.rec_pump.load(pump_id):
                funcs_wnd.group_display(wnd.groupPumpInfo, gvars.rec_pump)
    else:
        funcsSpinner.select_item_containing(wnd.cmbProducer, '')
        funcsSpinner.select_item_containing(wnd.cmbType, '')
        funcs_wnd.group_clear(wnd.groupPumpInfo)
        # gvars.rec_pump.clear()
        # gvars.rec_type.clear()
    # funcsGraph.draw_charts()



# PUMP INFO
def on_clicked_pump_new():
    """ нажата кнопка добавления нового насоса """
    Journal.log("Event::", "\tnew pump clicked")
    funcs_wnd.group_lock(gvars.wnd_main.groupPumpInfo, False)
    funcs_wnd.group_clear(gvars.wnd_main.groupPumpInfo)


def on_clicked_pump_save():
    """ нажата кнопка сохранения нового насоса """
    Journal.log("Event::", "\tsave pump clicked")
    if gvars.rec_type.check_exist({}):
        if gvars.rec_pump.check_exist({}) or gvars.rec_pump.save():
            funcs_wnd.group_lock(gvars.wnd_main.groupPumpInfo, True)
    else:
        funcsMessages.show("Ошибка", "Такого типоразмера нет в базе.")


def on_clicked_pump_cancel():
    """ нажата кнопка отмены добавления нового насоса """
    Journal.log("Event::", "\tnew pump cancel clicked")
    wnd = gvars.wnd_main
    funcs_wnd.group_display(wnd.groupPumpInfo, gvars.rec_pump)
    funcs_wnd.group_lock(wnd.groupPumpInfo, True)


# TEST INFO
def on_clicked_test_new():
    """ нажата кнопка добавления нового теста """
    Journal.log("Event::", "\tnew test clicked")
    wnd = gvars.wnd_main
    funcs_wnd.group_lock(wnd.groupTestInfo, False)
    funcs_wnd.group_clear(wnd.groupTestInfo)
    funcsCommon.set_current_date()


def on_clicked_test_info_save():
    """ нажата кнопка сохранения нового теста """
    Journal.log("Event::", "\tsave test clicked")
    test_id = Infos.Test.check_exist()
    if test_id:
        if funcsMessages.ask("Внимание", "Тест с таким наряд-заказом\nуже присутствует в базе.\nХотите его выбрать?"):
            funcsCommon.select_test(test_id)
        else:
            return
    else:
        if Infos.Test.save_info():
            funcs_wnd.fill_test_list()
        else:
            return
    Infos.Test.set_readonly(gvars.wnd_main.groupTestInfo, True)
    Infos.Pump.set_readonly(gvars.wnd_main.groupTestInfo, True)


def on_clicked_test_info_cancel():
    """ нажата кнопка отмены добавления нового теста """
    Journal.log("Event::", "\tnew test cancel clicked")
    wnd = gvars.wnd_main
    funcs_wnd.group_display(wnd.groupTestInfo, gvars.rec_test)
    funcs_wnd.group_lock(wnd.groupTestInfo, True)


def on_clicked_save():
    # gvars.wnd_main.__store_record()
    pass


def on_clicked_filter_reset():
    Journal.log("Event::", "\treset filter clicked")
    funcs_wnd.testlist_filter_reset()
    funcs_wnd.group_lock(gvars.wnd_main.groupTestInfo, True)
    funcs_wnd.group_lock(gvars.wnd_main.groupPumpInfo, True)


def on_clicked_go_test():
    """ нажата кнопка перехода к тестированию """
    Journal.log("Event::", "\tgo to testing clicked")
    gvars.wnd_main.stackedWidget.setCurrentIndex(1)
    funcsGraph.display_charts(gvars.markers)
    gvars.markers.repositionFor(gvars.graph_info)


def on_clicked_go_back():
    """ нажата кнопка возврата на основное окно """
    Journal.log("Event::", "\tgo back clicked")
    gvars.wnd_main.stackedWidget.setCurrentIndex(0)
    funcsGraph.display_charts(gvars.wnd_main.frameGraphInfo)


# TEST
def on_clicked_test():
    """ нажата кнопка начала/остановки испытания """
    funcsTest.is_test_running = not funcsTest.is_test_running
    funcsTest.switch_charts_visibility()
    funcsTest.switch_test_running_state()


def on_clicked_test_data_save():
    title = 'УСПЕХ'
    message = 'Результаты сохранены'
    if not Infos.Test.save_data():
        title = 'ОШИБКА'
        message = 'Запись заблокирована'
    funcsMessages.show(title, message)


def on_clicked_add_point():
    Journal.log("Event::", "\tadd point clicked")
    gvars.markers.addKnots()
    funcsTest.add_point_to_list()
    funcsTest.add_points_to_charts()
    funcsGraph.display_charts(gvars.markers)


def on_clicked_remove_point():
    Journal.log("Event::", "\tremove point clicked")
    gvars.markers.removeKnots()
    funcsTest.remove_last_point_from_list()
    funcsTest.remove_last_points_from_charts()
    funcsGraph.display_charts(gvars.markers)


def on_clicked_clear_curve():
    Journal.log("Event::", "\tmoving chart to graph")
    gvars.markers.clearAllKnots()
    funcsTest.clear_points_from_list()
    funcsTest.clear_points_from_charts()
    funcsGraph.display_charts(gvars.markers)


def on_changed_filter_apply(text: str):
    Journal.log("Event::", "\tapply filter clicked")
    funcs_wnd.testlist_filter_apply()


def on_radio_changed():
    funcs_wnd.testlist_filter_switch()


def on_clicked_adam_connection():
    state = funcsAdam.changeConnectionState()
    gvars.wnd_main.checkConnection.setChecked(state)
    gvars.wnd_main.checkConnection.setText("подключено" if state else "отключено")


def on_adam_data_received(sensors: dict):
    point_data = {key: sensors[key] for key in ['rpm', 'torque', 'pressure_in', 'pressure_out']}
    point_data['flow'] = sensors[gvars.active_flowmeter]
    funcs_wnd.display_sensors(sensors)


def on_changed_sensors():
    """ изменения значений датчиков """
    funcsTest.move_markers()
    pass


def on_markers_move(point_data: dict):
    funcsTest.display_current_marker_point(point_data)
