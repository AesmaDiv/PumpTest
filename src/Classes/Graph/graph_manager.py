"""
    Модуль содержит функции работы с графиками"""
import numpy as np
from loguru import logger
# from time import time_ns

from PyQt5.QtGui import QPalette, QBrush, QColor, QPen
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QFrame

from Classes.Data.record import TestData
from Classes.Graph.pump_graph import PumpGraph
from Classes.Graph.graph_markers import Markers
from Classes.UI.funcs.funcs_aux import calculateEffs

from AesmaLib.GraphWidget.chart import Chart, ChartOptions as co


class GraphManager(PumpGraph):
    """Менеджер графиков"""
    COUNT = 1
    MARKERS_PARAMS = {
        'tst_lft': Qt.blue,    # цвет маркера напора
        'tst_pwr': Qt.red      # цвет маркера мощности
    }

    def __init__(self, testdata: TestData) -> None:
        super().__init__(100, 100, parent=None)
        self._testdata = testdata
        self._markers = None
        self._limits = {'lft':(0.95, 1.05), 'pwr': (0.92, 1.08), 'eff': (0.98, 1.02)}
        self.setMargins([10, 10, 10, 10])

    def initMarkers(self, host):
        """инициализация маркеров"""
        self._markers = Markers(GraphManager.MARKERS_PARAMS.keys(), self)
        for key, val in GraphManager.MARKERS_PARAMS.items():
            self._markers.setMarkerColor(key, val)
        host.addWidget(self._markers, 0, 0)

    def displayCharts(self, frame: QFrame):
        """отображение графиков"""
        logger.debug(self.displayCharts.__doc__)
        self._prepareCharts()
        self.drawCharts(frame)

    def drawCharts(self, frame: QFrame):
        """вывод графика в рисунок и в frame"""
        logger.debug(self.drawCharts.__doc__)
        pic = self.renderToImage(frame.size())
        palette = frame.palette()
        palette.setBrush(QPalette.Background, QBrush(pic))
        frame.setPalette(palette)
        frame.setAutoFillBackground(True)

    def _prepareCharts(self):
        """подготовка графиков к отображению"""
        logger.debug(self._prepareCharts.__doc__)
        self.clearCharts()
        if not self._testdata.type_:
            logger.warning('Нет информации о типоразмере')
            return
        charts = self._loadCharts()
        for chart in charts.values():
            self.addChart(chart, chart.name)
        self.setLimits(
            self._testdata.type_['Min'],
            self._testdata.type_['Nom'],
            self._testdata.type_['Max']
        )

    def _loadCharts(self):
        """загрузка данных о точках"""
        points = self._getPoints('etalon')
        self.COUNT += 1
        result = self.createCharts_etalon(points)
        if self._testdata.test_:
            points = self._getPoints('test')
            result.update(self.createCharts_test(points, result))
        return result

    def _getPoints(self, chart_type='etalon'):
        """парсинг значений точек из строк"""
        is_etalon = (chart_type == 'etalon')
        src = self._testdata.type_ if is_etalon else self._testdata.test_
        if src.points:
            # flws = [p.Flw for p in src.points]
            # lfts = [p.Lft for p in src.points]
            # pwrs = [p.Pwr for p in src.points]
            # ибо так быстрее
            flws, lfts, pwrs = [],[],[]
            for p in src.points:
                flws.append(p.Flw)
                lfts.append(p.Lft)
                pwrs.append(p.Pwr)
            if is_etalon:
                pwrs = list(map(lambda x: x * 0.7457, pwrs))
            effs = calculateEffs(flws, lfts, pwrs)
            return [flws, lfts, pwrs, effs]
        return [list(), list(), list(), list()]

    def createCharts_etalon(self, points: list):
        """создание кривых графиков для эталона"""
        result = {}
        if points:
            ch_lft = self._createChart(points[0], points[1], 'etl_lft', co.Limits)
            ch_pwr = self._createChart(points[0], points[2], 'etl_pwr', co.Limits)
            ch_eff = self._createChart(points[0], points[3], 'etl_eff', co.Limits)
            ch_lft.setPen(QPen(QColor(200, 200, 255), 1), Qt.DashLine)
            ch_pwr.setPen(QPen(QColor(255, 0, 0), 1), Qt.DashLine)
            ch_eff.setPen(QPen(QColor(0, 255, 0), 1), Qt.DashLine)
            self._scaleChart(ch_lft, self._limits['lft'], 0, 0)
            self._scaleChart(ch_pwr, self._limits['pwr'], 0, ch_lft.getAxis('y').getDivs())
            self._scaleChart(ch_eff, self._limits['eff'], 0, ch_lft.getAxis('y').getDivs())
            result.update({'etl_lft': ch_lft, 'etl_pwr': ch_pwr, 'etl_eff': ch_eff})
        return result


    def createCharts_test(self, points: list, etalon_charts: dict):
        """создание кривых графиков для проведённого испытания"""
        result = {}
        if points and len(etalon_charts) == 3:
            ch_lft = self._createChart(points[0], points[1], 'tst_lft', co.Knots)
            ch_pwr = self._createChart(points[0], points[2], 'tst_pwr', co.Knots)
            ch_eff = self._createChart(points[0], points[3], 'tst_eff', co.Knots)
            ch_lft.setPen(QPen(etalon_charts['etl_lft'].pen), Qt.SolidLine)
            ch_pwr.setPen(QPen(etalon_charts['etl_pwr'].pen), Qt.SolidLine)
            ch_eff.setPen(QPen(etalon_charts['etl_eff'].pen), Qt.SolidLine)
            self._scaleChart(ch_lft, axes=etalon_charts['etl_lft'].axes)
            self._scaleChart(ch_pwr, axes=etalon_charts['etl_pwr'].axes)
            self._scaleChart(ch_eff, axes=etalon_charts['etl_eff'].axes)
            result.update({'tst_lft': ch_lft, 'tst_pwr': ch_pwr, 'tst_eff': ch_eff})
        return result

    @staticmethod
    def _createChart(coords_x: list, coords_y: list, name: str, options: co=''):
        """создание и настройка экземпляра класса кривой"""
        # points = [QPointF(x, y) for x, y in zip(coords_x, coords_y)]
        # result = Chart(points, name, options=options)
        logger.debug(f">> cоздание графика для {name}")
        result = Chart([coords_x.copy(), coords_y.copy()], name, options=options)
        return result

    @staticmethod
    def _scaleChart(chart: Chart, lim_coefs=(1.0, 1.0), ymin=0, yticks=0, axes=None):
        """установка размерности для осей и области допуска"""
        logger.debug(f">> cкалирование графика для {chart.name}")
        chart.limitCoefs = lim_coefs
        if axes:
            chart.setAxes(axes)
            return
        chart.getAxis('y').setMinimum(ymin)
        if yticks:
            chart.getAxis('y').setDivs(yticks)

    def saveTestdata(self):
        """сохранение данных из таблицы в запись испытания"""
        points_lft_x = super().getChart('tst_lft').getPoints('x')
        points_lft_y = super().getChart('tst_lft').getPoints('y')
        points_pwr_y = super().getChart('tst_pwr').getPoints('y')
        self._testdata.test_['Flows'] = ','.join(list(map(str, points_lft_x)))
        self._testdata.test_['Lifts'] = ','.join(list(map(str, points_lft_y)))
        self._testdata.test_['Powers'] = ','.join(list(map(str, points_pwr_y)))

    def markersReposition(self):
        """перенос маркеров на другой холст"""
        self._markers.repositionFor(self)

    def markersMove(self, params):
        """перемещение маркеров отображающих текущие значения"""
        for param in params:
            self._markers.moveMarker(
                QPointF(param['x'], param['y']),
                param['name']
            )

    def markersAddKnots(self):
        """добавление узлов (точки)"""
        self._markers.addKnots()

    def markersRemoveKnots(self):
        """удаление узлов (точки)"""
        self._markers.removeKnots()

    def markersClearKnots(self):
        """очистка узлов (всех точек)"""
        self._markers.clearAllKnots()

    def setPointLines_max(self, value):
        """установка макс.значения расхода для линий отбивания точек"""
        self._markers.setPointLinesMax(value)

    def setPointLines_num(self, value):
        """установка кол-ва линий для отбивания точек"""
        self._markers.setPointLinesNumber(value)
        self._markers.repaint()

    def setPointLines_cur(self, value):
        """установка кол-ва линий для отбивания точек"""
        self._markers.setPointLinesCurrent(value)
        self._markers.repaint()

    def checkPointExists(self, flw) -> bool:
        """проверка есть ли точка с таким значением по Х"""
        chart: Chart = super().getChart('tst_lft')
        if chart:
            points = chart.getPoints('x')
            return flw in points
        return False

    def addPointsToCharts(self, flw, lft, pwr, eff):
        """добавление точек напора и мощности на график"""
        self._addPointToChart('tst_lft', flw, lft)
        self._addPointToChart('tst_pwr', flw, pwr)
        self._addPointToChart('tst_eff', flw, eff)

    def _addPointToChart(self, chart_name: str, value_x: float, value_y: float):
        """добавление точки на график"""
        chart: Chart = self._getChart(chart_name)
        if chart:
            logger.debug(f"добавление точки к графику: {value_x}, {value_y}")
            chart.addPoint(value_x, value_y)

    def _getChart(self, name: str):
        """получение ссылки на кривую по имени"""
        chart_name = name
        chart: Chart = super().getChart(chart_name)
        if chart:
            return chart
        # если график отсутствует берем эталонный
        logger.warning(f"Нет такой кривой {chart_name}")
        etalon: Chart = super().getChart(chart_name.replace('tst_', ''))
        if etalon:
            chart: Chart = Chart(name=chart_name)
            chart.setAxes(etalon.axes)
            chart.setPen(QPen(etalon.pen.color(), 2, Qt.SolidLine))
            self.addChart(chart, chart_name)
            return chart
        logger.error(f"Не найден эталон для {chart_name}")

    def clearPointsFromCharts(self):
        """удаление всех точек из графиков напора и мощности"""
        self._clearPointsFromChart('tst_lft')
        self._clearPointsFromChart('tst_pwr')
        self._clearPointsFromChart('tst_eff')

    def _clearPointsFromChart(self, chart_name: str):
        """удаление всех точек из графика"""
        chart = super().getChart(chart_name)
        if chart is not None:
            chart.clearPoints()

    def removeLastPointsFromCharts(self):
        """удаление последних точек из графиков напора и мощности"""
        self._removeLastPointFromChart('tst_lft')
        self._removeLastPointFromChart('tst_pwr')
        self._removeLastPointFromChart('tst_eff')

    def _removeLastPointFromChart(self, chart_name: str):
        """удаление последней точки из графика"""
        chart = super().getChart(chart_name)
        if chart is not None:
            chart.removePoint()

    def switchChartsVisibility(self, state):
        """переключение видимости для кривых"""
        # если включено - показывать все графики
        # если выключено - только тестовые (напор / мощность)
        self.setVisibleCharts(['etl_lft', 'etl_pwr', 'tst_lft', 'tst_pwr']
                                            if not state else 'all')
        # переключение видимости линий для отбивания точек
        # если выключена видимость всех - показывается линии
        self._markers.setPointLinesVis(not state)
        self.drawCharts(self._markers)

    def generateResultText(self):
        """генерирует миниотчёт об испытании"""
        self._testdata.dlts_.clear()
        result_lines = []
        self._generateDeltasReport(result_lines)
        self._generateOptimalReport(result_lines)
        return '\n'.join(result_lines)

    def _generateDeltasReport(self, lines: list):
        """расчитывает отклонения для напора и мощности"""
        for name, title in zip(('lft', 'pwr', 'eff'),('Напор', 'Мощность', 'КПД')):
            self._calculateDeltasFor(name, name != 'eff')
            string = f'\u0394 {title}, %\t'
            for val in self._testdata.dlts_[name]:
                frmt = '{:>10.2f}' if val else '-.--'
                string += f'\t{frmt}'.format(val)
            lines.append(string)

    def _calculateDeltasFor(self, chart_name: str, in_percent=True):
        """расчёт отклонения для указанной характеристики"""
        get_spl = lambda name: self.getChart(name).getSpline()
        get_val = lambda spl, rng: float(spl(self._testdata.type_[rng]))
        get_dlt = lambda tst, etl: round(100 * (tst / etl - 1) if in_percent else tst - etl, 2)
        vals, result = [], [0] * 3
        names = (f'tst_{chart_name}', f'etl_{chart_name}')
        ranges = ('Min', 'Nom', 'Max')
        try:
            splines = [get_spl(name) for name in names]
            vals = [[get_val(spline, rng) for rng in ranges] for spline in splines]
            result = [get_dlt(x, y) for x, y in zip(vals[0], vals[1])]
        except ValueError as err:
            logger.error(str(err))
        self._testdata.dlts_[chart_name] = result

    def _generateOptimalReport(self, lines: list):
        """генерирование отчета об отклонении КПД"""
        result = self._getOptimalDelta()
        # result = self._checkOptimalDelta(optimal_delta)
        frmt = '{:>10.2f}' if result else '-.--'
        string = f'Отклонение оптимальной подачи, %\t\t{frmt}'.format(result)
        lines.append(string)
        self._testdata.dlts_['flw'] = result

    def _getOptimalDelta(self):
        """получение отклонения максимального КПД от номинального"""
        result = 0.0
        chart: Chart = self.getChart("tst_eff")
        if chart:
            curve = chart.regenerateCurve()
            if len(curve):
                nominal = float(self._testdata.type_['Nom'])
                optimal = self._getEffMaxPoint(curve)[0]
                result = 100.0 * (optimal / nominal - 1)
        return result

    def _checkOptimalDelta(self, optimal_delta):
        """проверка оптимальной подачи"""
        nominal = float(self._testdata.type_['Nom'])
        limits = (-15.0, 15.0)
        if 30.0 < nominal <= 60.0:
            limits = (-15.0, 13.0)
        elif 80.0 < nominal <= 125.0:
            limits = (-15.0, 12.0)
        elif nominal > 125.0:
            limits = (-15.0, 10.0)
        return limits[0] <= optimal_delta <= limits[1]

    @staticmethod
    def _getEffMaxPoint(curve):
        """получение точки максимального КПД"""
        index = np.where(curve['y'] == max(curve['y']))[0]
        x = float(curve['x'][index])
        y = float(curve['y'][index])
        return (x, y)
