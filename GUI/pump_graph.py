"""
    Модуль содержит классы компонента графика
    характеристик ЭЦН
"""
import math, numpy as np
from scipy.interpolate import make_interp_spline
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QFont, QFontMetricsF
from PyQt5.QtGui import QShowEvent, QTransform, QPixmap, QPolygonF, QPainterPath
from PyQt5.QtCore import QPointF, Qt, QSize
from AesmaLib.GraphWidget.Graph import Graph, Chart, Axis
from AesmaLib import aesma_funcs
from AesmaLib.journal import Journal


is_logged = True
limits_pen = QPen(QColor(200, 200, 0, 40), 1, Qt.SolidLine)


class PumpGraph(Graph):
    """ класс компонента графика характеристик ЭЦН """
    def __init__(self, width: int, height: int, PATH_TO_PIC: str = None, parent=None):
        Graph.__init__(self, width, height, parent)
        self.setGeometry(0, 0, width, height)
        self._limits_value = [0, 0, 0]
        self._range_pixels = [0, 0, 0]
        self._grid_divs: dict = {}
        self._charts_data = {}

    def render_to_image(self, size: QSize, path_to_file=None):
        """ отрисовка содержимого компонента в рисунок и в файл """
        self.setGeometry(0, 0, size.width(), size.height())
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        if path_to_file:
            pixmap.save(path_to_file)
        return pixmap

    def set_limits(self, minimum: float, nominal: float, maximum: float):
        """ установка области рабочего диапазона """
        self._limits_value = [minimum, nominal, maximum]

    def add_chart(self, chart: Chart, name: str):
        """ добавление графика """
        Graph.add_chart(self, chart, name)

    def get_chart(self, name: str):
        """ получение графика по имени """
        if name in self._charts:
            return self._charts[name]
        return None

    def paintEvent(self, event):
        super(PumpGraph, self).paintEvent(event)

    def set_visibile_charts(self, names_of_charts_to_show: list = 'all'):
        for chart in self._charts.values():
            chart.setVisibility(names_of_charts_to_show == 'all'
                                or chart.name
                                in names_of_charts_to_show)

    def clear_charts(self):
        """ удаление всех кривых """
        Graph.clear_charts(self)
        self._charts_data.clear()
        # self.set_margins([10, 10, 10, 10])

    def _draw_grid(self, painter: QPainter):
        """ отрисовка сетки графика """
        if len(self._charts):
            if is_logged: Journal.log(__name__, "\tотрисовка сетки ->")
            self._calculate_margins()

            step_x = self.get_draw_area().width() / self._divs_x
            step_y = self.get_draw_area().height() / self._divs_y

            pen = painter.pen()
            painter.setPen(self._grid_pen)
            self._draw_grid_background(painter)
            self._draw_grid_ranges(painter)
            self._draw_grid_lines(painter, 'x0', step_x)
            self._draw_grid_lines(painter, 'y0', step_y)
            self._draw_grid_divs_x(painter, step_x)
            self._draw_grid_divs_y(painter, step_y, 'y0')
            self._draw_grid_divs_y(painter, step_y, 'y1')
            self._draw_grid_divs_y(painter, step_y, 'y2')
            self._draw_labels(painter)
            painter.setPen(pen)

    def _draw_grid_ranges(self, painter: QPainter):
        """ отрисовка области рабочего диапазона """
        if is_logged: Journal.log(__name__, "\tотрисовка области раб.диапазона")
        self._calculate_limits()
        """ расчёт рабочего диапазона """
        x0 = self._margins[0] + self._range_pixels[0]
        x1 = self._margins[0] + self._range_pixels[1]
        x2 = self._margins[0] + self._range_pixels[2]
        y0 = self._margins[1]
        y1 = self.get_draw_area().height() + y0
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

    def _draw_grid_lines(self, painter: QPainter, name, step):
        """ отрисовка линий сетки для оси """
        if self._grid_divs[name].is_ready:
            if is_logged:
                Journal.log(__name__, f"\tотрисовка линий сетки оси {name}")
            divs = self._grid_divs[name].divs
            for i in range(1, len(divs)):
                self._grid_pen.setStyle(Qt.SolidLine if divs[i] == 0
                    else Qt.DotLine)
                if name == 'x0':
                    coord = i * step + self._margins[0]
                    p0 = QPointF(coord, self._margins[1])
                    p1 = QPointF(coord, self.height() - self._margins[3]) 
                else:
                    coord = (len(divs) - i) * step + self._margins[1]
                    p0 = QPointF(self._margins[0], coord)
                    p1 = QPointF(self.width() - self._margins[2], coord)
                painter.setPen(self._grid_pen)
                painter.drawLine(p0, p1)
        else:
            if is_logged:
                Journal.log(__name__, f"\tError -> деления оси {name} не готовы")

    def _draw_grid_divs_x(self, painter: QPainter, step: float):
        """ отрисовка значений делений на оси X """
        if self._grid_divs['x0'].is_ready:
            if is_logged:
                Journal.log(__name__, "\tотрисовка делений оси X")
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

    def _draw_grid_divs_y(self, painter: QPainter, step: float, axis_name='y0'):
        """ отрисовка значений делений на оси Y """
        if is_logged:
            Journal.log(__name__, "\tотрисовка делений оси", axis_name)
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
                offset_x = self._margins[0] + self.get_draw_area().width() + 10
                painter.setPen(self._charts['pwr'].getPen())
            elif axis_name == 'y2':
                offset_x = self._margins[0] + self.get_draw_area().width() + \
                           self._grid_divs['y1'].width + 40
                painter.setPen(self._charts['eff'].getPen())
            offset_y = self.height() - self._margins[3] + fm.height() / 4.0
            painter.drawText(QPointF(offset_x, offset_y - i * step), text)
        painter.setPen(pen)
    
    def _draw_labels(self, painter: QPainter):
        """ отображение подписей на осях """
        fm = QFontMetricsF(self._grid_font)
        pen = painter.pen()

        text = 'Расход, м³/сутки'
        offset_x = self._margins[0] + self.get_draw_area().width() / 2
        offset_x -= fm.width(text) / 2
        offset_y = self.height() - self._margins[3] + fm.height()
        offset_y += 20
        painter.setPen(self._grid_border_pen)
        painter.drawText(QPointF(offset_x, offset_y), text)

        text = 'Напор, м'
        offset_x = 0 - fm.height() - 5
        self._draw_label(painter, fm, offset_x, text)

        text = 'Мощность, кВт'
        offset_x = self._margins[0] + self.get_draw_area().width() + 10
        painter.setPen(self._charts['pwr'].getPen())
        self._draw_label(painter, fm, offset_x, text)
        
        text = 'КПД, %'
        offset_x = self._margins[0] + self.get_draw_area().width() + \
                   self._grid_divs['y1'].width + 40
        painter.setPen(self._charts['eff'].getPen())
        self._draw_label(painter, fm, offset_x, text)
        painter.setPen(pen)
            
    def _draw_label(self, painter: QPainter, fm, offset_x, text):
        """ отображение подписи оси """
        painter.rotate(-90)
        offset_y = -self._margins[1] - self.get_draw_area().height() / 2
        offset_y -= fm.width(text) / 2
        painter.drawText(QPointF(offset_y, offset_x + 45), text)
        painter.rotate(90)

    def _draw_charts(self, painter: QPainter):
        """ отрисовка всех графиков """
        if is_logged: Journal.log(__name__, "\tотрисовка графиков ->")
        transform: QTransform = QTransform()
        self._preparing_charts_data()
        self._set_canvas_transform(painter, transform)
        self._draw_charts_limits(painter)
        self._draw_charts_knots_n_curves(painter)
        self._reset_transform(transform)

    def _draw_charts_limits(self, painter: QPainter):
        """ отрисовка пределов допуска для всех кривых """
        for chart, data in self._charts_data.items():
            if data['limits'].size:
                self._draw_limit_polygon(painter, chart, data['limits'])

    def _draw_charts_knots_n_curves(self, painter: QPainter):
        """ отрисовка узлов и кривых """
        if is_logged:
            Journal.log(__name__, "\tотрисовка узлов и кривых ->")
        for chart, data in self._charts_data.items():
            if data['knots'].size and chart.visibility:
                pen = painter.pen()
                brush = painter.brush()
                painter.setPen(chart.getPen())
                painter.setBrush(chart.getPen().color())
                if "knots" in chart.getOptions():
                    if is_logged:
                        Journal.log(__name__, "\t-> отрисовка узлов для",
                                    chart.name)
                    PumpGraph._draw_knots(painter, data['knots'])
                painter.setBrush(brush)
                if is_logged:
                    Journal.log(__name__, "\t-> отрисовка кривой для",
                                chart.name)
                PumpGraph._draw_curve(painter, data['curve'])
                painter.setPen(pen)

    @staticmethod
    def _draw_curve(painter: QPainter, points):
        """ отрисовка линий по точкам """
        if points.size:
            path = QPainterPath()
            path.moveTo(QPointF(points[0][0], points[0][1]))
            for i in range(1, len(points['x'])):
                path.lineTo(QPointF(points[i][0], points[i][1]))
            painter.drawPath(path)

    @staticmethod
    def _draw_knots(painter: QPainter, points):
        """ отрисовка узлов """
        if len(points['x']):
            for p in points:
                painter.drawEllipse(QPointF(p[0], p[1]), 2, 2)

    @staticmethod
    def _draw_limit_polygon(painter: QPainter, chart, points):
        """ отрисовка полигона для области допуска """
        if is_logged:
            Journal.log(__name__, "\tотрисовка пределов допуска для",
                        chart.name)
        if points.size:
            old_pen = painter.pen()
            old_brush = painter.brush()
            polygon = QPolygonF()
            for p in points:
                polygon.append(QPointF(p[0], p[1]))
            painter.setPen(limits_pen)
            painter.setBrush(limits_pen.color())
            painter.drawPolygon(polygon, Qt.OddEvenFill)
            painter.setBrush(old_brush)
            painter.setPen(old_pen)

    def _calculate_margins(self):
        """ расчёт отступов """
        keys = self._charts.keys()
        if 'lft' in keys and 'pwr' in keys and 'eff' in keys:
            self._prepare_divs('x0', self._charts['lft'].getAxis('x'))
            self._prepare_divs('y0', self._charts['lft'].getAxis('y'))
            self._prepare_divs('y1', self._charts['pwr'].getAxis('y'))
            self._prepare_divs('y2', self._charts['eff'].getAxis('y'))

            self._margins[0] = self._grid_divs['y0'].width + 50
            self._margins[1] = 20
            self._margins[2] = self._grid_divs['y1'].width + 40 + \
                               self._grid_divs['y2'].width + 40
            self._margins[3] = self._grid_divs['x0'].height + 30
        pass

    def _calculate_limits(self):
        """ расчёт рабочего диапазона """
        chart: Chart = self._charts[self._base_chart]
        for i in range(3):
            self._range_pixels[i] = chart.translateCoordinate(
                'x', self._limits_value[i], self.get_draw_area().width())

    def _set_canvas_transform(self, painter: QPainter, transform: QTransform):
        """ трансформация холста """
        self._reset_transform(transform)
        transform.scale(1, -1)
        transform.translate(
            self._margins[0],
            -self.get_draw_area().height() - self._margins[1]
        )
        painter.setTransform(transform)

    def _reset_transform(self, transform: QTransform):
        """ сброс трансформации холста """
        transform.setMatrix(1, 0, 0,
                            0, 1, 0,
                            0, 0, 1)

    def _preparing_charts_data(self):
        """ подготовка данных для формирования графика """
        if is_logged: Journal.log(__name__, "\tподготовка данных для кривых ->")
        for chart in self._charts.values():
            self._prepare_chart_data(chart)

    def _prepare_chart_data(self, chart: Chart):
        """ подготовка данных для построения кривой """
        if is_logged:
            Journal.log(__name__, "\t-> подготовка данных для кривой",
                        chart.name)
        draw_area = self.get_draw_area()
        knots = self._get_chart_knots(chart, draw_area)
        curve = self._get_chart_curve(chart, draw_area)
        limit = self._get_chart_limit(chart, curve)
        self._charts_data.update({
            chart: {'knots': knots, 'curve': curve, 'limits': limit}})

    def _get_chart_knots(self, chart: Chart, draw_area):
        """ получение координат узлов кривой """
        if is_logged:
            Journal.log(__name__, "\t-> получение узлов для",
                        chart.name)
        result = chart.createEmptyPoints()
        if len(chart.getPoints('x')) > 1:
            sz_cnv = [draw_area.width(), draw_area.height()]
            result = chart.getTranslatedPoints(sz_cnv)
        return result

    def _get_chart_curve(self, chart: Chart, draw_area):
        """ получение координат точек кривой """
        if is_logged:
            Journal.log(__name__, "\t-> получение кривой для", chart.name)
        result = chart.createEmptyPoints()
        if len(chart.getPoints('x')) > 1:
            sz_cnv = [draw_area.width(), draw_area.height()]
            result = chart.getTranslatedPoints(sz_cnv, for_curve=True)
        return result
    

    def _get_chart_limit(self, chart: Chart, curve):
        """ получение координат точек описывающих пределы допуска """
        result = chart.createEmptyPoints()
        if 'limit' in chart.getOptions() and curve['x'].any():
            if is_logged:
                Journal.log(__name__, "\t-> получение пределов допуска для",
                            chart.name)
            ranges = self._range_pixels
            coeffs = chart.getCoefs()
            result = self._slice_curve_to_range(curve, ranges)
            result = self._calculate_limit_coords(chart, result, coeffs)
        return result
    
    @staticmethod
    def _slice_curve_to_range(curve, ranges):
        first, last = ranges[0], ranges[2]
        mask = curve['x'] >= first
        mask &= curve['x'] <= last
        result = curve[mask]
        return result
    
    @staticmethod
    def _calculate_limit_coords(chart, curve, coeffs):
        """ расчёт точек кривой оприсывающей пределы допуска """
        xs_hi = curve['x'].tolist()
        xs_lo = xs_hi[::-1]
        ys_hi = list(map(lambda x: x * coeffs[0], curve['y']))
        ys_lo = list(map(lambda x: x * coeffs[1], curve['y'][::-1]))
        result_x = xs_hi + xs_lo
        result_y = ys_hi + ys_lo
        result = chart.transposePoints([result_x, result_y])
        return result

    def _prepare_divs(self, name: str, axis: Axis):
        """ подготовка значений делений на оси """
        grid_divs = Divisions(name, self._grid_font)
        grid_divs.prepare(axis)
        self._grid_divs.update({name: grid_divs})


class Divisions:
    """ Класс для делений осей графика """
    def __init__(self, name: str, font: QFont):
        self.name = name
        self.font = font
        self.divs: list = []
        self.width: int = -1
        self.height: int = -1
        self.is_ready: bool = False

    def prepare(self, axis: Axis):
        if is_logged:
            Journal.log(__name__, "\tподготовка делений для", self.name)
        fm = QFontMetricsF(self.font)
        self.divs.clear()
        for i, div in axis.generateDivSteps():
            div = round(div, 7)
            self.divs.append(div)
            self._update_width(str(div), fm)
        self.height = fm.height()
        self.is_ready = True

    def _update_width(self, text: str, fm: QFontMetricsF):
        rect = fm.boundingRect(text)
        size = fm.size(Qt.TextSingleLine, text)
        width = size.width()
        if width > self.width:
            self.width = round(width) + 0
