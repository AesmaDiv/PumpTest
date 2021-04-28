"""
    Модуль содержащий функции обработки событий
"""
from PyQt5.QtCore import Qt

from Functions import funcs_common, funcs_messages, funcs_graph, funcs_temp
from Functions import funcs_db, funcs_wnd, funcs_test, funcsAdam, funcsTable
from AesmaLib.journal import Journal
from Globals import gvars


def on_changed_testlist():
    """ изменение выбора теста """
    wnd = gvars.wnd_main
    item = funcsTable.get_row(wnd.tableTests)
    if item:
        # Journal.log('*********************************************************')
        Journal.log('***' * 30)
        Journal.log(__name__, "::\t", on_changed_testlist.__doc__, "-->",
                    item['ID'] if item else "None")
        funcs_wnd.combos_filters_reset()
        funcs_wnd.clear_record(True)
        funcs_wnd.display_record()
        funcs_wnd.display_test_result()
        Journal.log('===' * 30)


def on_changed_combo_producers(index):
    """ изменение выбора производителя """
    wnd = gvars.wnd_main
    item = wnd.cmbProducer.currentData(Qt.UserRole)
    if item:
        Journal.log(__name__, "::\t", on_changed_combo_producers.__doc__, "-->",
                    item['Name'] if item else "None")
        # ↓ фильтрует типоразмеры для данного производителя
        condition = {'Producer': item['ID']} if index else None
        if not wnd.cmbType.model().check_selected(condition):
            wnd.cmbType.model().applyFilter(condition)


def on_changed_combo_types(index):
    """ изменение выбора типоразмера """
    wnd = gvars.wnd_main
    item = wnd.cmbType.currentData(Qt.UserRole)
    if item:
        Journal.log(__name__, "::\t", on_changed_combo_types.__doc__, "-->",
                    item['Name'] if item else "None")
        # ↑ выбирает производителя для данного типоразмера
        condition = {'ID': item['Producer']} if index else None
        if not wnd.cmbProducer.model().check_selected(condition) and index:
            wnd.cmbProducer.model().select_contains(condition)
        # ↓ фильтрует серийники для данного типоразмера
        condition = {'Type': item['ID']} if index else None
        if not wnd.cmbSerial.model().check_selected(condition):
            wnd.cmbSerial.model().applyFilter(condition)


def on_changed_combo_serials(index):
    """ изменение выбора заводского номера """
    wnd = gvars.wnd_main
    item = wnd.cmbSerial.currentData(Qt.UserRole)
    if item:
        Journal.log(__name__, "::\t", on_changed_combo_serials.__doc__, "-->",
                    item['Serial'] if item else "None")
        # ↑ выбирает типоразмер для данного серийника
        condition = {'ID': item['Type']} if index else None
        if not wnd.cmbType.model().check_selected(condition) and index:
            wnd.cmbType.model().select_contains(condition)
        funcs_graph.draw_charts()


def on_changed_testlist_column():
    """ изменён столбец списка тестов """
    Journal.log(__name__, "::\t", on_changed_testlist_column.__doc__)
    funcs_wnd.testlist_filter_switch()


def on_changed_filter_apply(text: str):
    """ изменён значение фильтра списка тестов """
    if text:
        Journal.log(__name__, "::\t", on_changed_filter_apply.__doc__, "-->",
                    text)
    funcs_wnd.testlist_filter_apply()


def on_clicked_filter_reset():
    """ нажата кнопка сброса фильтра """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_filter_reset.__doc__)
    funcs_wnd.testlist_filter_reset()
    funcs_wnd.group_lock(gvars.wnd_main.groupTestInfo, True)
    funcs_wnd.group_lock(gvars.wnd_main.groupPumpInfo, True)


def on_clicked_pump_new():
    """ нажата кнопка добавления нового насоса """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_pump_new.__doc__)
    funcs_wnd.group_lock(gvars.wnd_main.groupPumpInfo, False)
    funcs_wnd.group_clear(gvars.wnd_main.groupPumpInfo)


def on_clicked_pump_save():
    """ нажата кнопка сохранения нового насоса """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_pump_save.__doc__)
    pump_id, do_select = funcs_common.check_exists_serial()
    if do_select:
        funcs_wnd.display_pump(pump_id['ID'])
    if not pump_id and funcs_wnd.group_check(gvars.wnd_main.groupPumpInfo):
        if funcs_wnd.save_pump_info():
            funcs_wnd.fill_combos_pump()
            gvars.wnd_main.cmbSerial.model().select_contains(gvars.rec_pump.ID)


def on_clicked_pump_cancel():
    """ нажата кнопка отмены добавления нового насоса """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_pump_cancel.__doc__)
    wnd = gvars.wnd_main
    # funcs_wnd.display_record()
    funcs_wnd.combos_filters_reset()
    funcs_wnd.group_display(wnd.groupPumpInfo, gvars.rec_pump)
    funcs_wnd.group_lock(wnd.groupPumpInfo, True)


def on_clicked_test_new():
    """ нажата кнопка добавления нового теста """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_test_new.__doc__)
    wnd = gvars.wnd_main
    funcs_wnd.group_lock(wnd.groupTestInfo, False)
    funcs_wnd.group_clear(wnd.groupTestInfo)
    funcs_common.set_current_date()


def on_clicked_test_info_save():
    """ нажата кнопка сохранения нового теста """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_test_info_save.__doc__)
    test_id = funcs_common.check_exists_ordernum(with_select=True)
    if not test_id and funcs_wnd.group_check(gvars.wnd_main.groupTestInfo):
        funcs_wnd.save_test_info()
        funcs_wnd.fill_test_list()


def on_clicked_test_info_cancel():
    """ нажата кнопка отмены добавления нового теста """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_test_info_cancel.__doc__)
    wnd = gvars.wnd_main
    funcs_wnd.group_display(wnd.groupTestInfo, gvars.rec_test)
    funcs_wnd.group_lock(wnd.groupTestInfo, True)


def on_clicked_test_data_save():
    """ нажата кнопка сохранения результатов теста """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_test_data_save.__doc__)
    title = 'УСПЕХ'
    message = 'Результаты сохранены'
    funcs_test.save_test_data()
    if not gvars.rec_test.save():
        title = 'ОШИБКА'
        message = 'Запись заблокирована'
    funcs_messages.show(title, message)


def on_clicked_save():
    """ нажата кнопка сохранения """
    # gvars.wnd_main.__store_record()


def on_clicked_go_test():
    """ нажата кнопка перехода к тестированию """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_go_test.__doc__)
    gvars.wnd_main.stackedWidget.setCurrentIndex(1)
    funcs_graph.display_charts(gvars.markers)
    gvars.markers.repositionFor(gvars.pump_graph)


def on_clicked_go_back():
    """ нажата кнопка возврата на основное окно """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_go_back.__doc__)
    gvars.wnd_main.stackedWidget.setCurrentIndex(0)
    funcs_common.select_test(gvars.rec_test['ID'])


def on_clicked_test():
    """ нажата кнопка начала/остановки испытания """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_test.__doc__)
    funcs_test.is_test_running = not funcs_test.is_test_running
    funcs_test.switch_charts_visibility()
    funcs_test.switch_test_running_state()


def on_clicked_add_point():
    """ нажата кнопка добавления точки """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_add_point.__doc__)
    gvars.markers.addKnots()
    current_vals = funcs_test.get_current_vals()
    funcs_test.add_point_to_table(*current_vals)
    funcs_test.add_points_to_charts(*current_vals)
    funcs_graph.display_charts(gvars.markers)


def on_clicked_remove_point():
    """ нажата кнопка удаления точки """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_remove_point.__doc__)
    gvars.markers.removeKnots()
    funcs_test.remove_last_point_from_table()
    funcs_test.remove_last_points_from_charts()
    funcs_graph.display_charts(gvars.markers)


def on_clicked_clear_curve():
    """ нажата кнопка удаления всех точек """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_clear_curve.__doc__)
    gvars.markers.clearAllKnots()
    funcs_test.clear_points_from_table()
    funcs_test.clear_points_from_charts()
    funcs_graph.display_charts(gvars.markers)


def on_clicked_adam_connection():
    """ нажата кнопка подключения к ADAM5000TCP """
    Journal.log('___' * 30)
    Journal.log(__name__, "::\t", on_clicked_adam_connection.__doc__)
    state = funcsAdam.changeConnectionState()
    gvars.wnd_main.checkConnection.setChecked(state)
    gvars.wnd_main.checkConnection.setText("подключено" if state else "отключено")


def on_adam_data_received(sensors: dict):
    """ приход данных от ADAM5000TCP """
    Journal.log(__name__, "::\t", on_adam_data_received.__doc__)
    point_data = {key: sensors[key] for key 
                  in ['rpm', 'torque', 'pressure_in', 'pressure_out']}
    point_data['flw'] = sensors[gvars.active_flwmeter]
    funcs_wnd.display_sensors(sensors)


def on_changed_sensors():
    """ изменения значений датчиков """
    funcs_test.move_markers()


def on_markers_move(point_data: dict):
    """ изменения позиции маркеров """
    funcs_test.display_current_marker_point(point_data)


def on_mouse_wheel_flow(event):
    funcs_temp.process_mouse_wheel(
        gvars.wnd_main.txtFlow, event, 1)


def on_mouse_wheel_lift(event):
    funcs_temp.process_mouse_wheel(
        gvars.wnd_main.txtLift, event, 0.1)


def on_mouse_wheel_power(event):
    funcs_temp.process_mouse_wheel(
        gvars.wnd_main.txtPower, event, 0.001)