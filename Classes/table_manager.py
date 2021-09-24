from PyQt5.QtWidgets import QTableView, QHeaderView
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QItemSelectionModel
from AesmaLib import journal
from GUI.models import ListModel, QModelIndex


class TableManager:
    @staticmethod
    def create(table_view: QTableView, display: list, headers: list,
               data=None, headers_sizes: list=None, headers_resizes: list=None,
               filter_proxy: QSortFilterProxyModel=None):
        model = ListModel(data=data, display=display, headers=headers)
        if filter_proxy is None:
            filter_proxy = QSortFilterProxyModel()
        filter_proxy.setSourceModel(model)
        table_view.setModel(filter_proxy)
        TableManager.set_headers(table_view, len(display),
                                 headers_sizes, headers_resizes)

    @staticmethod
    def get_data(table_view: QTableView):
        proxy: QSortFilterProxyModel = table_view.model()
        current_model = proxy.sourceModel()
        data = current_model.getData()
        return data

    @staticmethod
    def set_data(table_view: QTableView, data):
        proxy: QSortFilterProxyModel = table_view.model()
        current_model = proxy.sourceModel()
        display, headers = current_model.getDisplay(), current_model.getHeaders()
        new_model = ListModel(data=data, display=display, headers=headers)
        proxy.setSourceModel(new_model)
        table_view.setModel(proxy)

    @staticmethod
    def add_row(table_view: QTableView, row):
        data = TableManager.get_data(table_view)
        data.append(row)
        TableManager.set_data(table_view, data)

    @staticmethod
    def remove_last_row(table_view: QTableView):
        data = TableManager.get_data(table_view)
        if len(data):
            data.pop()
        TableManager.set_data(table_view, data)

    @staticmethod
    def clear(table_view: QTableView):
        TableManager.set_data(table_view, [])

    @staticmethod
    def get_row(table_view: QTableView):
        try:
            m_index = table_view.currentIndex()
            m_index = m_index.sibling(m_index.row(), m_index.column())
            items = m_index.data(Qt.UserRole)
            return items
        except BaseException as error:
            journal.log(__name__ + " error: " + str(error))
            return None

    @staticmethod
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

    @staticmethod
    def select_row(table_view: QTableView, row: int):
        sel_model: QItemSelectionModel = table_view.selectionModel()
        index: QModelIndex = table_view.model().sourceModel().index(row, 0)
        mode = QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
        sel_model.select(index, mode)
        table_view.setFocus()

    @staticmethod
    def get_selected_row(table_view: QTableView):
        # sel_model: QItemSelectionModel = table_view.selectionModel()
        return TableManager.get_row(table_view)
