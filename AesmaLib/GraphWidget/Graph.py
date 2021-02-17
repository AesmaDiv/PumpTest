from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QColor, QBrush
from PyQt5.QtGui import QFont, QFontMetricsF, QTransform, QResizeEvent
from PyQt5.QtCore import QPointF, Qt, QRectF, QSizeF, QSize, QEvent

from AesmaLib.GraphWidget.Axis import Axis
from AesmaLib.GraphWidget.Chart import Chart
from AesmaLib.GraphWidget import SplineFuncs
from AesmaLib import journal

is_logged = True
is_updated = False


class Graph(QWidget):
    def __init__(self, width=400, height=300, parent=None):
        QWidget.__init__(self, parent)
        self.setGeometry(0, 0, width, height)
        self._margins = [20, 20, 40, 50]
        self.setMargins(self._margins)

        self._background = QBrush(QColor(30, 30, 30))  # temp 0,0,0
        self._grid_background = QBrush(QColor(50, 50, 50))  # 50,50,50
        self._grid_pen = QPen(QColor(100, 100, 100), 1)  # 255,255,255
        self._grid_border_pen = QPen(QColor(255, 255, 255), 2)  # 255,255,255
        self._grid_font = QFont("times", 10)

        self._def_axises: dict = {}
        self._charts: dict = {}
        self._base_chart = 'none'
        self._divs_x = 1
        self._divs_y = 1

    def setMargins(self, margins: list):
        if len(margins) == 4:
            self._margins = margins
        else:
            if is_logged: journal.log(__name__, '\tError:: margins len incorrect')

    def getMargins(self):
        return self._margins

    def getDrawArea(self):
        return QRectF(self._margins[0], self._margins[1],
                      self.width() - self._margins[0] - self._margins[2],
                      self.height() - self._margins[1] - self._margins[3])

    def addChart(self, chart: Chart, name: str):
        if is_logged: journal.log(__name__, "\tadding chart", name)
        self._charts.update({name: chart})
        self._updateBaseChart(chart, name)

    def removeChart(self, name: str):
        if name in self._charts.keys():
            if is_logged: journal.log(__name__, "\tremoving chart", name)
            del self._charts[name]
            if self._base_chart == name:
                self._updateBaseChart(None, 'none')

    def replaceChart(self, chart: Chart, name: str):
        if name in self._charts.keys():
            if is_logged: journal.log(__name__, "\treplacing chart", name)
            self._charts.update({name: chart})
            if self._base_chart == name:
                self._updateBaseChart(chart, name)

    def clearCharts(self):
        if is_logged: journal.log(__name__, "\tclearing charts")
        self._charts.clear()
        self._updateBaseChart(None, 'none')

    def paintEvent(self, event):
        if is_logged: journal.log(__name__, "\tpaintEvent -> begin *************")
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHints(QPainter.Antialiasing, True)
        self._drawGrid(painter)
        self._drawCharts(painter)
        self._drawBorder(painter)
        painter.end()
        if is_logged: journal.log(__name__, "\tpaintEvent -> end *************")

    def _drawGrid(self, painter: QPainter):
        if len(self._charts):
            if is_logged: journal.log(__name__, "\tdrawGrid ->")
            step_x = self.getDrawArea().width() / self._divs_x
            step_y = self.getDrawArea().height() / self._divs_y

            pen = painter.pen()
            painter.setPen(self._grid_pen)
            self._drawGridBackground(painter)
            self._drawGridLinesX(painter, step_x)
            self._drawGridLinesY(painter, step_y)
            self._drawGridDivsY(painter, step_y)
            self._drawGridDivsX(painter, step_x)
            painter.setPen(pen)

    def _drawGridBackground(self, painter: QPainter):
        if is_logged:
            journal.log(__name__, "\tdrawing grid background")
        x, y = self._margins[0], self._margins[1]
        painter.fillRect(QRectF(QPointF(0, 0),
                                QSizeF(self.width(),
                                       self.height())),
                         self._background)
        painter.fillRect(QRectF(QPointF(x, y),
                                QSizeF(self.getDrawArea().width(),
                                       self.getDrawArea().height())),
                         self._grid_background)

    def _drawGridLinesX(self, painter: QPainter, step):
        if is_logged: journal.log(__name__, "\tdrawing grid lines X")
        axis: Axis = self._charts[self._base_chart].getAxis('x')
        for i, div in axis.generateDivSteps():
            if i == 0 or i == self._divs_x or div == 0.0:
                self._grid_pen.setStyle(Qt.SolidLine)
            else:
                self._grid_pen.setStyle(Qt.DotLine)
            coord = i * step + self._margins[0]
            painter.setPen(self._grid_pen)
            painter.drawLine(QPointF(coord,
                                     self._margins[1]),
                             QPointF(coord,
                                     self.height() - self._margins[3]))

    def _drawGridLinesY(self, painter: QPainter, step: float):
        if is_logged: journal.log(__name__, "\tdrawing grid lines Y")
        axis: Axis = self._charts[self._base_chart].getAxis('y')
        for i, div in axis.generateDivSteps():
            if i == 0 or i == self._divs_y or div == 0.0:
                self._grid_pen.setStyle(Qt.SolidLine)
            else:
                self._grid_pen.setStyle(Qt.DotLine)
            coord = (self._divs_y - i) * step + self._margins[1]
            painter.setPen(self._grid_pen)
            painter.drawLine(QPointF(self._margins[0],
                                     coord),
                             QPointF(self.width() - self._margins[2],
                                     coord))

    def _drawGridDivsX(self, painter: QPainter, step: float):
        if len(self._charts) > 0:
            if is_logged: journal.log(__name__, "\tdrawing grid divisions X")
            axis: Axis = self._charts[self._base_chart].getAxis('x')
            fm = QFontMetricsF(self._grid_font)
            for i, div in axis.generateDivSteps():
                text = str(round(div, 8))
                offset_x = self._margins[0] - fm.boundingRect(text).width() / 2.0
                offset_y = self.height() - self._margins[3] + fm.height() + 5
                painter.drawText(QPointF(offset_x + i * step,
                                         offset_y),
                                 text)

    def _drawGridDivsY(self, painter: QPainter, step: float):
        if len(self._charts) > 0:
            if is_logged: journal.log(__name__, "\tdrawing grid divisions Y")
            axis: Axis = self._charts[self._base_chart].getAxis('y')
            fm = QFontMetricsF(self._grid_font)
            for i, div in axis.generateDivSteps():
                text = str(round(div, 8))
                offset_x = self._margins[0] - fm.width(text) - 10
                offset_y = self.height() - self._margins[3] + fm.height() / 4.0
                painter.drawText(QPointF(offset_x,
                                         offset_y - i * step),
                                 text)

    def _drawBorder(self, painter: QPainter):
        if is_logged: journal.log(__name__, "\tdrawing border")
        pen = painter.pen()
        painter.setPen(self._grid_border_pen)
        painter.drawRect(0, 0,
                         self.getDrawArea().width(),
                         self.getDrawArea().height())
        painter.setPen(pen)

    def _drawCharts(self, painter: QPainter):
        if is_logged: journal.log(__name__, "\tdrawCharts ->")
        transform: QTransform = QTransform()
        transform.setMatrix(1, 0, 0,
                            0, 1, 0,
                            0, 0, 1)
        transform.scale(1, -1)
        transform.translate(
            self._margins[0],
            -self.getDrawArea().height() - self._margins[1]
        )
        painter.setTransform(transform)
        for chart in self._charts.values():
            self._drawChart(painter, chart, flag='a')
        transform.setMatrix(1, 0, 0,
                            0, 1, 0,
                            0, 0, 1)

    def _drawChart(self, painter: QPainter, chart: Chart, flag=''):
        if is_logged: journal.log(__name__, "\tdrawing chart", chart.getName())
        if len(chart.getPoints('x')) > 1:
            points = chart.getTranslatedPoints(
                self.getDrawArea().width(),
                self.getDrawArea().height()
            )
            if flag == 'a':
                points = Graph.getBSpline(points)
            elif flag == 's':
                points = Graph.getSpline(points)
            elif flag == 'b':
                points = Graph.getSpline(points)
                Graph.drawBezier(painter, points)
                return
            Graph.drawCurve(painter, Graph.getBSpline(points), chart.getPen())
        else:
            journal.log(__name__, "\tchart", chart.getName(), "is empty")

    def _updateBaseChart(self, chart: Chart, name: str):
        if self._base_chart == 'none' or name == 'none':
            if is_logged: journal.log(__name__, "\tupdating base chart to", name)
            self._base_chart = name
            self._divs_x = chart.getAxis('x').getDivs() if chart else 1
            self._divs_y = chart.getAxis('y').getDivs() if chart else 1

    @staticmethod
    def drawLines(painter: QPainter, points: list):
        count = len(points)
        if count:
            path: QPainterPath = QPainterPath()
            path.moveTo(points[0].x(), points[0].y())
            for i in range(1, count):
                path.lineTo(points[i].x(), points[i].y())
            painter.drawPath(path)

    @staticmethod
    def drawCurve(painter: QPainter, points: list, pen: QPen):
        painter.setPen(pen)
        Graph.drawLines(painter, points)

    @staticmethod
    def drawBezier(painter: QPainter, points: list):
        steps = 500
        control_points = [[p.x(), p.y()] for p in points]
        old_point = control_points[0]
        for point in SplineFuncs.bezierCurveRange(steps, control_points):
            painter.drawLine(old_point[0], old_point[1], point[0], point[1])
            old_point = point

    @staticmethod
    def getSpline(points: list):
        coords_x, coords_y = Graph.unpackPointsToCoords(points)
        coords_x, coords_y = SplineFuncs.getCurvePoints(coords_x, coords_y)
        result = Graph.packCoordsToPoints(coords_x, coords_y)
        return result

    @staticmethod
    def getBSpline(points: list):
        coords_x, coords_y = Graph.unpackPointsToCoords(points)
        coords_x, coords_y = SplineFuncs.getBSplinePoints(coords_x, coords_y)
        result = Graph.packCoordsToPoints(coords_x, coords_y)
        return result

    @staticmethod
    def unpackPointsToCoords(points: list):
        coords = [[point.x(), point.y()] for point in points]
        coords_x, coords_y = zip(*coords)
        coords_x, coords_y = list(coords_x), list(coords_y)
        return coords_x, coords_y
    
    @staticmethod
    def packCoordsToPoints(coords_x: list, coords_y: list):
        coords = zip(coords_x, coords_y)
        points = [QPointF(x, y) for x, y in coords]
        return points
