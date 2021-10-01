"""
    Модуль содержит функции для работы с таблицами главного окна
"""
from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QItemSelectionModel
from Classes.UI import models as models
from AesmaLib.journal import Journal


def create(table_view: QTableView, display: list, headers: list,
            data=None, headers_sizes: list=None, headers_resizes: list=None,
            filter_proxy: QSortFilterProxyModel=None):
    """ создание таблицы """
    model = models.ListModel(data=data, display=display, headers=headers)
    if filter_proxy is None:
        filter_proxy = QSortFilterProxyModel()
    filter_proxy.setSourceModel(model)
    table_view.setModel(filter_proxy)
    set_headers(table_view, len(display),
                                headers_sizes, headers_resizes)


def get_data(table_view: QTableView):
    """ получение данных из таблицы """
    proxy: QSortFilterProxyModel = table_view.model()
    current_model = proxy.sourceModel()
    data = current_model.getData()
    return data


def set_data(table_view: QTableView, data):
    """ запись данных в таблицу """
    proxy: QSortFilterProxyModel = table_view.model()
    current_model = proxy.sourceModel()
    display, headers = current_model.getDisplay(), current_model.getHeaders()
    new_model = models.ListModel(data=data, display=display, headers=headers)
    proxy.setSourceModel(new_model)
    table_view.setModel(proxy)


def add_row(table_view: QTableView, row):
    """ добавление строки в таблицу """
    data = get_data(table_view)
    data.append(row)
    set_data(table_view, data)


def remove_last_row(table_view: QTableView):
    """ удаление последней строки из таблицы """
    data = get_data(table_view)
    if len(data):
        data.pop()
    set_data(table_view, data)


def clear(table_view: QTableView):
    """ полная очистка таблицы """
    set_data(table_view, [])


def get_row(table_view: QTableView):
    """ получение строки из таблицы """
    try:
        m_index = table_view.currentIndex()
        m_index = m_index.sibling(m_index.row(), m_index.column())
        items = m_index.data(Qt.UserRole)
        return items
    except BaseException as error:
        Journal.log(__name__ + " error: " + str(error))
        return None


def set_headers(table_view: QTableView, headers_count: int,
                headers_sizes: list, headers_resizes: list):
    """ установка заголовков столбцов таблицы """
    header: QHeaderView = table_view.verticalHeader()
    header.setSectionResizeMode(QHeaderView.Fixed)
    header.setDefaultSectionSize(20)
    header: QHeaderView = table_view.horizontalHeader()
    if headers_sizes and len(headers_sizes) == headers_count:
        for i in range(headers_count):
            table_view.setColumnWidth(i, headers_sizes[i])
    if headers_resizes and len(headers_resizes) == headers_count:
        for i in range(headers_count):
            header.setSectionResizeMode(i, headers_resizes[i])


def select_row(table_view: QTableView, row: int):
    """ выбор строки в таблице по индексу """
    sel_model: QItemSelectionModel = table_view.selectionModel()
    index = table_view.model().sourceModel().index(row, 0)
    mode = QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
    sel_model.select(index, mode)
    table_view.setFocus()
