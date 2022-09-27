"""
    Модуль содержит классы моделей для таблиц и комбобоксов,
    которые описывают механизм отображения элементов
"""
from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6.QtCore import QSortFilterProxyModel, QVariant, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem


class TemplateTableModel(QAbstractTableModel):
    """Шаблон модели таблицы"""

    def __init__(self, data: list = None, display: list = None, parent=None):
        QAbstractTableModel.__init__(self, parent=parent)
        self._data = [] if data is None else data
        self._display = [] if display is None else display
        self._row_count = len(self._data)
        self._col_count = len(self._display)

    def loadData(self, data: list):
        """загружает данные из списка"""
        self._data.clear()
        self._data = data
        self._row_count = len(data)

    def rowCount(self, _parent=QModelIndex()) -> int:
        """возвращает кол-во строк"""
        return self._row_count

    def columnCount(self, _parent=QModelIndex()) -> int:
        """возвращает кол-во столбцов"""
        return self._col_count


class ListModel(TemplateTableModel):
    """Модель таблицы для списка тестов"""

    def __init__(self, data: list = None, display: list = None, headers: list = None, parent=None):
        super().__init__(data, display)
        self._headers = [] if headers is None else headers

    def getDisplay(self) -> list:
        """имплементация метода суперкласса (элементы отображения)"""
        return self._display

    def setDisplay(self, display: list):
        """задаёт список элементов (столбцов) для отображения"""
        self._display = display

    def getHeaders(self) -> list:
        """имплементация метода суперкласса (заголовоки)"""
        return self._headers

    def getData(self) -> list:
        """имплементация метода суперкласса (данные)"""
        return self._data

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> QVariant:
        """возвращает отображаемое значение"""
        if not index.isValid():
            return QVariant()
        row, col = index.row(), index.column()
        data = self._data[row]
        if role == Qt.ItemDataRole.UserRole:
            return QVariant(data)
        if role == Qt.ItemDataRole.DisplayRole:
            key = self._display[col]
            return data[key] if key in data.keys() else QVariant()
        return QVariant()

    def headerData(self, column: int, orientation, role=Qt.ItemDataRole.DisplayRole) -> QVariant:
        """возвращает заголовок"""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return QVariant(self._headers[column])
        return QVariant()

    def getRowContains(self, column: int, value, role=Qt.ItemDataRole.DisplayRole) -> QModelIndex:
        """возвращает строку содержащую значение"""
        matches = self.match(self.index(0, column), role, value, -1,
                             flags=Qt.MatchFlag.MatchContains | Qt.MatchFlag.MatchRecursive)
        return  matches[0] if matches else None

    def findContains(self, value, role=Qt.ItemDataRole.DisplayRole):
        """возвращает список строк содержащих значение"""
        matches = self.match(self.index(0, 0), role, value, -1,
                             flags=Qt.MatchContains | Qt.MatchRecursive)
        return [index.data(Qt.ItemDataRole.UserRole) for index in matches] if matches else []


class FilterModel(QSortFilterProxyModel):
    """Модель для фильтра таблиц"""

    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
        self.parent = parent
        self.setDynamicSortFilter(True)
        self.setFilterKeyColumn(0)
        self.parent = parent
        self._filters: list = []
        self._conditions: dict = {}

    def applyFilter(self, filters=None):
        """применяет фильтр"""
        self._filters = filters if isinstance(filters, list) else []
        self._conditions = filters if isinstance(filters, dict) else {}
        self.setFilterFixedString("")

    def resetFilter(self):
        """сбрасывает фильтр"""
        self.applyFilter()

    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        """применяет фильтр к ряду"""
        if self._conditions:
            return self.__filterUserRole(source_row, source_parent)
        if self._filters:
            return self.__filterDisplayRole(source_row, source_parent)
        return True

    def __filterDisplayRole(self, source_row, source_parent) -> bool:
        """фильтрует по отображаемым полям"""
        result = True
        if not self._filters:
            return True
        for i, fltr in enumerate(self._filters):
            index = self.sourceModel().index(source_row, i, source_parent)
            if not index.isValid():
                continue
            data = str(index.data(Qt.ItemDataRole.DisplayRole))
            result &= fltr in data if data else True
        return result

    def __filterUserRole(self, source_row, source_parent) -> bool:
        """фильтрует по скрытым полям"""
        if not self._conditions:
            return False
        # я не знаю как избавиться от вложенных условий и не потерять читабельность кода
        if source_row:  # фильтровать все поля кроме нулевого
            index = self.sourceModel().index(source_row, 0, source_parent)
            data = index.data(Qt.ItemDataRole.UserRole)
            if data:
                for key, value in self._conditions.items():
                    if key in data.keys():
                        return (not value) or (data[key] == value)
            return False
        return True


class ComboItemModel(FilterModel):
    """Класс модели для комбобоксов с фильтрацией"""

    def __init__(self, parent=None):
        FilterModel.__init__(self, parent)
        self.parent = parent
        self._model = QStandardItemModel(0, 0)
        self._display = ""
        self.setSourceModel(self._model)
        self.setDynamicSortFilter(True)

    @property
    def display(self) -> str:
        """возвращает имя отображаемого поля"""
        return self._display

    def model(self) -> QStandardItemModel:
        """возвращает модель"""
        return self._model

    def fill(self, rows: list, display: str):
        """заполняет комбобокс элементами из списка"""
        self._display = display
        for _, value in enumerate(rows):
            self._model.appendRow(self.createRow(value))

    def createRow(self, data: dict) -> QStandardItem:
        """создаёт элемент-строку для комбобокса"""
        result = QStandardItem()
        result.setText(data[self._display] if self._display in data else 'Error')
        result.setData(data, Qt.ItemDataRole.UserRole)
        return result

    def findIndex(self, value) -> int:
        """возвращает индекс элемента содержащего значение"""
        items = self._model.findItems('', Qt.MatchFlag.MatchContains)
        if not items:
            return 0
        # функция поиска если value - словарь
        if isinstance(value, dict):
            key = next(iter(value))
            val = value[key]
            func = lambda data: key in data and data[key] == val
        # -/- если value - значение
        else:
            func = lambda data: value in data.values()
        return next((index for index, item in enumerate(items) \
                        if func(item.data(Qt.ItemDataRole.UserRole))), 0)

    def getItem(self, index=-1) -> QStandardItem:
        """возвращает элемент по индексу"""
        items = self._model.findItems('', Qt.MatchContains)
        if not items:
            return None
        if 0 <= index < self.rowCount():
            items = self._model.findItems('', Qt.MatchContains)
            return items[index]
        index = self.parent.currentIndex()
        return items[index]

    def selectContains(self, value):
        """устанавливает текущим элемент содержащий значение"""
        index = self.findIndex(value)
        self.applyFilter()
        self.select(index)

    def select(self, index):
        """устанавливает текущим элемент по индексу"""
        if self.parent:
            self.parent.setCurrentIndex(index)

    def checkAlreadySelected(self, condition):
        """проверяет выбран ли элемент списка отвечающий условию"""
        if not condition or not self.parent:
            return False
        item = self.parent.currentData()
        if not item:
            return False
        if isinstance(condition, dict):
            key = next(iter(condition))
            return (key in item) and (item[key] == condition[key])
        return condition in item.values()
