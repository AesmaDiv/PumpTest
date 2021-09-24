"""
    Модуль содержит функции работы с графиками
"""
from GUI.pump_graph import PumpGraph
from PyQt5.QtGui import QPalette, QBrush, QColor, QPen
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QFrame

from AesmaLib.GraphWidget.Chart import Chart
from Classes.record import TestInfo
from Classes.graph_markers import Markers


class GraphManager(PumpGraph):
    """ Менеджер графиков """

    def __init__(self, test_info) -> None:
        super().__init__(100, 100, parent=None)
        self._info: TestInfo = test_info
        self._markers: Markers = None
        self.set_margins([10, 10, 10, 10])
        self.create_markers()

    def create_markers(self):
        self._markers = Markers(['test_lft', 'test_pwr'], self)
        self._markers.setMarkerColor('test_lft', Qt.blue)
        self._markers.setMarkerColor('test_pwr', Qt.red)

    def markers(self):
        return self._markers

    def draw_charts(self, frame: QFrame):
        """ отрисовка графиков испытания """
        self.clear_charts()
        if self._info.type_:
            charts = self.load_charts()
            for chart in charts.values():
                self.add_chart(chart, chart.name)
            self.set_limits(self._info.type_['Min'],
                            self._info.type_['Nom'],
                            self._info.type_['Max'])
        self.display_charts(frame)

    def display_charts(self, frame: QFrame):
        """ вывод графика в рисунок и в frame """
        pic = self.render_to_image(frame.size())
        palette = frame.palette()
        palette.setBrush(QPalette.Background, QBrush(pic))
        frame.setPalette(palette)
        frame.setAutoFillBackground(True)

    def load_charts(self):
        """ загрузка данных о точках """
        points = self.get_points('etalon')
        result = self.create_charts_etalon(points)
        if self._info.test_:
            points = self.get_points('test')
            result.update(self.create_charts_test(points, result))
        return result

    def get_points(self, chart_type='etalon'):
        """ парсинг значений точек из строк """
        is_etalon = (chart_type == 'etalon')
        src = self._info.type_ if is_etalon else self._info.test_
        if src.num_points:
            flws = src.values_flw
            lfts = src.values_lft
            pwrs = src.values_pwr
            if is_etalon:
                pwrs = list(map(lambda x: x * 0.7457, pwrs))
            effs = self.calculate_effs(flws, lfts, pwrs)
            return [flws, lfts, pwrs, effs]
        return None

    def calculate_effs(self, flws: list, lfts: list, pwrs: list):
        """ расчёт точек КПД """
        result = []
        count = len(flws)
        if count == len(lfts) and count == len(pwrs):
            result = [self.calculate_eff(flws[i], lfts[i], pwrs[i]) \
                    for i in range(count)]
        return result

    def calculate_eff(self, flw: float, lft: float, pwr: float):
        """ вычисление КПД """
        return 9.81 * lft * flw / (24 * 3600 * pwr) * 100 \
            if flw and lft and pwr else 0

    def create_charts_etalon(self, points: list):
        """ создание кривых графиков для эталона """
        result = {}
        if points:
            ch_lft = self.create_chart(points[0], points[1], 'lft', 'limits')
            ch_pwr = self.create_chart(points[0], points[2], 'pwr', 'limits')
            ch_eff = self.create_chart(points[0], points[3], 'eff', '')
            ch_lft.setPen(QPen(QColor(200, 200, 255), 1), Qt.DashLine)
            ch_pwr.setPen(QPen(QColor(255, 0, 0), 1), Qt.DashLine)
            ch_eff.setPen(QPen(QColor(0, 255, 0), 1), Qt.DashLine)
            self.scale_chart(ch_lft, (0.95, 1.1), 0, 0)
            self.scale_chart(ch_pwr, (0.95, 1.1), 0, ch_lft.getAxis('y').getDivs())
            self.scale_chart(ch_eff, (1.0, 1.0),  0, ch_lft.getAxis('y').getDivs())
            result.update({'lft': ch_lft,
                        'pwr': ch_pwr,
                        'eff': ch_eff})
        return result

    def create_charts_test(self, points: list, etalon_charts: dict):
        """ создание кривых графиков для проведённого испытания """
        result = {}
        if points and len(etalon_charts) == 3:
            ch_lft = self.create_chart(points[0], points[1], 'test_lft', 'knots')
            ch_pwr = self.create_chart(points[0], points[2], 'test_pwr', 'knots')
            ch_eff = self.create_chart(points[0], points[3], 'test_eff', 'knots')
            ch_lft.setPen(QPen(etalon_charts['lft'].getPen()), Qt.SolidLine)
            ch_pwr.setPen(QPen(etalon_charts['pwr'].getPen()), Qt.SolidLine)
            ch_eff.setPen(QPen(etalon_charts['eff'].getPen()), Qt.SolidLine)
            self.scale_chart(ch_lft, axes=etalon_charts['lft'].getAxes())
            self.scale_chart(ch_pwr, axes=etalon_charts['pwr'].getAxes())
            self.scale_chart(ch_eff, axes=etalon_charts['eff'].getAxes())
            result.update({'test_lft': ch_lft,
                        'test_pwr': ch_pwr,
                        'test_eff': ch_eff})
        return result

    def create_chart(self, coords_x: list, coords_y: list, name: str, options=''):
        """ создание и настройка экземпляра класса кривой """
        # points = [QPointF(x, y) for x, y in zip(coords_x, coords_y)]
        # result = Chart(points, name, options=options)
        result = Chart([coords_x.copy(), coords_y.copy()], name, options=options)
        return result

    def scale_chart(self, chart: Chart, coefs=(1.0, 1.0), ymin=0, yticks=0, axes=None):
        """ установка размерности для осей и области допуска """
        chart.setCoefs(*coefs)
        if axes:
            chart.setAxes(axes)
        else:
            chart.getAxis('y').setMinimum(ymin)
            if yticks:
                chart.getAxis('y').setDivs(yticks)

    def save_test_data(self):
        """ сохранение данных из таблицы в запись испытания """
        points_lft_x = super().get_chart('test_lft').getPoints('x')
        points_lft_y = super().get_chart('test_lft').getPoints('y')
        points_pwr_x = super().get_chart('test_pwr').getPoints('x')
        points_pwr_y = super().get_chart('test_pwr').getPoints('y')
        self._info.test_['Flows'] = ','.join(list(map(str, points_lft_x)))
        self._info.test_['Lifts'] = ','.join(list(map(str, points_lft_y)))
        self._info.test_['Powers'] = ','.join(list(map(str, points_pwr_y)))


    def move_markers(self, vals):
        """ перемещение маркеров отображающих текущие значения """
        flw, lft, pwr, _ = vals
        self._markers.moveMarker(QPointF(flw, lft), 'test_lft')
        self._markers.moveMarker(QPointF(flw, pwr), 'test_pwr')

    def add_points_to_charts(self, flw, lft, pwr, eff):
        """ добавление точек напора и мощности на график """
        self.add_point_to_chart('test_lft', flw, lft)
        self.add_point_to_chart('test_pwr', flw, pwr)
        self.add_point_to_chart('test_eff', flw, eff)

    def add_point_to_chart(self, chart_name: str, value_x: float, value_y: float):
        """ добавление точки на график """
        chart: Chart = super().get_chart(chart_name)
        if chart is not None:
            print(__name__, '\tдобавление точки к графику', value_x, value_y)
            chart.addPoint(value_x, value_y)
        else:
            print(__name__, '\tError: нет такой кривой', chart_name)
            etalon: Chart = super().get_chart(chart_name.replace('test_', ''))
            if etalon is not None:
                chart: Chart = Chart(name=chart_name)
                chart.setAxes(etalon.getAxes())
                chart.setPen(QPen(etalon.getPen().color(), 2, Qt.SolidLine))
                self.add_chart(chart, chart_name)
                self.add_point_to_chart(chart_name, value_x, value_y)
            else:
                print(__name__, '\tError: не найден эталон для', chart_name)

    def get_chart(self, chart_name: str):
        """ получение ссылки на кривую по имени """
        chart: Chart = super().get_chart(chart_name)
        if chart is None:
            etalon: Chart = super().get_chart(chart_name.replace('test_', ''))
            if etalon is not None:
                chart: Chart = Chart(name=chart_name)
                chart.setAxes(etalon.getAxes())
                chart.setPen(QPen(etalon.getPen().color(), 2, Qt.SolidLine))
                self.add_chart(chart, chart_name)
            else:
                print(__name__, 'Error: не найден эталон для', chart_name)
        return chart

    def clear_points_from_charts(self):
        """ удаление всех точек из графиков напора и мощности """
        self.clear_points_from_chart('test_lft')
        self.clear_points_from_chart('test_pwr')
        self.clear_points_from_chart('test_eff')


    def clear_points_from_chart(self, chart_name: str):
        """ удаление всех точек из графика """
        chart = super().get_chart(chart_name)
        if chart is not None:
            chart.clearPoints()

    def remove_last_points_from_charts(self):
        """ удаление последних точек из графиков напора и мощности """
        self.remove_last_point_from_chart('test_lft')
        self.remove_last_point_from_chart('test_pwr')
        self.remove_last_point_from_chart('test_eff')


    def remove_last_point_from_chart(self, chart_name: str):
        """ удаление последней точки из графика """
        chart = super().get_chart(chart_name)
        if chart is not None:
            chart.removePoint()

    def switch_charts_visibility(self, state):
        self.set_visibile_charts(['lft', 'pwr', 'test_lft', 'test_pwr']
                                            if state else 'all')
        self.display_charts(self._markers)
