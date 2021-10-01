"""
    Модуль содержит функции для работы с таблицей точек
"""
from PyQt5.QtWidgets import QHeaderView
from Classes.UI import funcs_table
from AesmaLib.journal import Journal


@Journal.logged
def init(window):
    """ инициализирует таблицу точек """
    display = ['flw', 'lft', 'pwr', 'eff']
    headers = ['расход\nм³/сут', 'напор\nм', 'мощность\nкВт', 'кпд\n%']
    headers_sizes = [60, 60, 80, 60]
    resizes = [QHeaderView.Stretch] * 4
    resizes[2] = QHeaderView.Fixed
    for i, val in enumerate(headers_sizes):
        window.tablePoints.setColumnWidth(i, val)
    funcs_table.create(window.tablePoints, display=display,
                        headers=headers, headers_sizes=headers_sizes,
                        headers_resizes=resizes)


def add(window, flw, lft, pwr, eff):
    """ добавление точки в таблицу """
    data = {'flw': round(flw, 1),
            'lft': round(lft, 2),
            'pwr': round(pwr, 4),
            'eff': round(eff, 1)}
    funcs_table.add_row(window.tablePoints, data)


def remove_last(window):
    """ удаление последней добавленной точки """
    funcs_table.remove_last_row(window.tablePoints)
