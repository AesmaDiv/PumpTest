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
    if is_logged: Journal.log(__name__, "\tswitching test running state to", str(is_test_running))
    gvars.wnd_main.btnTest.setText(__ENGIGE_MSG[is_test_running])
    gvars.wnd_main.btnGoBack.setEnabled(not is_test_running)


def switch_charts_visibility():
    # gvars.graph_info.setVisibileCharts(['lft', 'pwr', 'test_lft', 'test_pwr'] if is_test_running else 'all')
    # funcs_graph.display_charts(gvars.markers)
    pass


def move_markers():
    flw, lft, pwr = get_flw_lft_pwr()
    gvars.markers.moveMarker(QPointF(flw, lft), 'test_lft')
    gvars.markers.moveMarker(QPointF(flw, pwr), 'test_pwr')


def add_point_to_list():
    flw, lft, pwr = get_flw_lft_pwr()
    data = {'flw': flw, 'lft': lft, 'pwr': pwr}
    if is_logged: Journal.log(__name__, "\tadding point to list", data)
    funcsTable.add_row(gvars.wnd_main.tablePoints, data)
    pass


def remove_last_point_from_list():
    if is_logged: Journal.log(__name__, "\tremoving last point from list")
    funcsTable.remove_last_row(gvars.wnd_main.tablePoints)


def clear_points_from_list():
    if is_logged: Journal.log(__name__, "\tclearing points from list")
    funcsTable.clear_table(gvars.wnd_main.tablePoints)


def add_points_to_charts():
    flw, lft, pwr = get_flw_lft_pwr()
    add_point_to_chart('test_lft', flw, lft)
    add_point_to_chart('test_pwr', flw, pwr)


def add_point_to_chart(chart_name: str, value_x: float, value_y: float):
    chart: Chart = gvars.pump_graph.get_chart(chart_name)
    if chart is not None:
        print(__name__, '\t adding point to chart', value_x, value_y)
        point = QPointF(value_x, value_y)
        chart.addPoint(point)
    else:
        print(__name__, '\tError: no such chart', chart_name)
        etalon: Chart = gvars.pump_graph.get_chart(chart_name.replace('test_', ''))
        if etalon is not None:
            chart: Chart = Chart(name=chart_name)
            chart.setAxes(etalon.getAxes())
            chart.setPen(QPen(etalon.getPen().color(), 2, Qt.SolidLine))
            gvars.pump_graph.add_chart(chart, chart_name)
            add_point_to_chart(chart_name, value_x, value_y)
        else:
            print(__name__, '\tError: cant find etalon for', chart_name)


def remove_last_points_from_charts():
    remove_last_point_from_chart('test_lft')
    remove_last_point_from_chart('test_pwr')


def remove_last_point_from_chart(chart_name: str):
    chart: Chart = gvars.pump_graph.get_chart(chart_name)
    if chart is not None:
        chart.removePoint()


def clear_points_from_charts():
    clear_points_from_chart('test_lft')
    clear_points_from_chart('test_pwr')


def clear_points_from_chart(chart_name: str):
    chart: Chart = gvars.pump_graph.get_chart(chart_name)
    if chart is not None:
        chart.clearPoints()


def display_current_marker_point(data: dict):
    name = list(data.keys())[0]
    point: QPointF = list(data.values())[0]
    if 'test_lft' == name:
        gvars.wnd_main.txtFlow.setText('%.4f' % point.x())
        gvars.wnd_main.txtLift.setText('%.4f' % point.y())
    elif 'test_pwr' == name:
        gvars.wnd_main.txtPower.setText('%.4f' % point.y())
    pass


def get_chart(chart_name: str):
    chart: Chart = gvars.pump_graph.get_chart(chart_name)
    if chart is None:
        etalon: Chart = gvars.pump_graph.get_chart(chart_name.replace('test_', ''))
        if etalon is not None:
            chart: Chart = Chart(name=chart_name)
            chart.setAxes(etalon.getAxes())
            chart.setPen(QPen(etalon.getPen().color(), 2, Qt.SolidLine))
            gvars.pump_graph.add_chart(chart, chart_name)
        else:
            print(__name__, 'Error: cant find etalon for', chart_name)
    return chart


def get_flw_lft_pwr():
    flw = aesma_funcs.safe_parse_to_float(gvars.wnd_main.txtFlow.text())
    lft = aesma_funcs.safe_parse_to_float(gvars.wnd_main.txtLift.text())
    pwr = aesma_funcs.safe_parse_to_float(gvars.wnd_main.txtPower.text())
    return flw, lft, pwr

def save_test_data():
    points_lft_x = gvars.pump_graph.get_chart('test_lft').getPoints('x')
    points_lft_y = gvars.pump_graph.get_chart('test_lft').getPoints('y')
    points_pwr_x = gvars.pump_graph.get_chart('test_pwr').getPoints('x')
    points_pwr_y = gvars.pump_graph.get_chart('test_pwr').getPoints('y')
    gvars.rec_test['Flows'] = ','.join(list(map(str, points_lft_x)))
    gvars.rec_test['Lifts'] = ','.join(list(map(str, points_lft_y)))
    gvars.rec_test['Powers'] = ','.join(list(map(str, points_pwr_y)))
    pass
