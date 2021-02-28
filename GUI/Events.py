from PyQt5.QtCore import Qt

from AppClasses import Infos
from Functions import funcsCommon, funcsSpinner, funcsGraph, funcsMessages
from Functions import funcsTest, funcsWindow, funcsAdam, funcsTable
from AesmaLib.journal import Journal
from Globals import gvars


# TESTLIST
def on_changed_testlist():
    Journal.log("Event::", "\ttest list changed", funcsTable.get_row(gvars.wnd_main.tableTests)['ID'])
    Infos.Test.set_readonly(gvars.wnd_main.groupTestInfo, True)
    Infos.Pump.set_readonly(gvars.wnd_main.groupPumpInfo, True)
    if Infos.Test.load() and Infos.Pump.load(gvars.dictTest['Pump']):
        Infos.Pump.display()
        Infos.Test.display()
        Infos.Type.display()
    else:
        Infos.Pump.clear(gvars.wnd_main.groupPumpInfo)
        Infos.Test.clear(gvars.wnd_main.groupTestInfo)
        Infos.Type.clear()
    funcsGraph.draw_charts()


# PUMP INFO
def on_clicked_pump_new():
    Journal.log("Event::", "\tnew pump clicked")
    Infos.Test.clear(gvars.wnd_main.groupTestInfo)
    Infos.Type.clear()
    Infos.Pump.clear(gvars.wnd_main.groupPumpInfo)
    Infos.Pump.set_readonly(gvars.wnd_main.groupPumpInfo, False)
    pass


def on_clicked_pump_save():
    Journal.log("Event::", "\tsave pump clicked")
    if Infos.Type.check_exist():
        if Infos.Pump.check_exist() or Infos.Pump.save():
            Infos.Pump.set_readonly(gvars.wnd_main.groupPumpInfo, True)
    else:
        funcsMessages.show("Ошибка", "Такого типоразмера нет в базе.")


def on_clicked_pump_cancel():
    Journal.log("Event::", "\tnew pump cancel clicked")
    Infos.Pump.clear(gvars.wnd_main.groupPumpInfo)
    Infos.Pump.set_readonly(gvars.wnd_main.groupPumpInfo, True)
    pass


# TEST INFO
def on_clicked_test_new():
    Journal.log("Event::", "\tnew test clicked")
    Infos.Test.clear(gvars.wnd_main.groupTestInfo)
    Infos.Test.set_readonly(gvars.wnd_main.groupTestInfo, False)
    funcsCommon.set_current_date()
    pass


def on_clicked_test_info_save():
    Journal.log("Event::", "\tsave test clicked")
    test_id: int = Infos.Test.check_exist()
    if test_id:
        if funcsMessages.ask("Внимание", "Тест с таким наряд-заказом\nуже присутствует в базе.\nХотите его выбрать?"):
            funcsCommon.select_test(test_id)
        else:
            return
    else:
        if Infos.Test.save_info():
            funcsWindow.fill_test_list()
        else:
            return
    Infos.Test.set_readonly(gvars.wnd_main.groupTestInfo, True)
    Infos.Pump.set_readonly(gvars.wnd_main.groupTestInfo, True)


def on_clicked_test_info_cancel():
    Journal.log("Event::", "\tnew test cancel clicked")
    Infos.Test.clear(gvars.wnd_main.groupTestInfo)
    Infos.Test.set_readonly(gvars.wnd_main.groupTestInfo, True)
    pass


# PUMP AND TEST INFO PARAMS
def on_changed_combo_producers(index):
    values = gvars.wnd_main.cmbProducers.currentData(Qt.UserRole)
    Journal.log("Event::", "\tproducer changed to ", values['Name'] if values else "None")
    conditions: dict = {'Producer': values['ID']} if type(values) is dict and 'ID' in values else {}
    funcsWindow.fill_spinner(gvars.wnd_main.cmbTypes, 'Types', ['ID', 'Name', 'Producer'], 1, conditions)


def on_changed_combo_types(index):
    if index:
        values = gvars.wnd_main.cmbTypes.currentData(Qt.UserRole)
        Journal.log("Event::", "\ttype changed to", values['Name'])
        if type(values) is dict and 'ID' in values:
            type_id = values['ID']
            gvars.wnd_main.groupTestFrame.setTitle(values['Name'])
            if not funcsSpinner.get_current_value(gvars.wnd_main.cmbProducers):
                funcsSpinner.select_item_containing(gvars.wnd_main.cmbProducers, values['Producer'])
                funcsSpinner.select_item_containing(gvars.wnd_main.cmbTypes, type_id)
            # elif Infos.Type.load(type_id):
            #     funcsGraph.draw_charts()


def on_changed_combo_serials(index):
    Journal.log("Event::", "\tserial changed")
    if index:
        values = gvars.wnd_main.cmbSerials.currentData(Qt.UserRole)
        if type(values) is dict and 'ID' in values:
            pump_id = values['ID']
            if Infos.Pump.load(pump_id):
                Infos.Pump.display()
    else:
        funcsSpinner.select_item_containing(gvars.wnd_main.cmbProducers, '')
        funcsSpinner.select_item_containing(gvars.wnd_main.cmbTypes, '')
        Infos.Pump.clear(gvars.wnd_main.groupPumpInfo)
    # funcsGraph.draw_charts()


def on_clicked_save():
    # gvars.wnd_main.__store_record()
    pass


def on_clicked_filter_reset():
    Journal.log("Event::", "\treset filter clicked")
    funcsCommon.Filters.reset()
    Infos.Test.set_readonly(gvars.wnd_main.groupTestInfo, True)
    Infos.Pump.set_readonly(gvars.wnd_main.groupPumpInfo, True)


def on_clicked_go_test():
    Journal.log("Event::", "\tgo to testing clicked")
    gvars.wnd_main.stackedWidget.setCurrentIndex(1)
    funcsGraph.display_charts(gvars.markers)
    gvars.markers.repositionFor(gvars.graph_info)


def on_clicked_go_back():
    Journal.log("Event::", "\tgo back clicked")
    gvars.wnd_main.stackedWidget.setCurrentIndex(0)
    funcsGraph.display_charts(gvars.wnd_main.frameGraphInfo)


# TEST
def on_clicked_test():
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


def on_changed_test_values():
    funcsTest.move_markers()
    pass


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
    funcsCommon.Filters.apply()


def on_radio_changed():
    funcsCommon.Filters.switch_others()


def on_clicked_adam_connection():
    state = funcsAdam.changeConnectionState()
    gvars.wnd_main.checkConnection.setChecked(state)
    gvars.wnd_main.checkConnection.setText("подключено" if state else "отключено")


def on_adam_data_received(sensors: dict):
    point_data = {key: sensors[key] for key in ['rpm', 'torque', 'pressure_in', 'pressure_out']}
    point_data['flow'] = sensors[gvars.active_flowmeter]
    funcsWindow.display_sensors(sensors)


def on_markers_move(point_data: dict):
    funcsTest.display_current_marker_point(point_data)
