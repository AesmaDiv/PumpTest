from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QItemSelectionModel
from AesmaLib import Journal
from AppClasses.UI.Models import ListModel, QModelIndex


def init(table_view: QTableView, display: list, headers: list, data=None, headers_sizes: list = None,
         headers_resizes: list = None, filter_proxy: QSortFilterProxyModel = None):
    model = ListModel(data=data, display=display, headers=headers)
    filter_proxy = QSortFilterProxyModel() if filter_proxy is None else filter_proxy
    filter_proxy.setSourceModel(model)
    table_view.setModel(filter_proxy)
    set_headers(table_view, len(display), headers_sizes, headers_resizes)
    pass


def get_data(table_view: QTableView):
    proxy: QSortFilterProxyModel = table_view.model()
    current_model: ListModel = proxy.sourceModel()
    data = current_model.getData()
    return data


def set_data(table_view: QTableView, data):
    proxy: QSortFilterProxyModel = table_view.model()
    current_model: ListModel = proxy.sourceModel()
    new_model: ListModel = ListModel(data=data, display=current_model.getDisplay(), headers=current_model.getHeaders())
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
        items: dict = index.sibling(index.row(), index.column()).data(Qt.UserRole)
        return items
    except BaseException as error:
        Journal.log(__name__ + " error: " + str(error))
        return None


def set_headers(table_view: QTableView, headers_count: int, headers_sizes: list, headers_resizes: list):
    header: QHeaderView = table_view.verticalHeader()
    header.setSectionResizeMode(QHeaderView.Fixed)
    header.setDefaultSectionSize(20)
    header: QHeaderView = table_view.horizontalHeader()
    is_headers_sizes_set = headers_sizes and len(headers_sizes) == headers_count
    is_headers_resizes_set = headers_resizes and len(headers_resizes) == headers_count
    for i in range(headers_count):
        if is_headers_sizes_set:
            table_view.setColumnWidth(i, headers_sizes[i])
        if is_headers_resizes_set:
            header.setSectionResizeMode(i, headers_resizes[i])
    pass


def select_row(table_view: QTableView, row: int):
    sel_model: QItemSelectionModel = table_view.selectionModel()
    index: QModelIndex = table_view.model().sourceModel().index(row, 0)
    # sel_model.setCurrentIndex(index, QItemSelectionModel.Rows | QItemSelectionModel.Toggle)
    sel_model.select(index, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
    table_view.setFocus()


def get_selected_row(table_view: QTableView):
    sel_model: QItemSelectionModel = table_view.selectionModel()
    sel_row = sel_model.selectedRows()[0]
    row = get_row(table_view)
    pass


