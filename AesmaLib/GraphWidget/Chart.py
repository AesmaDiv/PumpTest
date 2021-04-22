# AesmaDiv 03.2020
# Класс для графиков: Данные графика.
# Точки и оси, функция трансляции значений по осям
# в координаты холста
import math, numpy as np
from scipy.interpolate import make_interp_spline
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import Qt, QPointF
from AesmaLib.GraphWidget.Axis import Axis


class Chart:
    def __init__(self, points: list = None, name: str = '', 
                 color: QColor = Qt.white, options: str = ''):
        self.__name = name
        self.__visibility = True
        self.__options = options
        self.__pen = self.setPen(QPen(color, 1), Qt.SolidLine)
        # self.__pen.setStyle(Qt.SolidLine)
        self.__axes = {}
        self.__coefs = [1, 1]
        self.__points = []
        self.__spline = None
        if points:
            self.__points = points
            self.regenerate_axies()

    def setName(self, name: str):
        self.__name = name

    def getName(self):
        return self.__name

    def setVisibility(self, state: bool):
        self.__visibility = state

    def getVisibility(self):
        return self.__visibility

    def setOptions(self, options: str):
        self.__options = options

    def getOptions(self):
        return self.__options

    def setPen(self, pen: QPen, style=None):
        self.__pen = pen
        if style:
            self.__pen.setStyle(style)

    def getPen(self):
        return self.__pen

    def setAxes(self, axes: dict):
        self.__axes = axes

    def getAxes(self):
        return self.__axes

    def setAxis(self, axis: Axis, name: str):
        self.__axes.update({name: axis})

    def getAxis(self, name: str):
        return self.__axes[name] if name in self.__axes.keys() else None

    def getCoefs(self):
        return self.__coefs

    def setCoefs(self, coef_min, coef_max):
        self.__coefs = [coef_min, coef_max]

    def setPoints(self, points: list, regenerate_axises: bool = True):
        if len(points):
            self.__points = points
            self._sortPoints()
            if regenerate_axises:
                self.regenerate_axies()
        else:
            print(__name__, 'Error = points array is empty')

    def getPoints(self, name=''):
        if 'x' == name:
            return [p.x() for p in self.__points]
        elif 'y' == name:
            return [p.y() for p in self.__points]
        else:
            return self.__points

    def addPoint(self, point: QPointF, regenerate_axes: bool = False):
        self.__points.append(point)
        # self._sortPoints()
        if regenerate_axes:
            self.regenerate_axies()

    def removePoint(self, index: int = -1, regenerate_axies: bool = False):
        if index == -1:
            self.__points = self.__points[:-1]
            if regenerate_axies:
                self.regenerate_axies()
        elif 0 < index < len(self.__points):
            self.__points.pop(index)
            if regenerate_axies:
                self.regenerate_axies()
        else:
            print(__name__, 'Error = incorrect point index')

    def clearPoints(self):
        self.__points.clear()
    
    def get_spline(self):
        return self.__spline

    def getTranslatedPoints(self, width: float, height: float):
        result = []
        points = self.__points.copy()
        points.sort(key=lambda p: p.x())
        for point in points:
            result.append(QPointF(
                self.translateCoordinate('x', point.x(), width),
                self.translateCoordinate('y', point.y(), height),
            ))
        return result

    def translateCoordinate(self, name: str, value: float, length: float):
        if name in self.__axes:
            coef = length / self.__axes[name].getLength()
            value = (value - self.__axes[name].getMinimum()) * coef
            return value
        else:
            print("Error translating point:", "wrong axis name")
            return 0

    def untranslatePoint(self, name: str, value: float, length: float):
        if name in self.__axes:
            coef = self.__axes[name].getLength() / length
            return self.__axes[name].getMinimum() + value * coef
        else:
            print("Error untranslating point:", "wrong axis name")
            return 0

    def regenerate_axies(self):
        if len(self.__points) > 1:
            self._regenerate_axis('x')
            self._regenerate_axis('y')

    def _regenerate_axis(self, name: str):
        func = lambda p: p.x() if name == 'x' else p.y()
        point_min: QPointF = min(self.__points, key=func)
        point_max: QPointF = max(self.__points, key=func)
        axis_min = point_min.x() if name == 'x' else point_min.y()
        axis_max = point_max.x() if name == 'x' else point_max.y()
        axis_min, axis_max, _ = Chart._calculate_axies(axis_min, axis_max)
        axis = Axis(axis_min * 1.0, axis_max * 1.0)
        self.__axes.update({name: axis})

    def _sortPoints(self):
        if len(self.__points) > 1:
            self.__points = sorted(self.__points, key=lambda p: p.x())

    @staticmethod
    def _calculate_axies(axis_start, axis_end, ticks=10):
        if (axis_end - axis_start):
            nice_range = Chart._nice_number(axis_end - axis_start, 0)
            nice_tick = Chart._nice_number(nice_range / (ticks - 1), 1)
            new_axis_start = math.floor(axis_start / nice_tick) * nice_tick
            new_axis_end = math.ceil(axis_end / nice_tick) * nice_tick
            axis_start = new_axis_start
            axis_end = new_axis_end
            return (new_axis_start, new_axis_end, nice_tick)
        else:
            return (axis_start, axis_end, ticks)
    @staticmethod
    def _nice_number(value, round_=False):
        '''nice_number(value, round_=False) -> float'''
        exponent = math.floor(math.log(value, 10))
        fraction = value / 10 ** exponent

        if round_:
            if fraction < 1.5:
                nice_fraction = 1.
            elif fraction < 3.:
                nice_fraction = 2.
            elif fraction < 7.:
                nice_fraction = 5.
            else:
                nice_fraction = 10.
        else:
            if fraction <= 1:
                nice_fraction = 1.
            elif fraction <= 2:
                nice_fraction = 2.
            elif fraction <= 5:
                nice_fraction = 5.
            else:
                nice_fraction = 10.

        return nice_fraction * 10 ** exponent

    @staticmethod
    def _nice_bounds(axis_start, axis_end, num_ticks=10):
        '''
        nice_bounds(axis_start, axis_end, num_ticks=10) -> tuple
        @return: tuple as (nice_axis_start, nice_axis_end, nice_tick_width)
        '''
        axis_width = axis_end - axis_start
        nice_tick = 0
        if axis_width:
            nice_range = Chart._nice_number(axis_width)
            nice_tick = Chart._nice_number(nice_range / (num_ticks - 1), True)
            axis_start = math.floor(axis_start / nice_tick) * nice_tick
            axis_end = math.ceil(axis_end / nice_tick) * nice_tick

        return axis_start, axis_end, nice_tick
