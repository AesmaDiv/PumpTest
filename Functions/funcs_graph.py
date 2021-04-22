"""
    Модуль содержит функции работы с графиками
"""
from PyQt5.QtGui import QPalette, QBrush, QColor, QPen
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QFrame

from AesmaLib.GraphWidget.Chart import Chart
from Globals import gvars


def draw_charts():
    """ отрисовка графиков испытания """
    if gvars.pump_graph:
        gvars.pump_graph.clear_charts()
        if gvars.rec_type:
            charts = load_charts()
            for chart in charts.values():
                gvars.pump_graph.add_chart(chart, chart.getName())
            gvars.pump_graph.set_limits(gvars.rec_type['Min'],
                                        gvars.rec_type['Nom'],
                                        gvars.rec_type['Max'])
        display_charts(gvars.wnd_main.frameGraphInfo)


def display_charts(frame: QFrame):
    """ вывод графика в рисунок и в frame """
    pic = gvars.pump_graph.render_to_image(frame.size())
    palette = frame.palette()
    palette.setBrush(QPalette.Background, QBrush(pic))
    frame.setPalette(palette)
    frame.setAutoFillBackground(True)


def load_charts():
    """ загрузка данных о точках """
    points = get_points('etalon')
    result = create_charts_etalon(points)
    if gvars.rec_test:
        points = get_points('test')
        result.update(create_charts_test(points, result))
    return result


def get_points(chart_type='etalon'):
    """ парсинг значений точек из строк """
    is_etalon = (chart_type == 'etalon')
    source = gvars.rec_type if is_etalon else gvars.rec_test
    if source['Flows'] and source['Lifts'] and source['Powers']:
        try:
            flws = list(map(safe_parse_float, source['Flows'].split(',')))
            lfts = list(map(safe_parse_float, source['Lifts'].split(',')))
            pwrs = list(map(safe_parse_float ,source['Powers'].split(',')))
            if is_etalon:
                flws = flws[::-1]
                pwrs = list(map(lambda x: x * 0.7457, pwrs))
            effs = calculate_effs(flws, lfts, pwrs)
            return [flws, lfts, pwrs, effs]
        except AttributeError as ex:
            print('funcs_graph::get_points::Error:', str(ex))
    return None


def safe_parse_float(value: str):
    """ безопасная конвертация строки в число с пл.запятой """
    try:
        return float(value)
    except TypeError:
        return 0.0


def calculate_effs(flws: list, lfts: list, pwrs: list):
    """ расчёт точек КПД """
    result = []
    count = len(flws)
    if count == len(lfts) and count == len(pwrs):
        func = lambda f, l, p: 9.81 * l * f / (24 * 3600 * p)
        result = [func(flws[i], lfts[i], pwrs[i]) for i in range(count)]
    return result


def create_charts_etalon(points: list):
    """ создание кривых графиков для эталона """
    result = {}
    if points:
        ch_lft = create_chart(points[0], points[1], 'lft', 'limits')
        ch_pwr = create_chart(points[0], points[2], 'pwr', 'limits')
        ch_eff = create_chart(points[0], points[3], 'eff', '')
        ch_lft.setPen(QPen(QColor(200, 200, 255), 1), Qt.DashLine)
        ch_pwr.setPen(QPen(QColor(255, 0, 0), 1), Qt.DashLine)
        ch_eff.setPen(QPen(QColor(0, 255, 0), 1), Qt.DashLine)
        scale_chart(ch_lft, (0.95, 1.1), 0, 0)
        scale_chart(ch_pwr, (0.95, 1.1), 0, ch_lft.getAxis('y').getDivs())
        scale_chart(ch_eff, (1.0, 1.0),  0, ch_lft.getAxis('y').getDivs())
        result.update({'lft': ch_lft,
                       'pwr': ch_pwr,
                       'eff': ch_eff})
    return result


def create_charts_test(points: list, etalon_charts: dict):
    """ создание кривых графиков для проведённого испытания """
    result = {}
    if points and len(etalon_charts) == 3:
        ch_lft = create_chart(points[0], points[1], 'test_lft', 'knots')
        ch_pwr = create_chart(points[0], points[2], 'test_pwr', 'knots')
        ch_eff = create_chart(points[0], points[3], 'test_eff', 'knots')
        ch_lft.setPen(QPen(etalon_charts['lft'].getPen()), Qt.SolidLine)
        ch_pwr.setPen(QPen(etalon_charts['pwr'].getPen()), Qt.SolidLine)
        ch_eff.setPen(QPen(etalon_charts['eff'].getPen()), Qt.SolidLine)
        scale_chart(ch_lft, axes=etalon_charts['lft'].getAxes())
        scale_chart(ch_pwr, axes=etalon_charts['pwr'].getAxes())
        scale_chart(ch_eff, axes=etalon_charts['eff'].getAxes())
        result.update({'test_lft': ch_lft,
                       'test_pwr': ch_pwr,
                       'test_eff': ch_eff})
    return result


def create_chart(coords_x: list, coords_y: list, name: str, options=''):
    """ создание и настройка экземпляра класса кривой """
    points = [QPointF(x, y) for x, y in zip(coords_x, coords_y)]
    result = Chart(points, name, options=options)
    return result


def scale_chart(chart: Chart, coefs=(1.0, 1.0), ymin=0, yticks=0, axes=None):
    """ установка размерности для осей и области допуска """
    chart.setCoefs(*coefs)
    if axes:
        chart.setAxes(axes)
    else:
        chart.getAxis('y').setMinimum(ymin)
        if yticks:
            chart.getAxis('y').setDivs(yticks)
