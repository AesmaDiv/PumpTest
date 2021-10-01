"""
    Модуль содержит функции для работы с таблицей вибрации
"""
from PyQt5.QtWidgets import QHeaderView
from Classes.UI import funcs_table
from AesmaLib.journal import Journal


@Journal.logged
def init(window):
    """ инициализирует таблицу вибрации """
    display = ['num','vbr']
    headers = ['№','мм/с2']
    headers_sizes = [60, 80]
    resizes = [QHeaderView.Fixed, QHeaderView.Stretch]
    window.tablePoints.setColumnWidth(0, 60)
    window.tablePoints.setColumnWidth(1, 80)
    funcs_table.create(window.tableVibrations, display=display,
                        headers=headers, headers_sizes=headers_sizes,
                        headers_resizes=resizes)

def add(window, vibrations):
    """ добавление вибрации в таблицу """
    for i, vbr in enumerate(vibrations):
        data = {
            'num': i + 1,
            'vbr': round(vbr, 2)
        }
        funcs_table.add_row(window.tableVibrations, data)
