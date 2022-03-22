from timeit import timeit
import os


string_to_parce = '''
from typing import List
import math
import numpy as np
from scipy.interpolate import make_interp_spline
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import Qt
from AesmaLib.GraphWidget.axis import Axis
from AesmaLib.journal import Journal
'''
imports = [x for x in string_to_parce.split('\n') if x]
result = {x: timeit(x, number=1) for x in imports}
result = dict(sorted(result.items(), key=lambda x: x[1]))
for k,v in result.items():
    print(f'{k}\t\t{v}')

# code = """
# import os
# import sys
# from PyQt5.QtWidgets import QApplication
# from Classes.UI.wnd_main import MainWindow


# ROOT = os.path.dirname(__file__)
# PATHS = {
#     'DB': os.path.join(ROOT, 'Files/pump.sqlite'),  # путь к файлу базы данных
#     'WND': os.path.join(ROOT, 'Files/mainwindow.ui'),  # путь к файлу GUI
#     'TYPE': os.path.join(ROOT, 'Files/pumpwindow.ui'),  # путь к файлу GUI
#     'TEMPLATE': os.path.join(ROOT, 'Files/report')  # путь к шаблону протокола
# }

# app = QApplication(sys.argv)
# app.setStyle("Fusion")

# wnd = MainWindow(PATHS)
# """
# print(timeit(code, number=1))