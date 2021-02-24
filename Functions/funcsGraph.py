from PyQt5.QtGui import QColor, QPen
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QFrame

from AesmaLib.GraphWidget.Chart import Chart
from AesmaLib import aesma_funcs
from Globals import gvars


def draw_charts():
    if gvars.graph_info:
        gvars.graph_info.clearCharts()
        if gvars.dictType:
            charts = load_charts()
            for chart in charts.values():
                gvars.graph_info.addChart(chart, chart.getName())
            gvars.graph_info.setLimits(gvars.dictType['Min'],
                                      gvars.dictType['Nom'],
                                      gvars.dictType['Max'])
        display_charts(gvars.wnd_main.frameGraphInfo)


def display_charts(frame: QFrame):
    gvars.graph_info.renderToImage(frame.size())
    frame.setStyleSheet("QFrame { background-image: url('" + gvars.PATH_TO_PIC + "'); }")


def load_charts():
    points = get_points('ethalon')
    result = create_charts_ethalon(points)
    if gvars.dictTest:
        points = get_points('test')
        result.update(create_charts_test(points, result))
    return result


def get_points(of='ethalon'):
    is_ethalon: bool = (of == 'ethalon')
    source = gvars.dictType if is_ethalon else gvars.dictTest
    if source['Flows'] is not None and source['Lifts'] is not None and source['Powers'] is not None:
        try:
            coeff = 0.7457 if is_ethalon else 1
            flows = [aesma_funcs.safe_parse_to(float, val) for val in source['Flows'].split(',')]
            lifts = [aesma_funcs.safe_parse_to(float, val) for val in source['Lifts'].split(',')]
            powers = [aesma_funcs.safe_parse_to(float, val) * coeff for val in source['Powers'].split(',')]
            if is_ethalon:
                lifts.reverse()
                powers.reverse()
            effs = calculate_effs(flows, lifts, powers)
            return [flows, lifts, powers, effs]
        except AttributeError as ex:
            print('Error:', str(ex))
    else:
        return None


def calculate_effs(flows: list, lifts: list, powers: list):
    result = []
    count = len(flows)
    if count == len(lifts) and count == len(powers):
        for i in range(count):
            N = 9.81 * lifts[i] * flows[i] / (24 * 3600)
            eff = N / powers[i]
            # eff = flows[i] * lifts[i] / (136000 * powers[i]) * 100
            result.append(eff)
    return result


def create_charts_ethalon(points: list):
    result: dict = {}
    if points is not None:
        ch_lft: Chart = create_chart(points[0], points[1], 'lift',
                                     QPen(QColor(200, 200, 255), 1), Qt.DashLine,
                                     'limits', (0.95, 1.1), 0, 0)
        ch_pwr: Chart = create_chart(points[0], points[2], 'power',
                                     QPen(QColor(255, 0, 0), 1), Qt.DashLine,
                                     'limits', (0.95, 1.1), 0, ch_lft.getAxis('y').getDivs())
        ch_eff: Chart = create_chart(points[0], points[3], 'eff',
                                     QPen(QColor(0, 255, 0), 1), Qt.DashLine,
                                     '', (1.0, 1.0), 0, ch_lft.getAxis('y').getDivs())
        result.update({'lift': ch_lft, 'power': ch_pwr, 'eff': ch_eff})
    return result


def create_charts_test(points: list, ethalon_charts: dict):
    result: dict = {}
    if points is not None and 3 == len(ethalon_charts):
        ch_lft: Chart = create_chart(points[0], points[1], 'test_lift',
                                     ethalon_charts['lift'].getPen(), Qt.SolidLine,
                                     'knots', axes=ethalon_charts['lift'].getAxes())
        ch_pwr: Chart = create_chart(points[0], points[2], 'test_power',
                                     ethalon_charts['power'].getPen(), Qt.SolidLine,
                                     'knots', axes=ethalon_charts['power'].getAxes())
        ch_eff: Chart = create_chart(points[0], points[3], 'test_eff',
                                     ethalon_charts['eff'].getPen(), Qt.SolidLine,
                                     'knots', axes=ethalon_charts['eff'].getAxes())
        result.update({'test_lift': ch_lft, 'test_power': ch_pwr, 'test_eff': ch_eff})
    return result


def create_chart(coords_x: list, coords_y: list, name: str, pen: QPen, pen_style=Qt.SolidLine,
                 options='', coefs=(1.0, 1.0), minimum_y=0, divisions_y=0, axes=None):
    points = [QPointF(x, y) for x, y in zip(coords_x, coords_y)]
    result: Chart = Chart(points, name, options=options)
    result.setPen(QPen(pen.color(), pen.width(), style=pen_style))
    result.setCoefs(*coefs)
    if axes is None:
        result.getAxis('y').setMinimum(minimum_y)
        if divisions_y > 0:
            result.getAxis('y').setDivs(divisions_y)
    else:
        result.setAxes(axes)
    return result
