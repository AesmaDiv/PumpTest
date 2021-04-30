"""
    Модуль содержит функции связаные с процессом испытания
"""
from PyQt5.QtCore import QPoint, QPointF, Qt
from PyQt5.QtGui import QPen

from AesmaLib import aesma_funcs
from AesmaLib.journal import Journal
from AesmaLib.GraphWidget.Chart import Chart
from Functions import funcsTable, funcs_graph
from Globals import gvars


is_logged = True
is_test_running = False
__ENGIGE_MSG = {False: 'ЗАПУСК ДВИГАТЕЛЯ', True: 'ОСТАНОВКА ДВИГАТЕЛЯ'}


def switch_test_running_state():
    """ переключение состояния испытания (запущен/остановлен) """
    if is_logged: Journal.log(__name__, "::\tпереключение состояния теста в",
        str(is_test_running))
    gvars.wnd_main.btnTest.setText(__ENGIGE_MSG[is_test_running])
    gvars.wnd_main.btnGoBack.setEnabled(not is_test_running)


def switch_charts_visibility():
    gvars.pump_graph.set_visibile_charts(['lft', 'pwr', 'test_lft', 'test_pwr']
                                         if is_test_running else 'all')
    funcs_graph.display_charts(gvars.markers)
    pass


def move_markers():
    """ перемещение маркеров отображающих текущие значения """
    flw, lft, pwr, _ = get_current_vals()
    gvars.markers.moveMarker(QPointF(flw, lft), 'test_lft')
    gvars.markers.moveMarker(QPointF(flw, pwr), 'test_pwr')


def add_point_to_table(flw, lft, pwr, eff):
    """ добавление точки в таблицу """
    data = {'flw': round(flw, 1),
            'lft': round(lft, 2),
            'pwr': round(pwr, 4),
            'eff': round(eff, 1)}
    funcsTable.add_row(gvars.wnd_main.tablePoints, data)
    pass


def remove_last_point_from_table():
    """ удаление последней точки из таблицы """
    if is_logged: Journal.log(__name__, "\tудаление последней точки из таблицы")
    funcsTable.remove_last_row(gvars.wnd_main.tablePoints)


def clear_points_from_table():
    """ удаление всех точек из таблицы """
    if is_logged: Journal.log(__name__, "\tудаление всех точек из таблицы")
    funcsTable.clear_table(gvars.wnd_main.tablePoints)


def add_points_to_charts(flw, lft, pwr, eff):
    """ добавление точек напора и мощности на график """
    add_point_to_chart('test_lft', flw, lft)
    add_point_to_chart('test_pwr', flw, pwr)
    add_point_to_chart('test_eff', flw, eff)


def add_point_to_chart(chart_name: str, value_x: float, value_y: float):
    """ добавление точки на график """
    chart: Chart = gvars.pump_graph.get_chart(chart_name)
    if chart is not None:
        print(__name__, '\tдобавление точки к графику', value_x, value_y)
        chart.addPoint(value_x, value_y)
    else:
        print(__name__, '\tError: нет такой кривой', chart_name)
        etalon: Chart = gvars.pump_graph.get_chart(chart_name.replace('test_', ''))
        if etalon is not None:
            chart: Chart = Chart(name=chart_name)
            chart.setAxes(etalon.getAxes())
            chart.setPen(QPen(etalon.getPen().color(), 2, Qt.SolidLine))
            gvars.pump_graph.add_chart(chart, chart_name)
            add_point_to_chart(chart_name, value_x, value_y)
        else:
            print(__name__, '\tError: не найден эталон для', chart_name)


def remove_last_points_from_charts():
    """ удаление последних точек из графиков напора и мощности """
    remove_last_point_from_chart('test_lft')
    remove_last_point_from_chart('test_pwr')
    remove_last_point_from_chart('test_eff')


def remove_last_point_from_chart(chart_name: str):
    """ удаление последней точки из графика """
    chart = gvars.pump_graph.get_chart(chart_name)
    if chart is not None:
        chart.removePoint()


def clear_points_from_charts():
    """ удаление всех точек из графиков напора и мощности """
    clear_points_from_chart('test_lft')
    clear_points_from_chart('test_pwr')
    clear_points_from_chart('test_eff')


def clear_points_from_chart(chart_name: str):
    """ удаление всех точек из графика """
    chart = gvars.pump_graph.get_chart(chart_name)
    if chart is not None:
        chart.clearPoints()


def display_current_marker_point(data: dict):
    """ отображение текущих значений маркера в соотв.полях """
    name = list(data.keys())[0]
    point: QPointF = list(data.values())[0]
    if 'test_lft' == name:
        gvars.wnd_main.txtFlow.setText('%.4f' % point.x())
        gvars.wnd_main.txtLift.setText('%.4f' % point.y())
    elif 'test_pwr' == name:
        gvars.wnd_main.txtPower.setText('%.4f' % point.y())
    pass


def get_chart(chart_name: str):
    """ получение ссылки на кривую по имени """
    chart: Chart = gvars.pump_graph.get_chart(chart_name)
    if chart is None:
        etalon: Chart = gvars.pump_graph.get_chart(chart_name.replace('test_', ''))
        if etalon is not None:
            chart: Chart = Chart(name=chart_name)
            chart.setAxes(etalon.getAxes())
            chart.setPen(QPen(etalon.getPen().color(), 2, Qt.SolidLine))
            gvars.pump_graph.add_chart(chart, chart_name)
        else:
            print(__name__, 'Error: не найден эталон для', chart_name)
    return chart


def get_current_vals():
    """ получение значений расхода, напора и мощности из соотв.полей """
    flw = aesma_funcs.parse_to_float(gvars.wnd_main.txtFlow.text())
    lft = aesma_funcs.parse_to_float(gvars.wnd_main.txtLift.text())
    pwr = aesma_funcs.parse_to_float(gvars.wnd_main.txtPower.text())
    eff = funcs_graph.calculate_effs([flw], [lft], [pwr])[0]
    return (flw, lft, pwr, eff)

def save_test_data():
    """ сохранение данных из таблицы в запись испытания """
    points_lft_x = gvars.pump_graph.get_chart('test_lft').getPoints('x')
    points_lft_y = gvars.pump_graph.get_chart('test_lft').getPoints('y')
    points_pwr_x = gvars.pump_graph.get_chart('test_pwr').getPoints('x')
    points_pwr_y = gvars.pump_graph.get_chart('test_pwr').getPoints('y')
    gvars.rec_test['Flows'] = ','.join(list(map(str, points_lft_x)))
    gvars.rec_test['Lifts'] = ','.join(list(map(str, points_lft_y)))
    gvars.rec_test['Powers'] = ','.join(list(map(str, points_pwr_y)))
