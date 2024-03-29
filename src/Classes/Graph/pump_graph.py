"""
    Модуль содержит классы компонента графика
    характеристик ЭЦН"""
from loguru import logger

from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont, QFontMetricsF
from PyQt6.QtGui import QTransform, QPixmap, QPolygonF, QPainterPath
from PyQt6.QtCore import QPointF, Qt, QSize

from AesmaLib.GraphWidget.chart import ChartOptions
from AesmaLib.GraphWidget.graph import Graph
from AesmaLib.GraphWidget.graph import Chart
from AesmaLib.GraphWidget.graph import Axis


IS_LOGGED = True
LIMIT_PEN = QPen(QColor(200, 200, 0, 40), 1, Qt.PenStyle.SolidLine)

class PumpGraph(Graph):
    """класс компонента графика характеристик ЭЦН"""
    def __init__(self, width: int, height: int, parent=None):
        Graph.__init__(self, width, height, parent)
        self.setGeometry(0, 0, width, height)
        self._range_value = [0, 0, 0]
        self._range_pixels = [0, 0, 0]
        self._grid_divs: dict = {}
        self._charts_data = {}
        # цветовые палитры для приложения или протокола
        self._palettes = {
            'application': {
                'background': QBrush(QColor(30, 30, 30)),
                'grid': {
                    'background': QBrush(QColor(50, 50, 50)),
                    'ranges': QBrush(QColor(70, 70, 70)),
                    'pen': QPen(QColor(100, 100, 100), 1),
                    'border': QPen(QColor(255, 255, 255), 2),
                    'font': QFont("times", 10)
                }
            },
            'report': {
                'background': QBrush(QColor(255, 255, 255)),
                'grid': {
                    'background': QBrush(QColor(250, 250, 250)),
                    'ranges': QBrush(QColor(230, 230, 230)),
                    'pen': QPen(QColor(50, 50, 50), 1),
                    'border': QPen(QColor(0, 0, 0), 2),
                    'font': QFont("times", 10)
                }
            }
        }
        self.switchPalette('application')

    def switchPalette(self, name='application'):
        """переключение цветовой палитры"""
        self._style = self._palettes[name]

    def renderToImage(self, size: QSize, path_to_file=None):
        """отрисовка содержимого компонента в рисунок и в файл"""
        self.setGeometry(0, 0, size.width(), size.height())
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        if path_to_file:
            pixmap.save(path_to_file)
        return pixmap

    def setLimits(self, minimum: float, nominal: float, maximum: float):
        """установка области рабочего диапазона"""
        self._range_value = list(map(float, [minimum, nominal, maximum]))

    def addChart(self, chart: Chart, name: str):
        """добавление графика"""
        Graph.addChart(self, chart, name)

    def getChart(self, name: str):
        """получение графика по имени"""
        return self._charts[name] if name in self._charts else None

    def setChartsVisibility(self, names_of_charts_to_show: list = 'all'):
        """установка флага видимости для кривых"""
        for chart in self._charts.values():
            visibility = names_of_charts_to_show == 'all' or chart.name in names_of_charts_to_show
            chart.visibility = visibility

    def clearCharts(self):
        """удаление всех кривых"""
        Graph.clearCharts(self)
        self._charts_data.clear()
        # self.set_margins([10, 10, 10, 10])

    def _drawGrid(self, painter: QPainter):
        """отрисовка сетки графика"""
        if len(self._charts) == 0:
            return
        # logger.debug(f"{self._drawGrid.__doc__} ->")
        self._calculateMargins()
        step_x, step_y = super()._getSteps()
        pen = painter.pen()
        painter.setPen(self._style['grid']['pen'])
        self._drawGridBackground(painter)
        self._drawGridRanges(painter)
        self._drawGridLines(painter, 'x0', step_x)
        self._drawGridLines(painter, 'y0', step_y)
        self._drawGridDivs_x(painter, step_x)
        self._drawGridDivs_y(painter, step_y, 'y0')
        self._drawGridDivs_y(painter, step_y, 'y1')
        self._drawGridDivs_y(painter, step_y, 'y2')
        self._drawLabels(painter)
        painter.setPen(pen)

    def _drawGridRanges(self, painter: QPainter):
        """отрисовка области рабочего диапазона"""
        # logger.debug(self._drawGridRanges.__doc__)
        self._calculateRanges()
        # расчёт раб.диапазона
        x_0 =int(self._margins[0] + self._range_pixels[0])
        x_1 =int(self._margins[0] + self._range_pixels[1])
        x_2 =int(self._margins[0] + self._range_pixels[2])
        y_0 =int(self._margins[1])
        y_1 =int(self.getDrawArea().height() + y_0)
        # отрисовка раб.диапазона
        pen = painter.pen()
        painter.setPen(self._style['grid']['border'])
        painter.fillRect(
            x_0, y_0, x_2 - x_0, y_1 - y_0,
            self._style['grid']['ranges']
        )
        painter.drawLine(x_0, y_0, x_0, y_1)
        painter.drawLine(x_1, y_0, x_1, y_1)
        painter.drawLine(x_2, y_0, x_2, y_1)
        painter.setPen(pen)

    def _drawGridLines(self, painter: QPainter, name, step):
        """отрисовка линий сетки для оси"""
        if not self._grid_divs[name].is_ready:
            return
        # logger.debug(f"{self._drawGridLines.__doc__} {name}")
        divs = self._grid_divs[name].divs
        for i in range(1, len(divs)):
            self._style['grid']['pen'].setStyle(Qt.PenStyle.SolidLine if divs[i] == 0
                else Qt.PenStyle.DotLine)
            if name == 'x0':
                coord = i * step + self._margins[0]
                p_0 = QPointF(coord, self._margins[1])
                p_1 = QPointF(coord, self.height() - self._margins[3])
            else:
                coord = (len(divs) - i) * step + self._margins[1]
                p_0 = QPointF(self._margins[0], coord)
                p_1 = QPointF(self.width() - self._margins[2], coord)
            painter.setPen(self._style['grid']['pen'])
            painter.drawLine(p_0, p_1)

    def _drawGridDivs_x(self, painter: QPainter, step: float):
        """отрисовка значений делений на оси X"""
        if not self._grid_divs['x0'].is_ready:
            return
        # logger.debug(self._drawGridDivs_x.__doc__)
        f_m = QFontMetricsF(self._style['grid']['font'])
        divs = self._grid_divs['x0'].divs
        pen = painter.pen()
        painter.setPen(self._style['grid']['border'])
        for i, div in enumerate(divs):
            text = str(div)
            offset_x = self._margins[0] - f_m.boundingRect(text).width() / 2.0
            offset_y = self.height() - self._margins[3] + f_m.height() + 5
            painter.drawText(QPointF(offset_x + i * step, offset_y), text)
        painter.setPen(pen)

    def _drawGridDivs_y(self, painter: QPainter, step: float, axis_name='y0'):
        """отрисовка значений делений на оси Y"""
        # logger.debug(f"{self._drawGridDivs_y.__doc__} {axis_name}")
        f_m = QFontMetricsF(self._style['grid']['font'])
        divs = self._grid_divs[axis_name].divs
        pen = painter.pen()
        painter.setPen(self._style['grid']['border'])
        for i in range(1, len(divs)):
            text = str(divs[i])
            offset_x = 0.0
            if axis_name == 'y0':
                offset_x = self._margins[0] - f_m.tightBoundingRect(text).width() - 10
            elif axis_name == 'y1':
                offset_x = self._margins[0] + self.getDrawArea().width() + 10
                painter.setPen(self._charts['etl_pwr'].pen)
            elif axis_name == 'y2':
                offset_x = self._margins[0] + self.getDrawArea().width() + \
                           self._grid_divs['y1'].width + 40
                painter.setPen(self._charts['etl_eff'].pen)
            offset_y = self.height() - self._margins[3] + f_m.height() / 4.0
            painter.drawText(QPointF(offset_x, offset_y - i * step), text)
        painter.setPen(pen)

    def _drawLabels(self, painter: QPainter):
        """отображение подписей на осях"""
        f_m = QFontMetricsF(self._style['grid']['font'])
        pen = painter.pen()

        text = 'Расход, м³/сутки'
        offset_x = self._margins[0] + self.getDrawArea().width() / 2
        offset_x -= f_m.tightBoundingRect(text).width() / 2
        offset_y = self.height() - self._margins[3] + f_m.height()
        offset_y += 20
        painter.setPen(self._style['grid']['border'])
        painter.drawText(QPointF(offset_x, offset_y), text)

        text = 'Напор, м'
        offset_x = 0 - f_m.height() - 5
        self._drawLabel(painter, f_m, offset_x, text)

        text = 'Мощность, кВт'
        offset_x = self._margins[0] + self.getDrawArea().width() + 10
        painter.setPen(self._charts['etl_pwr'].pen)
        self._drawLabel(painter, f_m, offset_x, text)

        text = 'КПД, %'
        offset_x = self._margins[0] + self.getDrawArea().width() + \
                   self._grid_divs['y1'].width + 40
        painter.setPen(self._charts['etl_eff'].pen)
        self._drawLabel(painter, f_m, offset_x, text)
        painter.setPen(pen)

    def _drawLabel(self, painter: QPainter, font_metrics: QFontMetricsF, offset_x, text):
        """отображение подписи оси"""
        painter.rotate(-90)
        offset_y = -self._margins[1] - self.getDrawArea().height() / 2
        offset_y -= font_metrics.tightBoundingRect(text).width() / 2
        painter.drawText(QPointF(offset_y, offset_x + 45), text)
        painter.rotate(90)

    def _drawCharts(self, painter: QPainter):
        """отрисовка всех графиков"""
        logger.debug(f"{self._drawCharts.__doc__} ->")
        transform = QTransform()
        self._prepareChartsData()
        self._setCanvasTransform(painter, transform)
        self._drawChartsLimits(painter)
        self._drawChartsKnotsAndCurves(painter)
        self._resetTransform(transform)

    def _drawChartsLimits(self, painter: QPainter):
        """отрисовка пределов допуска для всех кривых"""
        for _, data in self._charts_data.items():
            if data['limits'].size:
                self._drawLimitPolygon(painter, data['limits'])

    def _drawChartsKnotsAndCurves(self, painter: QPainter):
        """отрисовка узлов и кривых"""
        # logger.debug(f"{self._drawChartsKnotsAndCurves.__doc__} ->")
        for chart, data in self._charts_data.items():
            if not chart.visibility or not data['knots'].size:
                continue
            pen = painter.pen()
            brush = painter.brush()
            painter.setPen(chart.pen)
            painter.setBrush(chart.pen.color())
            if ChartOptions.Knots in chart.options:
                # logger.debug(f"отрисовка узлов для {chart.name}")
                PumpGraph._drawKnots(painter, data['knots'])
            painter.setBrush(brush)
            logger.debug(f"отрисовка кривой для {chart.name}")
            PumpGraph._drawCurve(painter, data['curve'])
            painter.setPen(pen)

    @staticmethod
    def _drawCurve(painter: QPainter, points):
        """отрисовка линий по точкам"""
        if not points.size:
            return
        path = QPainterPath()
        path.moveTo(QPointF(points[0][0], points[0][1]))
        for i in range(1, len(points['x'])):
            path.lineTo(QPointF(points[i][0], points[i][1]))
        painter.drawPath(path)

    @staticmethod
    def _drawKnots(painter: QPainter, points):
        """отрисовка узлов"""
        if len(points['x']) == 0:
            return
        for point in points:
            painter.drawEllipse(QPointF(point[0], point[1]), 2, 2)

    @staticmethod
    def _drawLimitPolygon(painter: QPainter, points):
        """отрисовка полигона для области допуска"""
        if not points.size:
            return
        old_pen = painter.pen()
        old_brush = painter.brush()
        polygon = QPolygonF()
        for point in points:
            polygon.append(QPointF(point[0], point[1]))
        painter.setPen(LIMIT_PEN)
        painter.setBrush(LIMIT_PEN.color())
        painter.drawPolygon(polygon, Qt.FillRule.OddEvenFill)
        painter.setBrush(old_brush)
        painter.setPen(old_pen)

    def _calculateMargins(self):
        """расчёт отступов"""
        keys = self._charts.keys()
        if 'etl_lft' not in keys or 'etl_pwr' not in keys or 'etl_eff' not in keys:
            return
        self._prepareDivs('x0', self._charts['etl_lft'].getAxis('x'))
        self._prepareDivs('y0', self._charts['etl_lft'].getAxis('y'))
        self._prepareDivs('y1', self._charts['etl_pwr'].getAxis('y'))
        self._prepareDivs('y2', self._charts['etl_eff'].getAxis('y'))
        self._margins[0] = self._grid_divs['y0'].width + 50
        self._margins[1] = 20
        self._margins[2] = self._grid_divs['y1'].width + 40 + self._grid_divs['y2'].width + 40
        self._margins[3] = self._grid_divs['x0'].height + 30

    def _calculateRanges(self):
        """расчёт рабочего диапазона"""
        chart: Chart = self._charts[self._base_chart]
        for i in range(3):
            self._range_pixels[i] = chart.translateCoordinate(
                'x', self._range_value[i], self.getDrawArea().width())

    def _setCanvasTransform(self, painter: QPainter, transform: QTransform):
        """трансформация холста"""
        self._resetTransform(transform)
        super()._setTransform(painter, transform)

    @staticmethod
    def _resetTransform(transform: QTransform):
        """сброс трансформации холста"""
        transform.setMatrix(1, 0, 0,
                            0, 1, 0,
                            0, 0, 1)

    def _prepareChartsData(self):
        """подготовка данных для формирования графика"""
        # logger.debug(f"{self._prepareChartData.__doc__} ->")
        for chart in self._charts.values():
            self._prepareChartData(chart)

    def _prepareChartData(self, chart: Chart):
        """подготовка данных для построения кривой"""
        # logger.debug(f"{self._prepareChartData.__doc__} {chart.name}")
        draw_area = self.getDrawArea()
        knots = self._getChartKnots(chart, draw_area)
        curve = self._getChartCurve(chart, draw_area)
        limit = self._getChartLimit(chart, curve)
        self._charts_data.update({chart: {'knots': knots, 'curve': curve, 'limits': limit}})

    @staticmethod
    def _getChartKnots(chart: Chart, draw_area):
        """получение координат узлов кривой"""
        # logger.debug(f"{PumpGraph._getChartKnots.__doc__} {chart.name}")
        result = chart.createEmptyPoints()
        if len(chart.getPoints('x')) > 1:
            sz_cnv = [draw_area.width(), draw_area.height()]
            result = chart.getTranslatedPoints(sz_cnv)
        return result

    @staticmethod
    def _getChartCurve(chart: Chart, draw_area):
        """получение координат точек кривой"""
        # logger.debug(f"{PumpGraph._getChartCurve.__doc__} {chart.name}")
        result = chart.createEmptyPoints()
        if len(chart.getPoints('x')) > 1:
            sz_cnv = [draw_area.width(), draw_area.height()]
            result = chart.getTranslatedPoints(sz_cnv, for_curve=True)
        return result

    def _getChartLimit(self, chart: Chart, curve):
        """получение координат точек описывающих пределы допуска"""
        result = chart.createEmptyPoints()
        if chart.limitCoefs == (1.0, 1.0):
            return result
        if ChartOptions.Limits in chart.options and curve['x'].any():
            # logger.debug(f"{self._getChartLimit.__doc__} {chart.name}")
            ranges = self._range_pixels
            result = self._sliceCurveToRange(curve, ranges)
            result = self._calculateLimitCoords(chart, result, chart.limitCoefs)
        return result

    @staticmethod
    def _sliceCurveToRange(curve, ranges):
        first, last = ranges[0], ranges[2]
        mask = curve['x'] >= first
        mask &= curve['x'] <= last
        result = curve[mask]
        return result

    @staticmethod
    def _calculateLimitCoords(chart, curve, coeffs):
        """расчёт точек кривой оприсывающей пределы допуска"""
        xs_hi = curve['x'].tolist()
        xs_lo = xs_hi[::-1]
        ys_hi = list(map(lambda x: x * coeffs[0], curve['y']))
        ys_lo = list(map(lambda x: x * coeffs[1], curve['y'][::-1]))
        result_x = xs_hi + xs_lo
        result_y = ys_hi + ys_lo
        result = chart.transposePoints([result_x, result_y])
        return result

    def _prepareDivs(self, name: str, axis: Axis):
        """подготовка значений делений на оси"""
        grid_divs = Divisions(name, self._style['grid']['font'])
        grid_divs.prepare(axis)
        self._grid_divs.update({name: grid_divs})


class Divisions:
    """Класс для делений осей графика"""
    def __init__(self, name: str, font: QFont):
        self.name = name
        self.font = font
        self.divs: list = []
        self.width: int = -1
        self.height: int = -1
        self.is_ready: bool = False

    def prepare(self, axis: Axis):
        """подготовка делений для оси"""
        # logger.debug(f"{self.prepare.__doc__} {self.name}")
        f_m = QFontMetricsF(self.font)
        self.divs.clear()
        for _, div in axis.generateDivSteps():
            div = round(div, 7)
            self.divs.append(div)
            self.updateWidth(str(div), f_m)
        self.height = f_m.height()
        self.is_ready = True

    def updateWidth(self, text: str, font_metrics: QFontMetricsF):
        """обновление ширины"""
        # rect = font_metrics.boundingRect(text)
        size = font_metrics.size(0x0100, text)
        width = size.width()
        if width > self.width:
            self.width = round(width) + 0
