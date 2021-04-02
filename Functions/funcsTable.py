from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QItemSelectionModel
from AesmaLib import journal
from GUI.Models import ListModel, QModelIndex


def init(table_view: QTableView, display: list, headers: list,
         data=None, headers_sizes: list = None, headers_resizes: list = None,
         filter_proxy: QSortFilterProxyModel = None):
    model = ListModel(data=data, display=display, headers=headers)
    if filter_proxy is None:
        filter_proxy = QSortFilterProxyModel()
    filter_proxy.setSourceModel(model)
    table_view.setModel(filter_proxy)
    set_headers(table_view, len(display), headers_sizes, headers_resizes)


def get_data(table_view: QTableView):
    proxy: QSortFilterProxyModel = table_view.model()
    current_model = proxy.sourceModel()
    data = current_model.getData()
    return data


def set_data(table_view: QTableView, data):
    proxy: QSortFilterProxyModel = table_view.model()
    current_model = proxy.sourceModel()
    display, headers = current_model.getDisplay(), current_model.getHeaders()
    new_model = ListModel(data=data, display=display, headers=headers)
    proxy.setSourceModel(new_model)
    table_view.setModel(proxy)


def add_row(table_view: QTableView, row):
    data = get_data(table_view)
    data.append(row)
    set_data(table_view, data)


def remove_last_row(table_view: QTableView):
    data = get_data(table_view)
    if len(data):
        data.pop()
    set_data(table_view, data)


def clear_table(table_view: QTableView):
    set_data(table_view, [])


def get_row(table_view: QTableView):
    try:
        index = table_view.currentIndex()
        index= index.sibling(index.row(), index.column())
        items: dict = index.data(Qt.UserRole)
        return items
    except BaseException as error:
        journal.log(__name__ + " error: " + str(error))
        return None


def set_headers(table_view: QTableView, headers_count: int,
                headers_sizes: list, headers_resizes: list):
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
    sel_model: QItemSelectionModel = table_view.selectionModel()
    index: QModelIndex = table_view.model().sourceModel().index(row, 0)
    mode = QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
    sel_model.select(index, mode)
    table_view.setFocus()


def get_selected_row(table_view: QTableView):
    sel_model: QItemSelectionModel = table_view.selectionModel()
    sel_row = sel_model.selectedRows()[0]
    return get_row(table_view)
