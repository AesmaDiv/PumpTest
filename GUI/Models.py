from PyQt5.QtCore import Qt, QAbstractTableModel, QSortFilterProxyModel, QVariant, QRegExp
from PyQt5.Qt import QModelIndex


class ListModel(QAbstractTableModel):
    _data: list = None
    _display: list = None
    _headers: list = None
    _row_count: int = 0
    _col_count: int = 0

    def __init__(self, data: list = None, display: list = None, headers: list = None, parent=None):
        QAbstractTableModel.__init__(self, parent=parent)
        if data is None: data = []
        if display is None: display = []
        if headers is None: headers = []
        self._data = data
        self._display = display
        self._headers = headers
        self._col_count = len(display)
        self._row_count = 0 if data is None else len(data)

    def load_data(self, data: list):
        self._data.clear()
        self._data = data
        self._row_count = 0 if data is None else len(self._data)

    def getDisplay(self):
        return self._display

    def getHeaders(self):
        return self._headers

    def getData(self):
        return self._data

    def rowCount(self, parent=None):
        return self._row_count

    def columnCount(self, parent=None):
        return self._col_count

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
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
            else:
                return QVariant()
        else:
            return QVariant()

    def headerData(self, col, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self._headers[col])

    def get_row_contains(self, column: int, value, role=Qt.DisplayRole):
        result = None
        matches: list = self.match(self.index(0, column), role, value, -1, flags=Qt.MatchContains | Qt.MatchRecursive)
        if matches and len(matches):
            result = matches[0]
        return result

    def find_contains(self, value, role=Qt.DisplayRole):
        result: list = []
        matches: list = self.match(self.index(0, 0), role, value, -1, flags=Qt.MatchContains | Qt.MatchRecursive)
        found_num: int = len(matches)
        if found_num > 0:
            for index in matches:
                data = index.data(Qt.UserRole)
                dtat = index.data(Qt.DisplayRole)
                result.append(data)
        return result


class FilterModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self.setDynamicSortFilter(True)
        self.setFilterKeyColumn(0)
        self._filters: list = None
        self._conditions: dict = None

    def applyFilter(self, filters=None):
        self._filters = filters if type(filters) is list else None
        self._conditions = filters if type(filters) is dict else None
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


class PumpListModel(QAbstractTableModel):
    def __init__(self, data: list = [], display: list = []):
        QAbstractTableModel.__init__(self)
        self._data = data
        self._data = data
        self._display = display
        self._row_count = len(data)
        self._col_count = len(display)

    def load_data(self, data: list, display: str):
        self._data = data
        self._display = display
        self._row_count = len(data)
        self._col_count = len(display)

    def rowCount(self, parent=QModelIndex()):
        return self._row_count

    def columnCount(self, parent=QModelIndex()):
        return self._col_count

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        row = index.row()
        column = index.column()
        if role == Qt.DisplayRole:
            col_name: str = self._display[column]
            row_data: dict = self._data[row]
            if col_name in row_data.keys():
                result = row_data[col_name]
                return str(result)
