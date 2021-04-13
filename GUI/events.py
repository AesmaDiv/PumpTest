"""
    Модуль содержащий функции обработки событий
"""
from PyQt5.QtCore import Qt

from Functions import funcsCommon, funcsGraph, funcsMessages
from Functions import funcsTest, funcs_wnd, funcsAdam, funcsTable
from AesmaLib.journal import Journal
from Globals import gvars


def on_changed_testlist():
    """ изменение выбора теста """
    wnd = gvars.wnd_main
    item = funcsTable.get_row(wnd.tableTests)
    if item:
        Journal.log('*********************************************************')
        Journal.log(__name__, "::\t", on_changed_testlist.__doc__, "-->",
                    item['ID'] if item else "None")
        funcs_wnd.group_lock(wnd.groupTestInfo, True)
        funcs_wnd.group_lock(wnd.groupPumpInfo, True)
        Journal.log('->---------------- clearing widgets ---------------------')
        funcs_wnd.clear_record(True)
        wnd.cmbType.model().applyFilter()
        wnd.cmbSerial.model().applyFilter()
        Journal.log('=>=============== displaying new info ===================')
        funcs_wnd.display_record()
        Journal.log('=========================================================')


def on_changed_combo_producers(index):
    """ изменение выбора производителя """
    wnd = gvars.wnd_main
    item = wnd.cmbProducer.currentData(Qt.UserRole)
    if item:
        Journal.log('_________________________________________________________')
        Journal.log(__name__, "::\t", on_changed_combo_producers.__doc__, "-->",
                    item['Name'] if item else "None")
        # ↓ фильтруем типоразмеры для данного производителя
        condition = {'Producer': item['ID']} if index else None
        if not wnd.cmbType.model().check_selected(condition):
            wnd.cmbType.model().applyFilter(condition)


def on_changed_combo_types(index):
    """ изменение выбора типоразмера """
    wnd = gvars.wnd_main
    item = wnd.cmbType.currentData(Qt.UserRole)
    Journal.log('_________________________________________________________')
    Journal.log(__name__, "::\t", on_changed_combo_types.__doc__, "-->",
                item['Name'] if item else "None")
    if item:
        # ↑ выбираем производителя для данного типоразмера
        condition = {'ID': item['Producer']} if index else None
        if not wnd.cmbProducer.model().check_selected(condition) and index:
            wnd.cmbProducer.model().select_contains(condition)
        # ↓ фильтруем серийники для данного типоразмера
        condition = {'Type': item['ID']} if index else None
        if not wnd.cmbSerial.model().check_selected(condition):
            wnd.cmbSerial.model().applyFilter(condition)


def on_changed_combo_serials(index):
    """ изменение выбора заводского номера """
    wnd = gvars.wnd_main
    item = wnd.cmbSerial.currentData(Qt.UserRole)
    if item:
        Journal.log('_________________________________________________________')
        Journal.log(__name__, "::\t", on_changed_combo_serials.__doc__, "-->",
                    item['Serial'] if item else "None")
        # ↑ выбираем типоразмер для данного серийника
        condition = {'ID': item['Type']} if index else None
        if not wnd.cmbType.model().check_selected(condition) and index:
            wnd.cmbType.model().select_contains(condition)
        # funcsGraph.draw_charts()


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
    Journal.log(__name__, "::\t", on_clicked_filter_reset.__doc__)
    funcs_wnd.testlist_filter_reset()
    funcs_wnd.group_lock(gvars.wnd_main.groupTestInfo, True)
    funcs_wnd.group_lock(gvars.wnd_main.groupPumpInfo, True)


# PUMP INFO
def on_clicked_pump_new():
    """ нажата кнопка добавления нового насоса """
    Journal.log(__name__, "::\t", on_clicked_pump_new.__doc__)
    funcs_wnd.group_lock(gvars.wnd_main.groupPumpInfo, False)
    funcs_wnd.group_clear(gvars.wnd_main.groupPumpInfo)


def on_clicked_pump_save():
    """ нажата кнопка сохранения нового насоса """
    Journal.log(__name__, "::\t", on_clicked_pump_save.__doc__)
    if gvars.rec_type.check_exist({}):
        if gvars.rec_pump.check_exist({}) or gvars.rec_pump.save():
            funcs_wnd.group_lock(gvars.wnd_main.groupPumpInfo, True)
    else:
        funcsMessages.show("Ошибка", "Такого типоразмера нет в базе.")


def on_clicked_pump_cancel():
    """ нажата кнопка отмены добавления нового насоса """
    Journal.log(__name__, "::\t", on_clicked_pump_cancel.__doc__)
    wnd = gvars.wnd_main
    funcs_wnd.group_display(wnd.groupPumpInfo, gvars.rec_pump)
    funcs_wnd.group_lock(wnd.groupPumpInfo, True)


def on_clicked_test_new():
    """ нажата кнопка добавления нового теста """
    Journal.log(__name__, "::\t", on_clicked_test_new.__doc__)
    wnd = gvars.wnd_main
    funcs_wnd.group_lock(wnd.groupTestInfo, False)
    funcs_wnd.group_clear(wnd.groupTestInfo)
    funcsCommon.set_current_date()


def on_clicked_test_info_save():
    """ нажата кнопка сохранения нового теста """
    Journal.log(__name__, "::\t", on_clicked_test_info_save.__doc__)
    test_id = gvars.rec_test.check_exist()
    if test_id:
        if funcsMessages.ask("Внимание",
                             """Тест с таким наряд-заказом
                                уже присутствует в базе.
                                Хотите его выбрать?"""):
            funcsCommon.select_test(test_id)
        else:
            return
    else:
        if gvars.rec_test.save_info():
            funcs_wnd.fill_test_list()
        else:
            return
    gvars.rec_test.set_readonly(gvars.wnd_main.groupTestInfo, True)
    gvars.rec_pump.Pump.set_readonly(gvars.wnd_main.groupTestInfo, True)


def on_clicked_test_info_cancel():
    """ нажата кнопка отмены добавления нового теста """
    Journal.log(__name__, "::\t", on_clicked_test_info_cancel.__doc__)
    wnd = gvars.wnd_main
    funcs_wnd.group_display(wnd.groupTestInfo, gvars.rec_test)
    funcs_wnd.group_lock(wnd.groupTestInfo, True)


def on_clicked_test_data_save():
    """ нажата кнопка сохранения результатов теста """
    Journal.log(__name__, "::\t", on_clicked_test_data_save.__doc__)
    title = 'УСПЕХ'
    message = 'Результаты сохранены'
    if not gvars.rec_test.save_data():
        title = 'ОШИБКА'
        message = 'Запись заблокирована'
    funcsMessages.show(title, message)


def on_clicked_save():
    """ нажата кнопка сохранения """
    # gvars.wnd_main.__store_record()


def on_clicked_go_test():
    """ нажата кнопка перехода к тестированию """
    Journal.log(__name__, "::\t", on_clicked_go_test.__doc__)
    gvars.wnd_main.stackedWidget.setCurrentIndex(1)
    funcsGraph.display_charts(gvars.markers)
    gvars.markers.repositionFor(gvars.graph_info)


def on_clicked_go_back():
    """ нажата кнопка возврата на основное окно """
    Journal.log(__name__, "::\t", on_clicked_go_back.__doc__)
    gvars.wnd_main.stackedWidget.setCurrentIndex(0)
    funcsGraph.display_charts(gvars.wnd_main.frameGraphInfo)


# TEST
def on_clicked_test():
    """ нажата кнопка начала/остановки испытания """
    Journal.log(__name__, "::\t", on_clicked_test.__doc__)
    funcsTest.is_test_running = not funcsTest.is_test_running
    funcsTest.switch_charts_visibility()
    funcsTest.switch_test_running_state()


def on_clicked_add_point():
    """ нажата кнопка добавления точки """
    Journal.log(__name__, "::\t", on_clicked_add_point.__doc__)
    gvars.markers.addKnots()
    funcsTest.add_point_to_list()
    funcsTest.add_points_to_charts()
    funcsGraph.display_charts(gvars.markers)


def on_clicked_remove_point():
    """ нажата кнопка удаления точки """
    Journal.log(__name__, "::\t", on_clicked_remove_point.__doc__)
    gvars.markers.removeKnots()
    funcsTest.remove_last_point_from_list()
    funcsTest.remove_last_points_from_charts()
    funcsGraph.display_charts(gvars.markers)


def on_clicked_clear_curve():
    """ нажата кнопка удаления всех точек """
    Journal.log(__name__, "::\t", on_clicked_clear_curve.__doc__)
    gvars.markers.clearAllKnots()
    funcsTest.clear_points_from_list()
    funcsTest.clear_points_from_charts()
    funcsGraph.display_charts(gvars.markers)


def on_clicked_adam_connection():
    """ нажата кнопка подключения к ADAM5000TCP """
    Journal.log(__name__, "::\t", on_clicked_adam_connection.__doc__)
    state = funcsAdam.changeConnectionState()
    gvars.wnd_main.checkConnection.setChecked(state)
    gvars.wnd_main.checkConnection.setText("подключено" if state else "отключено")


def on_adam_data_received(sensors: dict):
    """ приход данных от ADAM5000TCP """
    Journal.log(__name__, "::\t", on_adam_data_received.__doc__)
    point_data = {key: sensors[key] for key in ['rpm', 'torque', 'pressure_in', 'pressure_out']}
    point_data['flow'] = sensors[gvars.active_flowmeter]
    funcs_wnd.display_sensors(sensors)


def on_changed_sensors():
    """ изменения значений датчиков """
    funcsTest.move_markers()


def on_markers_move(point_data: dict):
    """ изменения позиции маркеров """
    funcsTest.display_current_marker_point(point_data)
