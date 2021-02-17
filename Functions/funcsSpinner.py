from PyQt5.QtWidgets import QComboBox, QCompleter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from AesmaLib import journal


def fill(combo: QComboBox, rows: list, display_key: str = '', with_completer=False):
    model = QStandardItemModel(0, len(rows))
    model.setColumnCount(1)
    completer = __fill_combo_model(model, rows, display_key, with_completer)
    if with_completer and combo.isEditable():
        combo.setCompleter(completer)
    combo.setModel(model)


def get_values(combo: QComboBox, index=-1):
    index = combo.currentIndex() if index < 0 else index
    item = combo.model().item(index)
    result = item.data(Qt.UserRole)
    return result


def find_item_containing(combo: QComboBox, value):
    model: QStandardItemModel = combo.model()
    index = __find_index(model, value)
    return index


def select_item_containing(combo: QComboBox, value):
    index = find_item_containing(combo, value)
    combo.setCurrentIndex(index)


def get_current_value(combo: QComboBox, name: str = ''):
    result = None
    if name == '':
        result = combo.currentText()
        # index = combo.currentIndex()
        # item = combo.model().item(index)
        # result = item.data(Qt.DisplayRole)
    else:
        index = combo.currentIndex()
        item = combo.model().item(index)
        values = item.data(Qt.UserRole)
        if type(values) is dict:
            if name in values:
                result = values[name]
    return result


def __fill_combo_model(model: QStandardItemModel, rows: list, display_key: str, with_completer: bool):
    words = []
    for row in rows:
        item = QStandardItem()
        __fill_combo_item(item, row, display_key)
        if with_completer and type(row) is dict and display_key in row:
            words.append(row[display_key])
        model.appendRow(item)
    return QCompleter(words) if with_completer else None


def __fill_combo_item(item: QStandardItem, row, display_key: str):
    if type(row) is dict and len(row.items()) > 0:
        item.setData(row[display_key], Qt.DisplayRole)
        item.setData(row, Qt.UserRole)
    else:
        item.setData(row, Qt.DisplayRole)


def __find_index(model: QStandardItemModel, value):
    result = __find_index_in_display(model, value) or __find_index_in_user(model, value)
    return result


def __find_index_in_display(model: QStandardItemModel, value):
    try:
        if type(value) is str:
            items: QStandardItem = model.findItems(value)
            if len(items):
                item: QStandardItem = items[0]
                index: Qt.QModelIndex = model.indexFromItem(item)
                result = index.row()
                return result
    except BaseException as error:
        journal.log(__name__ + " Error: " + str(error))
    return 0


def __find_index_in_user(model: QStandardItemModel, value):
    try:
        item: QStandardItem = None
        data = None
        for result in range(model.rowCount()):
            item = model.item(result)
            data = item.data(Qt.UserRole)
            if type(data) is dict:
                if not type(value) is dict:
                    if value in data.values():
                        return result
                else:
                    for key, val in value.items():
                        if key in data.keys():
                            if data[key] == val:
                                return result
    except BaseException as error:
        journal.log(__name__ + " Error: " + str(error))
    return 0
