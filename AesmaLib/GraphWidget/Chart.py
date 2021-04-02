# AesmaDiv 03.2020
# Класс для графиков: Данные графика.
# Точки и оси, функция трансляции значений по осям
# в координаты холста
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import Qt, QPointF
from AesmaLib.GraphWidget.Axis import Axis


class Chart:
    def __init__(self, points: list = None, name: str = '', color: QColor = Qt.white, options: str = ''):
        self.__name = name
        self.__visibility = True
        self.__options = options
        self.__pen = QPen(color, 1)
        self.__pen.setStyle(Qt.SolidLine)
        self.__axes = {}
        self.__coefs = [1, 1]
        if points is None:
            self.__points = []
        else:
            self.__points = points
            self.regenerateAxes()

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

    def setPen(self, pen: QPen):
        self.__pen = pen

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
                self.regenerateAxes()
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
            self.regenerateAxes()

    def removePoint(self, index: int = -1, regenerate_axes: bool = False):
        if index == -1:
            self.__points = self.__points[:-1]
            if regenerate_axes:
                self.regenerateAxes()
        elif 0 < index < len(self.__points):
            self.__points.pop(index)
            if regenerate_axes:
                self.regenerateAxes()
        else:
            print(__name__, 'Error = incorrect point index')

    def clearPoints(self):
        self.__points.clear()

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

    def regenerateAxes(self):
        if len(self.__points) > 1:
            self._regenerateAxis('x')
            self._regenerateAxis('y')

    def _regenerateAxis(self, name: str):
        point_min: QPointF = min(self.__points, key=lambda p: p.x() if name == 'x' else p.y())
        point_max: QPointF = max(self.__points, key=lambda p: p.x() if name == 'x' else p.y())
        axis_min = point_min.x() if name == 'x' else point_min.y()
        axis_max = point_max.x() if name == 'x' else point_max.y()
        axis = Axis(axis_min * 1.0, axis_max * 1.0)
        self.__axes.update({name: axis})

    def _sortPoints(self):
        if len(self.__points) > 1:
            self.__points = sorted(self.__points, key=lambda p: p.x())
