"""
    Модуль описывает класс маркеров для графика
"""
from operator import itemgetter
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QEvent, QPoint, QPointF, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame
from AesmaLib.GraphWidget import Chart
from Classes.Graph.pump_graph import PumpGraph


class Markers(QFrame):
    """ Класс маркеров графика """
    eventMove = pyqtSignal(dict)

    def __init__(self, names: list, graph: PumpGraph, parent=None):
        super().__init__(parent)
        self._graph: PumpGraph = graph
        self._names: list = names
        self._markers: dict = {}
        self._colors: dict = {}
        self._knots: dict = {}
        self._area: QFrame = QFrame(self)
        self._area.installEventFilter(self)
        self._area.setGeometry(1, 1, 10, 10)
        self._area.setFrameShape(QFrame.StyledPanel)
        self._area.setFrameShadow(QFrame.Raised)
        self._area.setStyleSheet(
            "QFrame {"
            "border: 1px solid red;"
            "background: transparent;"
            "}"
        )
        self._init_markers()

    def _init_markers(self):
        """ инициализация маркеров """
        for name in self._names:
            self._markers.update({name: QPointF(5.0, 5.0)})
            self._colors.update({name: Qt.yellow})
            self._knots.update({name: []})

    def eventFilter(self, obj: QFrame, event_):
        """ фильтр событий """
        if event_.type() == QEvent.Paint:
            if obj == self._area:
                painter = QtGui.QPainter()
                painter.begin(obj)
                self._drawMarkers(painter)
                self._drawKnots(painter)
                painter.end()
            return True
        if event_.type() == QEvent.MouseMove:
            if obj == self._area:
                # funcsTemporary.process_move_marker(obj, e)
                pass
        return super().eventFilter(obj, event_)

    def getMarkerPosition(self, name: str):
        """ получение координат маркера """
        if name in self._markers:
            return self._markers[name]
        else:
            print(__name__, 'Error = no such marker')
            return QPointF(0, 0)

    def setMarkerPosition(self, name: str, pos: QPointF):
        """ установка координат маркера """
        if name in self._markers:
            self._markers.update({name: pos})
        else:
            print(__name__, 'Error = no such marker')

    def setMarkerColor(self, name: str, color):
        """ установка цвета маркера """
        if name in self._colors:
            self._colors.update({name: color})
        else:
            print(__name__, 'Error = no such marker')

    def repositionFor(self, graph: PumpGraph):
        """ перенос маркера на другой холст """
        left, top, _, _ = graph.get_margins()
        size = graph.get_draw_area()
        self._area.setGeometry(left, top, size.width(), size.height())

    def addKnots(self):
        """ добавление узлов """
        for name in self._names:
            self.addKnot(name)

    def addKnot(self, name: str):
        """ добавление узла """
        if name in self._knots:
            self._knots[name].append(self._markers[name])
            self._area.repaint()

    def removeKnots(self):
        """ удаление узлов """
        for name in self._names:
            self.removeKnot(name)

    def removeKnot(self, name: str):
        """ удаление узла по имени """
        if name in self._knots and len(self._knots[name]) > 0:
            self._knots[name] = self._knots[name][:-1]
            self._area.repaint()

    def clearAllKnots(self):
        """ очистка узлов """
        for name in self._names:
            self.clearKnots(name)

    def clearKnots(self, name: str):
        """ очистка узлов по имени """
        if name in self._knots:
            self._knots.update({name: []})

    def moveMarker(self, point, name: str):
        """ перемещение маркера  по имени """
        pos = self.translatePointToPosition(point, name)
        self._markers[name] = pos
        # self.eventMove.emit({name: self.translatePositionToPoint(name)})
        self._area.repaint()

    def createBackground(self):
        """ создание подложки """
        pixmap = QPixmap(self._graph.size())
        self._graph.render(pixmap)
        pixmap.save('render.png')
        self.setStyleSheet("QFrame {background-image: url('render.png');}")
        self._graph.setVisible(False)

    def _drawMarkers(self, painter):
        """ отрисовка маркеров """
        for name in self._names:
            painter.setPen(QtGui.QPen(self._colors[name], 1))
            self._drawMarker(painter, name)

    def _drawMarker(self, painter, name: str):
        """ отрисовка маркера по имени """
        painter.drawLine(self._markers[name].x() - 5, self._markers[name].y(),
                         self._markers[name].x() + 5, self._markers[name].y())
        painter.drawLine(self._markers[name].x(), self._markers[name].y() - 5,
                         self._markers[name].x(), self._markers[name].y() + 5)

    def _drawKnots(self, painter):
        """ отрисовка узлов """
        for name in self._names:
            painter.setPen(QtGui.QPen(self._colors[name], 1))
            painter.setBrush(QtGui.QBrush(self._colors[name]))
            for point in self._knots[name]:
                painter.drawEllipse(point.x() - 2, point.y() - 2, 4, 4)

    def translatePositionToPoint(self, position: QPointF, name: str):
        """ пересчёт координат из значений в пиксели """
        result: QPoint = QPointF(0.0, 0.0)
        etalon: Chart = self._graph.get_chart(name.replace('test_', ''))
        if etalon is not None:
            size = self._area.size()
            max_x = etalon.getAxis('x').getMaximum()
            max_y = etalon.getAxis('y').getMaximum()
            result.setX(max_x * position.x() / size.width())
            result.setY(max_y * (size.height() - position.y()) / size.height())
        return result

    def translatePointToPosition(self, point: QPointF, name: str):
        """ пересчёт координат из пикселей в значения """
        result: QPoint = QPointF(0.0, 0.0)
        etalon: Chart = self._graph.get_chart(name.replace('test_', ''))
        if etalon is not None:
            size = self._area.size()
            max_x = etalon.getAxis('x').getMaximum()
            max_y = etalon.getAxis('y').getMaximum()
            result.setX(size.width() * point.x() / max_x)
            result.setY(size.height() * (1 - point.y() / max_y))
        return result

    def _addPointToKnots(self, name: str, point_x, point_y):
        """ добавление точки к узлам """
        if name in self._knots:
            self._knots[name].append((point_x, point_y))
        else:
            self._knots.update({name: []})
            self._addPointToKnots(name, point_x, point_y)

    def _getSortedPoints(self, name: str):
        """ получение отсортированных точек """
        points = sorted(self._knots[name], key=itemgetter(0))
        points_x, points_y = zip(*points)
        return list(points_x), list(points_y)
