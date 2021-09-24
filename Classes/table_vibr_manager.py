from PyQt5.QtWidgets import QHeaderView
from Classes.table_manager import TableManager
from AesmaLib.journal import Journal


class VibrationTableManager:
    @staticmethod
    @Journal.logged
    def init(window):
        """ инициализирует таблицу вибрации """
        display = ['num','vbr']
        headers = ['№','мм/с2']
        headers_sizes = [60, 80]
        resizes = [QHeaderView.Fixed, QHeaderView.Stretch]
        window.tablePoints.setColumnWidth(0, 60)
        window.tablePoints.setColumnWidth(1, 80)
        TableManager.create(window.tableVibrations, display=display,
                            headers=headers, headers_sizes=headers_sizes,
                            headers_resizes=resizes)

    @staticmethod
    def add(window, vibrations):
        """ добавление вибрации в таблицу """
        for i, vbr in enumerate(vibrations):
            data = {
                'num': i + 1,
                'vbr': round(vbr, 2)
            }
            TableManager.add_row(window.tableVibrations, data)
