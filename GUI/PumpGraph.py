from PyQt5.QtGui import QPainter, QColor, QBrush, QFont, QPolygonF, QPen, QTransform, QPixmap
from PyQt5.QtGui import QFontMetricsF, QShowEvent
from PyQt5.QtCore import QPointF, Qt, QSize
from AesmaLib.GraphWidget.Graph import Graph, Chart, Axis
from AesmaLib import aesma_funcs
from AesmaLib.journal import Journal


is_logged = True
is_limits_polygon = True
limits_pen = QPen(QColor(200, 200, 0, 20), 1, Qt.SolidLine)


class PumpGraph(Graph):
    def __init__(self, width: int, height: int, path_to_pic: str, parent=None):
        Graph.__init__(self, width, height, parent)
        self.setGeometry(0, 0, width, height)
        self._limits_value = [0, 0, 0]
        self._limits_pixel = [0, 0, 0]
        self._grid_divs: dict = {}
        self._charts_data = {}
        self._path_to_pic = path_to_pic

    def renderToImage(self, size: QSize):
        self.setGeometry(0, 0, size.width(), size.height())
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        pixmap.save(self._path_to_pic)

    def setLimits(self, minimum: float, nominal: float, maximum: float):
        self._limits_value = [minimum, nominal, maximum]

    def addChart(self, chart: Chart, name: str):
        Graph.addChart(self, chart, name)

    def getChart(self, name: str):
        if name in self._charts:
            return self._charts[name]
        return None

    def paintEvent(self, event):
        super(PumpGraph, self).paintEvent(event)

    def setVisibileCharts(self, names_of_charts_to_show: list = 'all'):
        for chart in self._charts.values():
            chart.setVisibility(names_of_charts_to_show == 'all' or chart.getName() in names_of_charts_to_show)

    def clearCharts(self):
        Graph.clearCharts(self)
        self.clearChartsData()
        self.setMargins([10, 10, 10, 10])

    def clearChartsData(self):
        if is_logged: Journal.log(__name__, "\tclearing charts data")
        self._charts_data.clear()

    def _drawGrid(self, painter: QPainter):
        if len(self._charts):
            if is_logged: Journal.log(__name__, "\tdrawGrid ->")
            self._calculateMargins()

            step_x = self.getDrawArea().width() / self._divs_x
            step_y = self.getDrawArea().height() / self._divs_y

            pen = painter.pen()
            painter.setPen(self._grid_pen)
            self._drawGridBackground(painter)
            self._drawGridRanges(painter)
            self._drawGridLinesX(painter, step_x)
            self._drawGridLinesY(painter, step_y)
            self._drawGridDivsX(painter, step_x)
            self._drawGridDivsY(painter, step_y, 'y0')
            self._drawGridDivsY(painter, step_y, 'y1')
            self._drawGridDivsY(painter, step_y, 'y2')
            painter.setPen(pen)

    def _drawGridRanges(self, painter: QPainter):
        if is_logged: Journal.log(__name__, "\tdrawing grid ranges")
        self._calculateLimits()
        x0 = self._margins[0] + self._limits_pixel[0]
        x1 = self._margins[0] + self._limits_pixel[1]
        x2 = self._margins[0] + self._limits_pixel[2]
        y0 = self._margins[1]
        y1 = self.getDrawArea().height() + y0
        pen = painter.pen()
        painter.setPen(self._grid_border_pen)
        painter.fillRect(
            x0, y0, x2 - x0, y1 - y0,
            QBrush(QColor(70, 70, 70))
        )
        painter.drawLine(x0, y0, x0, y1)
        painter.drawLine(x1, y0, x1, y1)
        painter.drawLine(x2, y0, x2, y1)
        painter.setPen(pen)

    def _drawGridLinesX(self, painter: QPainter, step: float):
        if self._grid_divs['x0'].is_ready:
            if is_logged: Journal.log(__name__, "\tdrawing grid lines X")
            divs = self._grid_divs['x0'].divs
            for i in range(len(divs)):
                self._grid_pen.setStyle(Qt.SolidLine if divs[i] == 0 else Qt.DotLine)
                coord = i * step + self._margins[0]
                painter.setPen(self._grid_pen)
                painter.drawLine(QPointF(coord,
                                         self._margins[1]),
                                 QPointF(coord,
                                         self.height() - self._margins[3]))
        else:
            if is_logged: Journal.log(__name__, "\tError -> grid divs X not ready")

    def _drawGridLinesY(self, painter: QPainter, step: float):
        if self._grid_divs['y0'].is_ready:
            if is_logged: Journal.log(__name__, "\tdrawing grid lines Y")
            divs = self._grid_divs['y0'].divs
            for i in range(1, len(divs)):
                self._grid_pen.setStyle(Qt.SolidLine if divs[i] == 0 else Qt.DotLine)
                coord = (len(divs) - i) * step + self._margins[1]
                painter.setPen(self._grid_pen)
                painter.drawLine(QPointF(self._margins[0],
                                         coord),
                                 QPointF(self.width() - self._margins[2],
                                         coord))
        else:
            if is_logged: Journal.log(__name__, "\tError -> grid divs Y not ready")

    def _drawGridDivsX(self, painter: QPainter, step: float):
        if self._grid_divs['x0'].is_ready:
            if is_logged: Journal.log(__name__, "\tdrawing grid divisions X")
            fm = QFontMetricsF(self._grid_font)
            divs = self._grid_divs['x0'].divs
            pen = painter.pen()
            painter.setPen(self._grid_border_pen)
            for i in range(len(divs)):
                text = str(divs[i])
                offset_x = self._margins[0] - fm.boundingRect(text).width() / 2.0
                offset_y = self.height() - self._margins[3] + fm.height() + 5
                painter.drawText(QPointF(offset_x + i * step,
                                         offset_y),
                                 text)
            painter.setPen(pen)

    def _drawGridDivsY(self, painter: QPainter, step: float, axis_name='y0'):
        if self._grid_divs[axis_name].is_ready:
            if is_logged: Journal.log(__name__, "\tdrawing grid divisions Y", axis_name)
            fm = QFontMetricsF(self._grid_font)
            divs = self._grid_divs[axis_name].divs
            pen = painter.pen()
            painter.setPen(self._grid_border_pen)
            for i in range(1, len(divs)):
                text = str(divs[i])
                offset_x = 0.0
                if axis_name == 'y0':
                    offset_x = self._margins[0] - fm.width(text) - 10
                elif axis_name == 'y1':
                    offset_x = self._margins[0] + self.getDrawArea().width() + 5
                    painter.setPen(self._charts['power'].getPen())
                elif axis_name == 'y2':
                    offset_x = self._margins[0] + self.getDrawArea().width() + self._grid_divs['y1'].width + 20
                    painter.setPen(self._charts['eff'].getPen())
                offset_y = self.height() - self._margins[3] + fm.height() / 4.0
                painter.drawText(QPointF(offset_x, offset_y - i * step), text)
            painter.setPen(pen)

    def _drawCharts(self, painter: QPainter):
        if is_logged: Journal.log(__name__, "\tdrawCharts ->")
        transform: QTransform = QTransform()
        self._preparingChartsData()
        self._setCanvasTransform(painter, transform)
        self._drawChartsLimits(painter)
        self._drawChartsKnotsAndCurves(painter)
        self._resetTransform(transform)

    def _drawChartsLimits(self, painter: QPainter):
        for chart, data in self._charts_data.items():
            if data['limits']:
                self._drawLimits(painter, data['limits'], chart)

    def _drawChartsKnotsAndCurves(self, painter: QPainter):
        if is_logged: Journal.log(__name__, "\tdrawing charts curves and knots")
        for chart, data in self._charts_data.items():
            if len(data['knots']) > 1:
                if chart.getVisibility():
                    pen = painter.pen()
                    brush = painter.brush()
                    painter.setPen(chart.getPen())
                    painter.setBrush(chart.getPen().color())
                    if "knots" in chart.getOptions():
                        if is_logged: Journal.log(__name__, "\tdrawing knots for", chart.getName())
                        self._drawKnots(painter, data['knots'])
                    painter.setBrush(brush)
                    if is_logged: Journal.log(__name__, "\tdrawing curve for", chart.getName())
                    Graph.drawCurve(painter, data['curve'], chart.getPen())
                    painter.setPen(pen)

    def _drawLimits(self, painter: QPainter, limits: list, chart: Chart):
        if is_logged: Journal.log(__name__, "\tdrawing limits for", chart.getName())
        points_hi, points_lo = limits
        if is_limits_polygon:
            self._drawCurveLimitPolygon(painter, points_hi + points_lo)
        else:
            self._drawCurveLimitLines(painter, points_hi, points_lo)

    def _drawKnots(self, painter: QPainter, points: list):
        for point in points:
            painter.drawEllipse(point, 2, 2)

    def _drawCurveLimitPolygon(self, painter: QPainter, points: list):
        old_pen = painter.pen()
        old_brush = painter.brush()
        polygon = QPolygonF()
        for p in points:
            polygon.append(p)
        painter.setPen(limits_pen)
        painter.setBrush(limits_pen.color())
        painter.drawPolygon(polygon, Qt.OddEvenFill)
        painter.setBrush(old_brush)
        painter.setPen(old_pen)

    def _drawCurveLimitLines(self, painter: QPainter, points_hi: list, points_lo: list):
        old_pen = painter.pen()
        painter.setPen(limits_pen)
        Graph.drawLines(painter, points_hi)
        Graph.drawLines(painter, points_lo)
        painter.setPen(old_pen)

    def _calculateMargins(self):
        keys = self._charts.keys()
        if 'lift' in keys and 'power' in keys and 'eff' in keys:
            self._prepareDivs('x0', self._charts['lift'].getAxis('x'))
            self._prepareDivs('y0', self._charts['lift'].getAxis('y'))
            self._prepareDivs('y1', self._charts['power'].getAxis('y'))
            self._prepareDivs('y2', self._charts['eff'].getAxis('y'))

            self._margins[0] = self._grid_divs['y0'].width + 20
            self._margins[1] = 20
            self._margins[2] = self._grid_divs['y1'].width + 20 + self._grid_divs['y2'].width + 10
            self._margins[3] = self._grid_divs['x0'].height + 20
        pass

    def _calculateLimits(self):
        chart: Chart = self._charts[self._base_chart]
        for i in range(3):
            self._limits_pixel[i] = chart.translateCoordinate(
                'x', self._limits_value[i], self.getDrawArea().width())

    def _setCanvasTransform(self, painter: QPainter, transform: QTransform):
        self._resetTransform(transform)
        transform.scale(1, -1)
        transform.translate(
            self._margins[0],
            -self.getDrawArea().height() - self._margins[1]
        )
        painter.setTransform(transform)

    def _resetTransform(self, transform: QTransform):
        transform.setMatrix(1, 0, 0,
                            0, 1, 0,
                            0, 0, 1)

    def _preparingChartsData(self):
        if is_logged: Journal.log(__name__, "\tpreparing charts datas ->")
        for chart in self._charts.values():
            self._prepareChartData(chart)

    def _prepareChartData(self, chart: Chart):
        if is_logged: Journal.log(__name__, "\t-> preparing chart data for", chart.getName())
        knots = self._getChartKnots(chart)
        curve = self._getChartCurve(chart, knots)
        limits = self._getChartLimits(chart, curve)
        self._charts_data.update({chart: {'knots': knots, 'curve': curve, 'limits': limits}})

    def _getChartKnots(self, chart: Chart):
        if is_logged: Journal.log(__name__, "\t-> getting knots for", chart.getName())
        result = []
        if len(chart.getPoints()) > 1:
            result = chart.getTranslatedPoints(
                self.getDrawArea().width(),
                self.getDrawArea().height()
            )
        return result

    def _getChartCurve(self, chart: Chart, knots: list):
        if is_logged: Journal.log(__name__, "\t-> getting curve for", chart.getName())
        result = Graph.getBSpline(knots) if len(knots) > 2 else knots
        return result

    def _getChartLimits(self, chart: Chart, curve: list):
        if 'limit' in chart.getOptions():
            if is_logged: Journal.log(__name__, "\t-> getting limits for", chart.getName())
            coords_x, coords_y = self._calculateLimitPoints(curve)
            coords_y_hi = list(map(lambda x: x * chart.getCoefs()[0], coords_y))
            coords_y_lo = list(map(lambda x: x * chart.getCoefs()[1], coords_y))
            result_hi = Graph.packCoordsToPoints(coords_x, coords_y_hi)
            result_lo = Graph.packCoordsToPoints(coords_x, coords_y_lo)
            if is_limits_polygon:
                result_lo.reverse()
            return [result_hi, result_lo]
        else:
            return []

    def _calculateLimitPoints(self, points: list):
        result_x, result_y = Graph.unpackPointsToCoords(points)
        result_x, first = aesma_funcs.remove_lesser(result_x, self._limits_pixel[0])
        result_x, last = aesma_funcs.remove_greater(result_x, self._limits_pixel[2])
        if first >= 0:
            del result_y[:first]
        if last >= 0:
            del result_y[last:]
        return result_x, result_y

    def _prepareDivs(self, name: str, axis: Axis):
        grid_divs = Divisions(name, self._grid_font)
        grid_divs.prepare(axis)
        self._grid_divs.update({name: grid_divs})


class Divisions:
    def __init__(self, name: str, font: QFont):
        self.name = name
        self.font = font
        self.divs: list = []
        self.width: int = -1
        self.height: int = -1
        self.is_ready: bool = False

    def prepare(self, axis: Axis):
        if is_logged: Journal.log(__name__, "\tpreparing grid divisions", self.name)
        fm = QFontMetricsF(self.font)
        self.divs.clear()
        for i, div in axis.generateDivSteps():
            div = round(div, 7)
            self.divs.append(div)
            self.__updateWidth(str(div), fm)
        self.height = fm.height()
        self.is_ready = True

    def __updateWidth(self, text: str, fm: QFontMetricsF):
        rect = fm.boundingRect(text)
        size = fm.size(Qt.TextSingleLine, text)
        width = size.width()
        if width > self.width:
            self.width = round(width) + 0
