"""
    Модуль содержит функции работы с графиками
"""
from PyQt5.QtGui import QPalette, QBrush, QColor, QPen
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QFrame
from Classes.Graph.pump_graph import PumpGraph
from Classes.Graph.graph_markers import Markers
from Classes.UI.funcs_aux import calculate_effs
from AesmaLib.GraphWidget.Chart import Chart


class GraphManager(PumpGraph):
    """ Менеджер графиков """
    def __init__(self, testdata) -> None:
        super().__init__(100, 100, parent=None)
        self._testdata = testdata
        self._markers = None
        self.set_margins([10, 10, 10, 10])

    def init_markers(self, params, host):
        self._markers = Markers(params.keys(), self)
        for key, val in params.items():
            self._markers.setMarkerColor(key, val)
        host.addWidget(self._markers, 0, 0)

    def draw_charts(self, frame: QFrame):
        """ отрисовка графиков испытания """
        self.clear_charts()
        if self._testdata.type_:
            charts = self.load_charts()
            for chart in charts.values():
                self.add_chart(chart, chart.name)
            self.set_limits(self._testdata.type_['Min'],
                            self._testdata.type_['Nom'],
                            self._testdata.type_['Max'])
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
        if self._testdata.test_:
            points = self.get_points('test')
            result.update(self.create_charts_test(points, result))
        return result

    def get_points(self, chart_type='etalon'):
        """ парсинг значений точек из строк """
        is_etalon = (chart_type == 'etalon')
        src = self._testdata.type_ if is_etalon else self._testdata.test_
        if src.num_points:
            flws = src.values_flw
            lfts = src.values_lft
            pwrs = src.values_pwr
            if is_etalon:
                pwrs = list(map(lambda x: x * 0.7457, pwrs))
            effs = calculate_effs(flws, lfts, pwrs)
            return [flws, lfts, pwrs, effs]
        return None

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
        # points_pwr_x = super().get_chart('test_pwr').getPoints('x')
        points_pwr_y = super().get_chart('test_pwr').getPoints('y')
        self._testdata.test_['Flows'] = ','.join(list(map(str, points_lft_x)))
        self._testdata.test_['Lifts'] = ','.join(list(map(str, points_lft_y)))
        self._testdata.test_['Powers'] = ','.join(list(map(str, points_pwr_y)))

    def markers_reposition(self):
        self._markers.repositionFor(self)

    def markers_move(self, params):
        """ перемещение маркеров отображающих текущие значения """
        for param in params:
            self._markers.moveMarker(
                QPointF(param['x'], param['y']),
                param['name']
            )

    def markers_add_knots(self):
        self._markers.addKnots()

    def markers_remove_knots(self):
        self._markers.removeKnots()

    def markers_clear_knots(self):
        self._markers.clearAllKnots()

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

    def generate_result_text(self):
        """ генерирует миниотчёт об испытании """
        self._testdata.dlts_.clear()
        result_lines = []
        if self._testdata.test_['Flows']:
            self.generate_deltas_report(result_lines)
            self.generate_effs_report(result_lines)
        return '\n'.join(result_lines)


    def generate_deltas_report(self, lines: list):
        """ расчитывает отклонения для напора и мощности """
        for name, title in zip(('lft', 'pwr'),('Напор', 'Мощность')):
            self.calculate_deltas_for(name)
            string = f'\u0394 {title}, %\t'
            string += '\t{:>10.2f}\t{:>10.2f}\t{:>10.2f}'.format(*self._testdata.dlts_[name])
            lines.append(string)

    def generate_effs_report(self, lines: list):
        """ расчитывает отклонения для кпд """
        chart = self.get_chart('test_eff')
        spline = chart.getSpline()
        curve = chart.regenerateCurve()
        nom = self._testdata.type_['Nom']
        eff_nom = float(spline(nom))
        eff_max = float(max(curve['y']))
        eff_dlt = abs(eff_max - eff_nom)
        string = 'Отклонение КПД от номинального, %\t{:>10.2f}'.format(eff_dlt)
        lines.append(string)
        self._testdata.dlts_['eff'] = eff_dlt

    def calculate_deltas_for(self, chart_name: str):
        """ расчитывает отклонения для указанной характеристики """
        names = (f'test_{chart_name}', f'{chart_name}')
        ranges = ('Min', 'Nom', 'Max')
        get_val = lambda spl, rng: float(spl(self._testdata.type_[rng]))
        get_dlt = lambda tst, etl: round((tst / etl * 100 - 100), 2)
        vals = []
        for name in names:
            spln = self.get_chart(f'{name}').getSpline()
            vals.append([get_val(spln, rng) for rng in ranges])
        result = [get_dlt(x, y) for x, y in zip(vals[0], vals[1])]
        self._testdata.dlts_[name] = result