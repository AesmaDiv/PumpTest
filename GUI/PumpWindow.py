import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic


class Window(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        path = os.path.dirname(__file__)
        path += "/pumpwindow.ui"
        uic.loadUi(path, self)
        self.listView.clicked.connect(self.on_listview_clicked)

    def show(self):
        super().show()
        geometry = QtWidgets.QApplication.desktop().geometry()
        x = (geometry.width() - self.width()) / 2
        y = (geometry.height() - self.height()) / 2
        self.move(x, y)

    def fill(self, folder: str):
        model = QtGui.QStandardItemModel()
        self.listView.setModel(model)
        for f in os.walk(folder):
            item = QtGui.QStandardItem(f.replace(self.folder, ''))
            model.appendRow(item)

    def on_listview_clicked(self, index):
        item = self.listView.model().data(index, QtCore.Qt.DisplayRole)
        pump_type = self.read_type(item)
        self.__process_type(pump_type)

    def read_type(self, filename: str):
        fullpath = self.folder + filename
        try:
            f = open(fullpath, 'r')
            lines = f.readlines()
            f.close()
        except IOError:
            print("Error")
        result = self.__process_lines(lines)
        return result

    def __process_lines(self, lines: list):
        if 22 > len(lines):
            return {}
        try:
            result = {'Producer_Name': lines[0][:-1],
                      'Name': lines[1][:-1],
                      'Date': lines[2][:-1],
                      'Rpm': float(lines[3][:-1]),
                      'Nominal_Low': float(lines[4][:-1]),
                      'Nominal_Opt': float(lines[5][:-1]),
                      'Nominal_High': float(lines[6][:-1])}
            flows = {}
            lifts = {}
            powers = {}
            max_flow = float(lines[7][:-1])
            for i in range(7):
                flows[i] = round(float(i) * max_flow / 6.0, 4)
                lifts[i] = round(float(lines[i + 8][:-1]), 4)
                powers[i] = round(float(lines[i + 15][:-1]), 4)
            result['Flows_String'] = ','.join(map(str, flows.values()))
            result['Lifts_String'] = ','.join(map(str,  lifts.values()))
            result['Powers_String'] = ','.join(map(str, powers.values()))
            return result
        except:
            return {}

    def __process_type(self, pump_type: dict):
        pass
