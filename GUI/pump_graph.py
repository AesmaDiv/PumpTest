"""
    Модуль содержит классы компонента графика
    характеристик ЭЦН
"""
from PyQt5.QtGui import QPainter, QColor, QBrush, QFont, QPolygonF, QPen, QTransform, QPixmap
from PyQt5.QtGui import QFontMetricsF, QShowEvent
from PyQt5.QtCore import QPointF, Qt, QSize
from AesmaLib.GraphWidget.Graph import Graph, Chart, Axis
from AesmaLib import aesma_funcs
from AesmaLib.journal import Journal


is_logged = True
with_limits = True
limits_pen = QPen(QColor(200, 200, 0, 20), 1, Qt.SolidLine)


class PumpGraph(Graph):
    """ класс компонента графика характеристик ЭЦН """
    def __init__(self, width: int, height: int, PATH_TO_PIC: str = None, parent=None):
        Graph.__init__(self, width, height, parent)
        self.setGeometry(0, 0, width, height)
        self._limits_value = [0, 0, 0]
        self._limits_pixel = [0, 0, 0]
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
                                or chart.getName()
                                in names_of_charts_to_show)

    def clear_charts(self):
        """ удаление всех кривых """
        Graph.clear_charts(self)
        self.clear_charts_data()
        # self.set_margins([10, 10, 10, 10])

    def clear_charts_data(self):
        if is_logged: Journal.log(__name__, "\tclearing charts data")
        self._charts_data.clear()

    def _draw_grid(self, painter: QPainter):
        """ отрисовка сетки графика """
        if len(self._charts):
            if is_logged: Journal.log(__name__, "\tdrawGrid ->")
            self._calculate_margins()

            step_x = self.get_draw_area().width() / self._divs_x
            step_y = self.get_draw_area().height() / self._divs_y

            pen = painter.pen()
            painter.setPen(self._grid_pen)
            self._draw_grid_background(painter)
            self._draw_grid_ranges(painter)
            self._draw_grid_lines_x(painter, step_x)
            self._draw_grid_lines_y(painter, step_y)
            self._draw_grid_divs_x(painter, step_x)
            self._draw_grid_divs_y(painter, step_y, 'y0')
            self._draw_grid_divs_y(painter, step_y, 'y1')
            self._draw_grid_divs_y(painter, step_y, 'y2')
            self._draw_labels(painter)
            painter.setPen(pen)

    def _draw_grid_ranges(self, painter: QPainter):
        """ отрисовка области рабочего диапазона """
        if is_logged: Journal.log(__name__, "\tdrawing grid ranges")
        self._calculate_limits()
        """ расчёт рабочего диапазона """
        x0 = self._margins[0] + self._limits_pixel[0]
        x1 = self._margins[0] + self._limits_pixel[1]
        x2 = self._margins[0] + self._limits_pixel[2]
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

    def _draw_grid_lines_x(self, painter: QPainter, step):
        """ отрисовка линий сетки для оси X """
        if self._grid_divs['x0'].is_ready:
            if is_logged:
                Journal.log(__name__, "\tdrawing grid lines X")
            divs = self._grid_divs['x0'].divs
            for i in range(len(divs)):
                self._grid_pen.setStyle(Qt.SolidLine if divs[i] == 0
                    else Qt.DotLine)
                coord = i * step + self._margins[0]
                painter.setPen(self._grid_pen)
                painter.drawLine(QPointF(coord,
                                         self._margins[1]),
                                 QPointF(coord,
                                         self.height() - self._margins[3]))
        else:
            if is_logged:
                Journal.log(__name__, "\tError -> grid divs X not ready")

    def _draw_grid_lines_y(self, painter: QPainter, step: float):
        """ отрисовка линий сетки для оси Y """
        if self._grid_divs['y0'].is_ready:
            if is_logged:
                Journal.log(__name__, "\tdrawing grid lines Y")
            divs = self._grid_divs['y0'].divs
            for i in range(1, len(divs)):
                self._grid_pen.setStyle(Qt.SolidLine if divs[i] == 0
                    else Qt.DotLine)
                coord = (len(divs) - i) * step + self._margins[1]
                painter.setPen(self._grid_pen)
                painter.drawLine(QPointF(self._margins[0],
                                         coord),
                                 QPointF(self.width() - self._margins[2],
                                         coord))
        else:
            if is_logged:
                Journal.log(__name__, "\tError -> grid divs Y not ready")

    def _draw_grid_divs_x(self, painter: QPainter, step: float):
        """ отрисовка значений делений на оси X """
        if self._grid_divs['x0'].is_ready:
            if is_logged:
                Journal.log(__name__, "\tdrawing grid divisions X")
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

    def _draw_grid_divs_y(self, painter: QPainter, step: float, axis_name='x'):
        """ отрисовка значений делений на оси Y """
        if is_logged:
            Journal.log(__name__, "\tdrawing grid divisions Y", axis_name)
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
        """ отрисовка всех кривых """
        if is_logged: Journal.log(__name__, "\tdrawCharts ->")
        transform: QTransform = QTransform()
        self._preparing_charts_data()
        self._set_canvas_transform(painter, transform)
        self._draw_charts_limits(painter)
        self._draw_charts_knots_n_curves(painter)
        self._reset_transform(transform)

    def _draw_charts_limits(self, painter: QPainter):
        """ отрисовка пределов допуска для всех кривых """
        for chart, data in self._charts_data.items():
            if data['limits']:
                self._draw_limits(painter, data['limits'], chart)

    def _draw_charts_knots_n_curves(self, painter: QPainter):
        """ отрисовка узлов и кривых """
        if is_logged:
            Journal.log(__name__, "\tdrawing charts curves and knots")
        for chart, data in self._charts_data.items():
            if len(data['knots']) > 1:
                if chart.getVisibility():
                    pen = painter.pen()
                    brush = painter.brush()
                    painter.setPen(chart.getPen())
                    painter.setBrush(chart.getPen().color())
                    if "knots" in chart.getOptions():
                        if is_logged:
                            Journal.log(__name__, "\tdrawing knots for",
                                        chart.getName())
                        self._draw_knots(painter, data['knots'])
                    painter.setBrush(brush)
                    if is_logged:
                        Journal.log(__name__, "\tdrawing curve for",
                                    chart.getName())
                    Graph.draw_curve(painter, data['curve'], chart.getPen())
                    painter.setPen(pen)

    def _draw_limits(self, painter: QPainter, limits: list, chart: Chart):
        """ отрисовка пределов допуска """
        if is_logged:
            Journal.log(__name__, "\tdrawing limits for", chart.getName())
        points_hi, points_lo = limits
        if with_limits:
            self._draw_limit_polygon(painter, points_hi + points_lo)
        else:
            self._draw_limit_lines(painter, points_hi, points_lo)

    def _draw_knots(self, painter: QPainter, points: list):
        """ отрисовка узлов """
        for point in points:
            painter.drawEllipse(point, 2, 2)

    def _draw_limit_polygon(self, painter: QPainter, points: list):
        """ отрисовка полигона для области допуска """
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

    def _draw_limit_lines(self, painter: QPainter, points_hi: list, points_lo: list):
        """ отрисовка линий для области допуска """
        old_pen = painter.pen()
        painter.setPen(limits_pen)
        Graph.draw_lines(painter, points_hi)
        Graph.draw_lines(painter, points_lo)
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
            self._limits_pixel[i] = chart.translateCoordinate(
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
        if is_logged: Journal.log(__name__, "\tpreparing charts datas ->")
        for chart in self._charts.values():
            self._prepare_chart_data(chart)

    def _prepare_chart_data(self, chart: Chart):
        """ подготовка данных для построения кривой """
        if is_logged:
            Journal.log(__name__, "\t-> preparing chart data for",
                        chart.getName())
        knots = self._get_chart_knots(chart)
        curve = self._get_chart_curve(chart, knots)
        limits = self._get_chart_limits(chart, curve)
        self._charts_data.update(
            {chart: {'knots': knots, 'curve': curve, 'limits': limits}})

    def _get_chart_knots(self, chart: Chart):
        """ получение координат узлов кривой """
        if is_logged:
            Journal.log(__name__, "\t-> getting knots for",
                        chart.getName())
        result = []
        if len(chart.getPoints()) > 1:
            result = chart.getTranslatedPoints(
                self.get_draw_area().width(),
                self.get_draw_area().height()
            )
        return result

    def _get_chart_curve(self, chart: Chart, knots: list):
        """ построение кривой по точкам """
        if is_logged:
            Journal.log(__name__, "\t-> getting curve for", chart.getName())
        # result = Graph.get_cspline(chart, knots) if len(knots) > 2 else knots
        result = Graph.get_bspline(knots) if len(knots) > 2 else knots
        return result
    


    def _get_chart_limits(self, chart: Chart, curve: list):
        """ построение кривой описывающей пределы допуска """
        if 'limit' in chart.getOptions():
            if is_logged:
                Journal.log(__name__, "\t-> getting limits for", chart.getName())
            coords_x, coords_y = self._calculate_limit_points(curve)
            coords_y_hi = list(map(lambda x: x * chart.getCoefs()[0], coords_y))
            coords_y_lo = list(map(lambda x: x * chart.getCoefs()[1], coords_y))
            result_hi = Graph.pack_to_points(coords_x, coords_y_hi)
            result_lo = Graph.pack_to_points(coords_x, coords_y_lo)
            if with_limits:
                result_lo.reverse()
            return [result_hi, result_lo]
        else:
            return []

    def _calculate_limit_points(self, points: list):
        """ расчёт точек кривой оприсывающей пределы допуска """
        result_x, result_y = Graph.unpack_to_coords(points)
        first, last = self._limits_pixel[0], self._limits_pixel[2]
        indices = [i for i, x in enumerate(result_x) if first < x < last]
        first, last = indices[0] - 1, indices[-1] + 1
        result_x = result_x[first:last]
        result_y = result_y[first:last]
        return result_x, result_y

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
            Journal.log(__name__, "\tpreparing grid divisions", self.name)
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
