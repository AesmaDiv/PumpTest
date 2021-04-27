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
    """ Класс кривой графика """
    def __init__(self, points: list = None, name: str = '', 
                 color: QColor = Qt.white, options: str = ''):
        self.__name = name
        self.__visibility = True
        self.__options = options
        self.__pen = self.setPen(QPen(color, 1), Qt.SolidLine)
        self.__axes = {}
        self.__coefs = [1, 1]
        self.__points = np.empty([2, 0], dtype=float)
        self.__spline = None
        if points:
            self.__points = np.array(points, dtype=float)
            self.regenerateAxies()

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

    def setPoints(self, points: list, do_regenerate_axises: bool = True):
        if len(points):
            self.__points = np.array(points, dtype=float)
            self._sortPoints()
            if do_regenerate_axises:
                self.regenerateAxies()
        else:
            print(__name__, 'Error = points array is empty')

    def getPoints(self, name=''):
        result = self.__points.tolist()
        if name == 'x':
            return result[0]
        elif name == 'y':
            return result[1]
        return result

    def addPoint(self, x: float, y: float, do_regenerate_axes: bool = False):
        self.__points = np.append(self.__points, [[x], [y]], axis=1)
        # self._sortPoints()
        if do_regenerate_axes:
            self.regenerateAxies()

    def removePoint(self, index: int = -1, do_regenerate_axies: bool = False):
        if (index == -1) or (0 < index < len(self.__points[0])):
            self.__points = np.delete(self.__points, index, 1)
            if do_regenerate_axies:
                self.regenerateAxies()
        else:
            print(__name__, 'Error = incorrect point index')

    def clearPoints(self):
        self.__points = np.empty([2, 0], dtype=float)
    
    def getSpline(self):
        return self.__spline

    def getTranslatedCurve(self, width: float, height: float):
        result = self.regenerateCurve()
        return self.getTranslatedPoints(width, height)

    def getTranslatedPoints(self, width: float, height: float):
        result = self.__points.copy()
        # result.sort(key=lambda p: p[0])
        coeff_x = width / self.__axes['x'].getLength()
        coeff_y = height / self.__axes['y'].getLength()
        result[0] = list(map(lambda x: x * coeff_x, result[0]))
        result[1] = list(map(lambda y: y * coeff_y, result[1]))
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

    def regenerateAxies(self):
        if np.shape(self.__points)[1] > 1:
            mins = np.amin(self.__points, axis=1)
            maxs = np.amax(self.__points, axis=1)
            xmin, xmax, _ = Chart._calculateAxies(mins[0], maxs[0])
            ymin, ymax, _ = Chart._calculateAxies(mins[1], maxs[1])
            xaxis = Axis(xmin * 1.0, xmax * 1.0)
            yaxis = Axis(ymin * 1.0, ymax * 1.0)
            self.__axes.update({'x': xaxis, 'y': yaxis})
        self.regenerateSpline()

    def regenerateSpline(self):
        if np.shape(self.__points)[1] > 1:
            points = self.__points.copy()
            if points[0][0] > points[0][-1]:
                points = np.flip(points, axis=1)
            self.__spline = make_interp_spline(points[0], points[1], k=2)

    def regenerateCurve(self, points=None, samples=100):
        if points is None:
            if self.__points.any():
                return self.regenerateCurve(self.__points)
            else:
                None
        else:
            result_x = np.linspace(0, max(points[0]), samples)
            result_y = self.__spline(result_x)
            result = np.array([result_x, result_y], dtype=float)
            return result
        
    def _sortPoints(self):
        if len(self.__points) > 1:
            self.__points = sorted(self.__points, key=lambda p: p[0])

    @staticmethod
    def _calculateAxies(axis_start, axis_end, ticks=10):
        if (axis_end - axis_start):
            nice_range = Chart._niceNumber(axis_end - axis_start, 0)
            nice_tick = Chart._niceNumber(nice_range / (ticks - 1), 1)
            new_axis_start = math.floor(axis_start / nice_tick) * nice_tick
            new_axis_end = math.ceil(axis_end / nice_tick) * nice_tick
            axis_start = new_axis_start
            axis_end = new_axis_end
            return (new_axis_start, new_axis_end, nice_tick)
        else:
            return (axis_start, axis_end, ticks)
    @staticmethod
    def _niceNumber(value, round_=False):
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
    def _niceBounds(axis_start, axis_end, num_ticks=10):
        '''
        nice_bounds(axis_start, axis_end, num_ticks=10) -> tuple
        @return: tuple as (nice_axis_start, nice_axis_end, nice_tick_width)
        '''
        axis_width = axis_end - axis_start
        nice_tick = 0
        if axis_width:
            nice_range = Chart._niceNumber(axis_width)
            nice_tick = Chart._niceNumber(nice_range / (num_ticks - 1), True)
            axis_start = math.floor(axis_start / nice_tick) * nice_tick
            axis_end = math.ceil(axis_end / nice_tick) * nice_tick

        return axis_start, axis_end, nice_tick
