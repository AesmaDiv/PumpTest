"""
    Модуль описания класса протокола об испытании
"""
from cgitb import reset
import os
import numpy as np
from jinja2 import FileSystemLoader, Environment
from jinja2.exceptions import *
from PyQt5.QtGui import QPageSize
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from Classes.Data.record import Record, Point
from Classes.Graph.graph_manager import GraphManager
from Classes.Data.data_manager import DataManager, TestData
from Classes.Data.alchemy_tables import *
from AesmaLib.journal import Journal


class Report:
    """ Класс протокола об испытании """
    _NAMES = {
        "template": "template.html",
        "report": "report.pdf",
        "image": "graph_image.jpg"
    }

    def __init__(self, template_folder, graph_manager: GraphManager, data_manager: DataManager):
        self._webview = None
        self._printer = None
        self._template_folder = template_folder
        self._db_manager = data_manager
        self._graph_manager = graph_manager
        self._path_to_img = os.path.join(
            self._template_folder,
            self._NAMES["image"]
        )
        self._base_url = QUrl.fromLocalFile(self._template_folder + os.path.sep)

    @Journal.logged
    def print(self):
        """ Генерирование протокола """
        if not self._webview:
            self._initPrinter()
        self._print(self.createWeb())
        self._deleteGraphImage()

    def createWeb(self):
        """ создание web страницы протокола """
        try:
            self._createGraphImage()
            result = self._loadTemplate()
            result = self._fill(result)
        except (TypeError, UndefinedError, TemplateSyntaxError) as err:
            print("Protocol::createWeb error:\t", err)
            result = ""
        return result

    def _initPrinter(self):
        """ инициализация представления и принтера при первом запросе """
        self._webview = QWebEngineView()
        self._printer = QPrinter(QPrinter.ScreenResolution)
        self._printer.setOutputFormat(QPrinter.NativeFormat)
        self._printer.setPageSize(QPageSize(QPageSize.A4))

    def _loadTemplate(self):
        """ загрузка html шаблона """
        loader = FileSystemLoader(self._template_folder)
        jinja_env = Environment(loader=loader, autoescape=True)
        result = jinja_env.get_template(self._NAMES["template"])
        return result

    def _createGraphImage(self):
        """ сохранение графика испытания в jpg"""
        img_size = QSize(794, 450)
        self._graph_manager.switchPalette('report')
        self._graph_manager.renderToImage(img_size, self._path_to_img)
        self._graph_manager.switchPalette('application')

    def _deleteGraphImage(self):
        if os.path.exists(self._path_to_img):
            os.remove(self._path_to_img)

    @staticmethod
    def _onPrinted(result: bool):
        """ callback вызова печати """
        print(f"Report\t\t->{'успех' if result else 'ошибка'}")

    def _fill(self, template):
        """ заполнение шаблона данными об испытании """
        self._addNamesForIDs(self._db_manager.testdata)
        point_tst = self._getPointsForTest()
        # УДАЛИТЬ -> добавление значений точек в границах раб.диапазона
        point_tst = self._insertsPoints(point_tst, self._getPointsForRanges())
        # <- УДАЛИТЬ
        point_etl = self._getPointsForEtalon(point_tst)
        #point_etl = self._insertsPoints(point_etl, self._getPointsForRanges())
        point_dlt = self._getDeltas()
        context = {
            "info_pump": self._db_manager.testdata.pump_,
            "info_test": self._db_manager.testdata.test_,
            "info_type": self._db_manager.testdata.type_,
            "point_tst": point_tst,
            "point_etl": point_etl,
            "point_dlt": point_dlt,
            "delta_lft": self._db_manager.testdata.dlts_['lft'],
            "delta_pwr": self._db_manager.testdata.dlts_['pwr'],
            "delta_eff": self._db_manager.testdata.dlts_['eff'],
        }
        result = template.render(context)
        return result

    def _addNamesForIDs(self, testdata: TestData):
        """ добавление имён полей для id полей """
        def func(info: Record, tables):
            prop_name = ""
            get_name = lambda x: x['ID'] == info[prop_name]
            for table in tables:
                prop_name = table.__name__
                if prop_name in info.keys():
                    items = self._db_manager.getListFor(table, ('ID', 'Name'))
                    name = next(filter(get_name, items), {"Name": ""}).get('Name')
                    setattr(info, f"{prop_name}Name", name)
        func(testdata.type_, (Producer, Efficiency))
        func(testdata.pump_, (Type, Group, Material, Size, Connection))
        func(testdata.test_, (Customer, Owner, SectionStatus, SectionType))

    def _getPointsForTest(self):
        """ получение точек кривой испытания """
        result = self._db_manager.testdata.test_.points
        return result

    def _insertsPoints(self, dst: list, src: list) -> list:
        """ вставка точек в массив точек """
        tst = [p.Flw for p in dst]
        rng = [p.Flw for p in src]
        indices = np.searchsorted(tst, rng)
        result = np.insert(dst, indices, src, axis=0)
        return result

    def _getPointsForRanges(self) -> list:
        """ получение точек для границ рабочей зоны """
        flows = (
            self._db_manager.testdata.type_['Min'],
            self._db_manager.testdata.type_['Nom'],
            self._db_manager.testdata.type_['Max']
        )
        return self._getPointsFor(flows, ('tst_lft', 'tst_pwr','tst_eff'))

    def _getPointsForEtalon(self, test_points: list) -> list:
        """ получение точек эталонной кривой, соответствующих кривой испытания """
        flows = [p.Flw for p in test_points]
        return self._getPointsFor(flows, ('etl_lft', 'etl_pwr','etl_eff'))

    def _getPointsFor(self, flows: list, chart_names: list) -> list:
        """ получение точек для указанных расходов и имён кривых """
        result = []
        for flw in flows:
            # фиксируем расход
            vals = [flw]
            # получаем значения для этого расхода из кривых
            for chart_name in chart_names:
                chart = self._graph_manager.getChart(chart_name)
                if chart:
                    vals.append(chart.getValueY(flw))
                # если ошибка поиска кривой, возвращаем пустой результат
                else:
                    return []
            # создаём и добавляем точку к результату
            result.append(Point(Flw=vals[0],Lft=vals[1],Pwr=vals[2],Eff=vals[3]))
        return result

    def _getDeltas(self) -> dict:
        """ получение информации об отклонениях кривых """
        keys = ('lft', 'pwr', 'eff')
        result = dict.fromkeys(keys)
        point_dlt = self._getDeltaList(keys)
        if point_dlt:
            # транспонирование массивов значений
            point_dlt = np.array(point_dlt).T.tolist()
            # заполнение результата
            for i, k in enumerate(keys):
                i += 1
                result.update({k: (min(point_dlt[i]), max(point_dlt[i]))})
        return result

    def _getDeltaList(self, names: tuple) -> list:
        """ получение массивов отклонений для указанных имён кривых """
        result = []
        # диапазон расхода в рабочей зоне
        flw_min = int(self._db_manager.testdata.type_['Min'])
        flw_max = int(self._db_manager.testdata.type_['Max'])
        flw_rng = [x for x in range(flw_min, flw_max + 1)]
        # точки для этого диапазона (тест и эталон)
        point_tst = self._getPointsFor(flw_rng, [f'tst_{name}' for name in names])
        point_etl = self._getPointsFor(flw_rng, [f'etl_{name}' for name in names])
        # расчёт отклонений
        if all((point_tst, point_etl)):
            func = lambda t, e: [
                t.Flw,
                100.0 * (-1 + t.Lft / e.Lft),
                100.0 * (-1 + t.Pwr / e.Pwr),
                t.Eff - e.Eff
            ]
            result = [func(t,e) for t,e in zip(point_tst, point_etl)]
        return result

    def _print(self, report):
        """ печать протокола испытания """
        self._webview.setZoomFactor(1)
        self._webview.setHtml(report, baseUrl=self._base_url)
        if QPrintDialog(self._printer).exec_():
            print("Report\t\t->отправка протокола на печать")
            self._webview.page().print(self._printer, self._onPrinted)
        os.remove(self._path_to_img)
