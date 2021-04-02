"""
    Модуль содержит классы моделей для таблиц и комбобоксов,
    которые описывают механизм отображения элементов
"""
from PyQt5.QtCore import Qt, QAbstractTableModel, QSortFilterProxyModel, QVariant
from PyQt5.Qt import QModelIndex


class TemplateTableModel(QAbstractTableModel):
    """ Шаблон модели таблицы """
    def __init__(self, data: list=None, display: list=None, parent=None):
        QAbstractTableModel.__init__(self, parent=parent)
        self._data = [] if data is None else data
        self._display = [] if display is None else display
        self._row_count = len(self._data)
        self._col_count = len(self._display)

    def load_data(self, data: list):
        """ загрузка данных из списка """
        self._data.clear()
        self._data = data
        self._row_count = len(data)

    def rowCount(self, parent=QModelIndex()):
        """ кол-во строк """
        return self._row_count

    def columnCount(self, parent=QModelIndex()):
        """ кол-во столбцов """
        return self._col_count


class ListModel(TemplateTableModel):
    """ Модель таблицы для списка тестов """
    def __init__(self, data: list=None, display: list=None, headers: list=None, parent=None):
        super().__init__(data, display)
        self._headers = [] if headers is None else headers

    def getDisplay(self):
        """ имплементация метода суперкласса (элементы отображения) """
        return self._display

    def getHeaders(self):
        """ имплементация метода суперкласса (заголовоки) """
        return self._headers

    def getData(self):
        """ имплементация метода суперкласса (данные) """
        return self._data

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        """ отображаемое значение """
        if index.isValid():
            row = index.row()
            col = index.column()
            data: dict = self._data[row]
            if role == Qt.DisplayRole:
                key: str = self._display[col]
                if key in data.keys():
                    value = data[key]
                    return value
            elif role == Qt.UserRole:
                return QVariant(data)
        return QVariant()

    def headerData(self, col, orientation, role=Qt.DisplayRole):
        """ заголовок """
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self._headers[col])
        return QVariant()

    def get_row_contains(self, column: int, value, role=Qt.DisplayRole):
        """ получение строки содержащей значение """
        result = None
        matches = self.match(self.index(0, column), role, value, -1,
                             flags=Qt.MatchContains | Qt.MatchRecursive)
        if matches:
            result = matches[0]
        return result

    def find_contains(self, value, role=Qt.DisplayRole):
        """ получение списка строк содержащих значение """
        result = []
        matches = self.match(self.index(0, 0), role, value, -1,
                             flags=Qt.MatchContains | Qt.MatchRecursive)
        found_num: int = len(matches)
        if found_num > 0:
            for index in matches:
                data = index.data(Qt.UserRole)
                # dtat = index.data(Qt.DisplayRole)
                result.append(data)
        return result


class PumpListModel(TemplateTableModel):
    """ Модель таблицы для списка насосов """
    _display = []
    _col_count = 0

    def load_data(self, data: list, display: str):
        """ загрузка данных из списка """
        super().load_data(data)
        self._display = display
        self._col_count = len(display)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        """ отображаемое значение """
        row = index.row()
        column = index.column()
        if role == Qt.DisplayRole:
            col_name: str = self._display[column]
            row_data: dict = self._data[row]
            if col_name in row_data.keys():
                result = row_data[col_name]
                return str(result)
        return ""


class FilterModel(QSortFilterProxyModel):
    """ Модель для фильтра таблиц """
    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self.setDynamicSortFilter(True)
        self.setFilterKeyColumn(0)
        self._filters: list = None
        self._conditions: dict = None

    def applyFilter(self, filters=None):
        """ применение фильтра """
        self._filters = filters if isinstance(filters, list) else None
        self._conditions = filters if isinstance(filters, dict) else None
        self.setFilterFixedString("")

    def filterAcceptsRow(self, source_row, source_parent):
        if self._conditions is not None:
            return self.__filterUserRole(source_row, source_parent)
        elif self._filters is not None:
            return self.__filterDisplayRole(source_row, source_parent)
        else:
            return True

    def __filterDisplayRole(self, source_row, source_parent):
        result: bool = True
        if self._filters is not None:
            count: int = len(self._filters)
            for i in range(count):
                index: QModelIndex = self.sourceModel().index(source_row, i, source_parent)
                if index.isValid():
                    data = str(index.data(Qt.DisplayRole))
                    result &= self._filters[i] in data
        return result

    def __filterUserRole(self, source_row, source_parent):
        index: QModelIndex = self.sourceModel().index(source_row, 0, source_parent)
        data: dict = index.data(Qt.UserRole)
        if data is not None and self._conditions is not None:
            for key, value in self._conditions.items():
                if key in data.keys():
                    return data[key] == value
        return False
