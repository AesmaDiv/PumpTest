import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QColor, QBrush
from PyQt5.QtGui import QFont, QFontMetricsF, QTransform, QResizeEvent
from PyQt5.QtCore import QPointF, Qt, QRectF, QSizeF, QSize, QEvent

from AesmaLib.GraphWidget.Axis import Axis
from AesmaLib.GraphWidget.Chart import Chart
from AesmaLib.GraphWidget import SplineFuncs
from AesmaLib.journal import Journal

is_logged = True
is_updated = False


class Graph(QWidget):
    def __init__(self, width=400, height=300, parent=None):
        QWidget.__init__(self, parent)
        self.setGeometry(0, 0, width, height)
        self._margins = [20, 20, 40, 50]
        self.set_margins(self._margins)

        self._background = QBrush(QColor(30, 30, 30))  # temp 0,0,0
        self._grid_background = QBrush(QColor(50, 50, 50))  # 50,50,50
        self._grid_pen = QPen(QColor(100, 100, 100), 1)  # 255,255,255
        self._grid_border_pen = QPen(QColor(255, 255, 255), 2)  # 255,255,255
        self._grid_font = QFont("times", 10)

        # self._def_axises: dict = {}
        self._charts: dict = {}     # кривые
        self._base_chart = 'none'   # кривая определяющая размерность осей
        self._divs_x = 1            # кол-во делений оси X
        self._divs_y = 1            # кол-во делений оси Y

    def set_margins(self, margins: list):
        """ установка списка отступов """
        if len(margins) == 4:
            self._margins = margins
        else:
            if is_logged:
                Journal.log(__name__, '\tError:: margins len incorrect')

    def get_margins(self):
        """ получение ссылки на список отступов """
        return self._margins

    def get_draw_area(self):
        """ получение размеров области отрисовки графиков """
        return QRectF(self._margins[0], self._margins[1],
                      self.width() - self._margins[0] - self._margins[2],
                      self.height() - self._margins[1] - self._margins[3])

    def add_chart(self, chart: Chart, name: str):
        """ добавление кривой по имени """
        if is_logged: Journal.log(__name__, "\tadding chart", name)
        self._charts.update({name: chart})
        self._update_base_chart(chart, name)

    def remove_chart(self, name: str):
        """ удаление кривой по имени """
        if name in self._charts.keys():
            if is_logged: Journal.log(__name__, "\tremoving chart", name)
            del self._charts[name]
            if self._base_chart == name:
                self._update_base_chart(None, 'none')

    def replace_chart(self, chart: Chart, name: str):
        """ замена кривой по имени """
        if name in self._charts.keys():
            if is_logged: Journal.log(__name__, "\treplacing chart", name)
            self._charts.update({name: chart})
            if self._base_chart == name:
                self._update_base_chart(chart, name)

    def clear_charts(self):
        """ удаление всех кривых """
        if is_logged: Journal.log(__name__, "\tclearing charts")
        self._charts.clear()
        self._update_base_chart(None, 'none')

    def paintEvent(self, event):
        """ событие перерисовки компонента """
        if is_logged: Journal.log(__name__, "\tpaintEvent -> begin *************")
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHints(QPainter.Antialiasing, True)
        self._draw_grid(painter)
        self._draw_charts(painter)
        self._draw_border(painter)
        painter.end()
        if is_logged: Journal.log(__name__, "\tpaintEvent -> end *************")

    def _draw_grid(self, painter: QPainter):
        """ отрисовка сетки графика """
        if len(self._charts):
            if is_logged: Journal.log(__name__, "\tdrawGrid ->")
            step_x = self.get_draw_area().width() / self._divs_x
            step_y = self.get_draw_area().height() / self._divs_y

            pen = painter.pen()
            painter.setPen(self._grid_pen)
            self._draw_grid_background(painter)
            self._draw_grid_lines_x(painter, step_x)
            self._draw_grid_lines_y(painter, step_y)
            self._draw_grid_divs_y(painter, step_y)
            self._draw_grid_divs_x(painter, step_x)
            painter.setPen(pen)

    def _draw_grid_background(self, painter: QPainter):
        """ отрисовка подложки сетки графика """
        if is_logged: Journal.log(__name__, "\tdrawing grid background")
        x, y = self._margins[0], self._margins[1]
        painter.fillRect(QRectF(QPointF(0, 0),
                                QSizeF(self.width(),
                                       self.height())),
                         self._background)
        painter.fillRect(QRectF(QPointF(x, y),
                                QSizeF(self.get_draw_area().width(),
                                       self.get_draw_area().height())),
                         self._grid_background)

    def _draw_grid_lines_x(self, painter: QPainter, step):
        """ отрисовка линий сетки для оси X """
        if is_logged: Journal.log(__name__, "\tdrawing grid lines X")
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

    def _draw_grid_lines_y(self, painter: QPainter, step: float):
        """ отрисовка линий сетки для оси Y """
        if is_logged: Journal.log(__name__, "\tdrawing grid lines Y")
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

    def _draw_grid_divs_x(self, painter: QPainter, step: float):
        """ отрисовка значений делений на оси X """
        if len(self._charts) > 0:
            if is_logged: Journal.log(__name__, "\tdrawing grid divisions X")
            axis: Axis = self._charts[self._base_chart].getAxis('x')
            fm = QFontMetricsF(self._grid_font)
            for i, div in axis.generateDivSteps():
                text = str(round(div, 8))
                offset_x = self._margins[0] - fm.boundingRect(text).width() / 2.0
                offset_y = self.height() - self._margins[3] + fm.height() + 5
                painter.drawText(QPointF(offset_x + i * step,
                                         offset_y),
                                 text)

    def _draw_grid_divs_y(self, painter: QPainter, step: float):
        """ отрисовка значений делений на оси Y """
        if len(self._charts) > 0:
            if is_logged: Journal.log(__name__, "\tdrawing grid divisions Y")
            axis: Axis = self._charts[self._base_chart].getAxis('y')
            fm = QFontMetricsF(self._grid_font)
            for i, div in axis.generateDivSteps():
                text = str(round(div, 8))
                offset_x = self._margins[0] - fm.width(text) - 10
                offset_y = self.height() - self._margins[3] + fm.height() / 4.0
                painter.drawText(QPointF(offset_x,
                                         offset_y - i * step),
                                 text)

    def _draw_border(self, painter: QPainter):
        """ отрисовка границы области графика """
        if is_logged: Journal.log(__name__, "\tdrawing border")
        pen = painter.pen()
        painter.setPen(self._grid_border_pen)
        painter.drawRect(0, 0,
                         self.get_draw_area().width(),
                         self.get_draw_area().height())
        painter.setPen(pen)

    def _draw_charts(self, painter: QPainter):
        """ отрисовка всех кривых """
        if is_logged: Journal.log(__name__, "\tdrawCharts ->")
        transform: QTransform = QTransform()
        transform.setMatrix(1, 0, 0,
                            0, 1, 0,
                            0, 0, 1)
        transform.scale(1, -1)
        transform.translate(
            self._margins[0],
            -self.get_draw_area().height() - self._margins[1]
        )
        painter.setTransform(transform)
        for chart in self._charts.values():
            self._draw_chart(painter, chart, flag='a')
        transform.setMatrix(1, 0, 0,
                            0, 1, 0,
                            0, 0, 1)

    def _draw_chart(self, painter: QPainter, chart: Chart, flag=''):
        """ отрисовка кривой """
        if is_logged: Journal.log(__name__, "\tdrawing chart", chart.getName())
        if len(chart.getPoints()) > 1:
            points = chart.getTranslatedPoints(
                self.get_draw_area().width(),
                self.get_draw_area().height()
            )
            points = chart.apply_spline(points)
            Graph.draw_curve(painter, points, chart.getPen())
        else:
            Journal.log(__name__, "\tchart", chart.getName(), "is empty")

    def _update_base_chart(self, chart: Chart, name: str):
        """ обновление информации об основной кривой """
        if self._base_chart == 'none' or name == 'none':
            if is_logged: Journal.log(__name__, "\tupdating base chart to", name)
            self._base_chart = name
            self._divs_x = chart.getAxis('x').getDivs() if chart else 1
            self._divs_y = chart.getAxis('y').getDivs() if chart else 1

    @staticmethod
    def draw_lines(painter: QPainter, points: list):
        """ отрисовка линий по точкам """
        if points is not None and points.any():
            path: QPainterPath = QPainterPath()
            path.moveTo(points[0][0], points[1][0])
            for i in range(1, len(points[0])):
                path.lineTo(points[0][i], points[1][i])
            painter.drawPath(path)

    @staticmethod
    def draw_curve(painter: QPainter, points: list, pen: QPen):
        """ отрисовка кривой по точкам """
        painter.setPen(pen)
        Graph.draw_lines(painter, points)

    @staticmethod
    def draw_bezier(painter: QPainter, points: list):
        """ отрисовка кривой Безье по точкам """
        steps = 500
        control_points = [[p.x(), p.y()] for p in points]
        old_point = control_points[0]
        for point in SplineFuncs.bezierCurveRange(steps, control_points):
            painter.drawLine(old_point[0], old_point[1], point[0], point[1])
            old_point = point

    @staticmethod
    def get_spline(points: list):
        """ создание кривой по точкам """
        coords_x, coords_y = Graph.unpack_to_coords(points)
        coords_x, coords_y = SplineFuncs.getCurvePoints(coords_x, coords_y)
        result = Graph.pack_to_points(coords_x, coords_y)
        return result

    @staticmethod
    def get_bspline(points: list):
        """ создание кубической кривой по точкам """
        coords_x, coords_y = Graph.unpack_to_coords(points)
        coords_x, coords_y = SplineFuncs.getBSplinePoints(coords_x, coords_y)
        result = Graph.pack_to_points(coords_x, coords_y)
        return result
    
    @staticmethod
    def unpack_to_coords(points: list):
        """ распаковка списка точек в списки координат """
        return points[0], points[1]
    
    @staticmethod
    def pack_to_points(coords_x: list, coords_y: list):
        """ запаковка списков координат в список точек """
        return [coords_x, coords_y]
