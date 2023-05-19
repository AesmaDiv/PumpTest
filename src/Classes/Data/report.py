"""
    Модуль описания класса протокола об испытании
"""
import asyncio
import os
import numpy as np
from loguru import logger
from jinja2 import FileSystemLoader, Environment
from jinja2.exceptions import  UndefinedError, TemplateSyntaxError

from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtCore import QSize, QUrl, QObject, QPoint, QMarginsF
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QPainter, QPageLayout, QPageSize

from Classes.Data.record import Record, Point, TestData
from Classes.Graph.graph_manager import GraphManager, ChartType
from Classes.Data.db_manager import DataManager
from Classes.Data.db_tables import (Producer, Efficiency ,Type, Party, Material,
    Size, Connection, Customer, Owner, SectionStatus, SectionType)


class Report(QObject):
    """Класс протокола об испытании"""
    _PATH = {}
    _LIMITS = {
        'flw': (-15, 12),
        'lft': (-5, 5),
        'pwr': (-8, 8),
        'eff': (-2, 0),
        'vbr': 4.0,
        'wob': 0.3,
        'mom': 0.6
    }

    def __init__(self, template_folder, graph_manager: GraphManager, data_manager: DataManager):
        super().__init__()
        Report._PATH = {
          "root": os.path.join(template_folder, ''),
          "template": os.path.join(template_folder, "template.html"),
          "report": os.path.join(template_folder, "report.pdf"),
          "image": os.path.join(template_folder, "graph_image.jpg"),
          "logo": os.path.join(template_folder, "logo.png"),
        }
        self._graph_manager = graph_manager
        self._db_manager = data_manager
        self._template = self._loadTemplate()

    def show(self, window, testdata: TestData, size_name, webview=None):
        """отображение протокола в элементе WebEngineView"""
        logger.debug(self.show.__doc__)
        context = Report._createContext(self._graph_manager, testdata, size_name)
        Report._showContext(window, context)
        if webview:
            html = self._fillTemplate(self._template, self._graph_manager, context)
            webview.setHtml(html, QUrl.fromLocalFile(Report._PATH['root']))

    def print(self, testdata: TestData):
        """вывод протокола на печать"""
        async def print_async():
            html = await self._createHtml(testdata)
            protocol = await Report._buildProtocol(html)
            printer = await Report._initPrinter()
            if QPrintDialog(printer).exec():
                await Report._printProtocol(protocol, printer)
        asyncio.run(print_async())

    async def _createHtml(self, testdata):
        """генерирование протокола"""
        Report._addNamesForIDs(self._db_manager, testdata)
        context = Report._createContext(self._graph_manager, testdata, '-')
        result = Report._fillTemplate(self._template, self._graph_manager, context)
        return result

    @staticmethod
    async def _buildProtocol(html):
        """построение протокола"""
        logger.debug(Report._buildProtocol.__doc__)
        web = QWebEngineView()
        web.setHtml(html, QUrl.fromLocalFile(Report._PATH['root']))
        web.setZoomFactor(1)
        web.showMaximized()
        return web

    @staticmethod
    async def _initPrinter():
        """инициализация принтера"""
        logger.debug(Report._initPrinter.__doc__)
        printer = QPrinter(mode=QPrinter.PrinterMode.ScreenResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.NativeFormat)
        printer.setPageMargins(QMarginsF(10, 10, 10, 0), QPageLayout.Unit.Millimeter)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setFullPage(False)
        return printer

    @staticmethod
    async def _printProtocol(web, printer):
        """отправка протокола в принтер"""
        logger.debug(Report._printProtocol.__doc__)
        painter = QPainter(printer)
        web.render(
            painter,
            QPoint(0, 0),
            web.childrenRegion())
        painter.end()

    @staticmethod
    def _fillTemplate(template, graph_manager: GraphManager, context: dict):
        """генерирование HTML разметки протокола"""
        logger.debug(Report._fillTemplate.__doc__)
        try:
            Report._createGraphImage(graph_manager)
            result = template.render(context).replace('None', '-')
        except (TypeError, UndefinedError, TemplateSyntaxError) as err:
            logger.error(f"Protocol::createWeb error:\t{err}")
            result = ""
        return result

    @staticmethod
    def _loadTemplate():
        """загрузка html шаблона"""
        logger.debug(Report._loadTemplate.__doc__)
        loader = FileSystemLoader(Report._PATH["root"])
        jinja_env = Environment(loader=loader, autoescape=True)
        result = jinja_env.get_template("template.html")
        return result

    @staticmethod
    def _createGraphImage(graph_manager: GraphManager):
        """сохранение графика испытания в jpg"""
        logger.debug(Report._createGraphImage.__doc__)
        img_size = QSize(794, 450)
        path_to_img = os.path.join(Report._PATH["image"])
        graph_manager.switchPalette('report')
        graph_manager.renderToImage(img_size, path_to_img)
        graph_manager.switchPalette('application')

    @staticmethod
    def _createContext(graph_manager: GraphManager, testdata: TestData, size_name: str) -> dict:
        """создание контекста для заполнение шаблона данными об испытании"""
        logger.debug(Report._createContext.__doc__)
        deltas = Report._getDeltas(graph_manager, testdata)
        vibration = Report._getMaxVibration(testdata)
        point_tst = Report._getPointsForTest(testdata)
        point_rng = Report._getPointsForRanges(graph_manager, testdata)
        point_tst = Report._insertsPoints(point_tst, point_rng)
        point_etl = Report._getPointsForEtalon(graph_manager, point_tst)
        point_rng = list(filter(lambda x: x.Flw != deltas['opt'], point_rng))
        efficiency = Report._getEfficiency(size_name, point_rng)
        result = {
            "info_test": testdata.test_,
            "info_type": testdata.type_,
            "point_tst": point_tst,
            "point_etl": point_etl,
            "deltas": deltas,
            "vibration": vibration,
            "efficiency": efficiency,
            "limits": Report._LIMITS,
            "path_to_logo": Report._PATH['logo'],
            "path_to_graph": Report._PATH['image']
        }
        return result

    @staticmethod
    def _addNamesForIDs(data_manager: DataManager, testdata: TestData):
        """добавление имён полей для id полей"""
        def func(info: Record, tables: tuple):
            prop_name = ""
            for table in tables:
                prop_name = table.__name__
                if prop_name in info.keys():
                    items = data_manager.getListFor(table, ('ID', 'Name'))
                    name = next(
                        filter(lambda x: x['ID'] == info[prop_name], items),
                        {"Name": ""}
                    ).get('Name')
                    setattr(info, f"{prop_name}Name", name)
        func(testdata.type_, (Producer, Efficiency))
        func(testdata.test_,
            (Customer, Owner, SectionStatus, SectionType,
             Type, Party, Material, Size, Connection)
        )

    @staticmethod
    def _insertsPoints(dst: list, src: list) -> list:
        """вставка точек в массив точек"""
        result = []
        if dst and src:
            tst = [p.Flw for p in dst]
            rng = [p.Flw for p in src]
            indices = np.searchsorted(tst, rng)
            result = np.insert(dst, indices, src, axis=0)
        return list(result)

    @staticmethod
    def _getPointsForTest(testdata: TestData) -> list:
        """получение точек кривой испытания"""
        return testdata.test_.points

    @staticmethod
    def _getPointsForRanges(graph_manager: GraphManager, testdata: TestData) -> list:
        """получение точек для границ рабочей зоны"""
        flows = [
            testdata.type_['Min'],
            testdata.type_['Nom'],
            testdata.type_['Max'],
        ]
        if 'Opt' in testdata.dlts_.keys():
            flows.append(testdata.dlts_['Opt'])
        return Report._getPointsFor(graph_manager, sorted(flows), ChartType.TEST)

    @staticmethod
    def _getPointsForEtalon(graph_manager: GraphManager, test_points: list) -> list:
        """получение точек эталонной кривой, соответствующих кривой испытания"""
        result = []
        if all(test_points):
            flows = [p.Flw for p in test_points]
            result = Report._getPointsFor(graph_manager, flows, ChartType.ETALON)
        return result

    @staticmethod
    def _getPointsFor(graph_manager: GraphManager, flows: list, chart_type: ChartType) -> list:
        """получение точек для указанных расходов и типа кривых"""
        if not flows:
            return []
        result, charts = [], []
        # получаем кривые по типу кривых
        prefix = 'tst' if chart_type == ChartType.TEST else 'etl'
        chart_names = [f"{prefix}{name}" for name in ("_lft", "_pwr", "_eff")]
        for name in chart_names:
            chart = graph_manager.getChart(name)
            # если ошибка поиска кривой, возвращаем пустой результат
            if not chart or chart.isEmpty():
                return []
            charts.append(chart)
        # для каждого расхода получаем значения из кривых
        result = [
            Point(flw, *(chart.getValueY(flw) for chart in charts))
            for flw in flows
        ]
        return result

    @staticmethod
    def _getDeltas(graph_manager: GraphManager, testdata: TestData) -> dict:
        """получение информации об отклонениях кривых"""
        result = {
                'flw': None,
                'lft': None,
                'pwr': None,
                'eff': None,
                'vbr': None,
                'wob': None,
                'mom': None,
                'opt': None,
        }
        if point_dlt:= Report._getDeltaList(graph_manager, testdata):
            # транспонирование массивов значений
            point_dlt = np.array(point_dlt).T.tolist()
            tst = testdata.test_
            # заполнение результата
            result.update({
                'flw': Report._getOptimalDelta(graph_manager, testdata),
                'lft': max(point_dlt[1], key=abs),
                'pwr': max(point_dlt[2], key=abs),
                'eff': max(point_dlt[3], key=abs),
                'vbr': max(tst.values_vbr) if tst.values_vbr else 0.0,
                'wob': tst['ShaftWobb'],
                'mom': tst['ShaftMomentum'],
                'opt': testdata.dlts_['Opt']
            })
        return result

    @staticmethod
    def _getDeltaList(graph_manager: GraphManager, testdata: TestData) -> list:
        """получение массивов отклонений для указанных имён кривых"""
        result = []
        # диапазон расхода в рабочей зоне
        flw_min = int(testdata.type_['Min'])
        flw_max = int(testdata.type_['Max'])
        flw_rng = list(range(flw_min, flw_max + 1))
        # точки для этого диапазона (тест и эталон)
        point_tst = Report._getPointsFor(graph_manager, flw_rng, ChartType.TEST)
        point_etl = Report._getPointsFor(graph_manager, flw_rng, ChartType.ETALON)
        # расчёт отклонений
        if all((point_tst, point_etl)):
            def func(t, e):
                return [
                    round(t.Flw, 2),
                    round(100.0 * (-1 + t.Lft / e.Lft), 2),
                    round(100.0 * (-1 + t.Pwr / e.Pwr), 3),
                    round(t.Eff - e.Eff, 2)
                ]
            result = [func(t,e) for t,e in zip(point_tst, point_etl)]
        return result

    @staticmethod
    def _getOptimalDelta(graph_manager: GraphManager, testdata: TestData) -> float:
        """получение отклонения оптимальной подачи"""
        result = 0.0
        chart = graph_manager.getChart("tst_eff")
        if not chart:
            return result
        curve = chart.regenerateCurve()
        if len(curve):
            flw_nom = float(testdata.type_['Nom'])
            flw_opt = Report._getEffMaxPoint(curve)
            testdata.dlts_['Opt'] = round(flw_opt[0], 2)
            result = 100.0 * (flw_opt[0] / flw_nom - 1)
        return round(result, 2)

    @staticmethod
    def _getEffMaxPoint(curve) -> tuple:
        """получение точки с максимальным КПД"""
        index = np.where(curve['y'] == max(curve['y']))[0]
        x = float(curve['x'][index])
        y = float(curve['y'][index])
        return (x, y)

    @staticmethod
    def _getMaxVibration(testdata: TestData):
        vbr = testdata.test_.values_vbr
        return max(vbr) if vbr else 0.0

    @staticmethod
    def _showContext(window, context):
        """отображение итоговых результатов испытания"""
        lmt = context['limits']
        dlt = context['deltas']
        def color_tst(name):
            cond = dlt[name] is not None and lmt[name][0] <= dlt[name] <= lmt[name][1]
            return "green" if cond else "red"
        def color_aux(name):
            cond = dlt[name] is not None and dlt[name] <= lmt[name]
            return "green" if cond else "red"
        window.lblTestResult_1.setText(
    f"""<table width=200 cellspacing=2>
        <thead>
            <tr>
                <th width=200>параметр</th>
                <th width=70>допуск</th>
                <th width=70>данные</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Отклонение оптимальной подачи, %</td>
                <td>{lmt['flw'][0]} .. {lmt['flw'][1]}</td>
                <td style='color: {color_tst('flw')};'>{dlt['flw']}</td>
            </tr>
            <tr>
                <td>Отклонение напора, %</td>
                <td>{lmt['lft'][0]} .. {lmt['lft'][1]}</td>
                <td style='color: {color_tst('lft')};'>{dlt['lft']}</td>
            </tr>
            <tr>
                <td>Отклонение мощности, %</td>
                <td>{lmt['pwr'][0]} .. {lmt['pwr'][1]}</td>
                <td style='color: {color_tst('pwr')};'>{dlt['pwr']}</td>
            </tr>
            <tr>
                <td>Отклонение КПД, %</td>
                <td>{lmt['eff'][0]} .. {lmt['eff'][1]}</td>
                <td style='color: {color_tst('eff')};'>{dlt['eff']}</td>
            </tr>
        </tbody>
    </table>""")
        window.lblTestResult_2.setText(
    f"""<table width=200 cellspacing=2>
        <thead>
            <tr>
                <th width=200>параметр</th>
                <th width=70>допуск</th>
                <th width=70>данные</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Вибрация, мм</td>
                <td>&#8804; {lmt['vbr']}</td>
                <td style='color: {color_aux('vbr')};'>{dlt['vbr']}</td>
            </tr>
            <tr>
                <td>Радиальное биение, мм</td>
                <td>&#8804; {lmt['wob']}</td>
                <td style='color: {color_aux('wob')};'>{dlt['wob']}</td>
            </tr>
            <tr>
                <td>Момент проворота, кВт</td>
                <td>&#8804; {lmt['mom']}</td>
                <td style='color: {color_aux('mom')};'>{dlt['mom']}</td>
            </tr>
            <tr>
                <td>Энергоэффективность</td>
                <td/>
                <td style='color: black;'>{context['efficiency']}</td>
            </tr>
        </tbody>
    </table>""")

    @staticmethod
    def _getEfficiency(size: str, points_rng) -> str:
        result = '-'
        class_names = ['E1', 'E2', 'E3']
        sizes = ('2', '2А', '3', '4', '5', '5А', '6', '6А', '7А', '8')
        if size in sizes and len(points_rng) == 3:
            flw, eff = points_rng[1].Flw, points_rng[1].Eff
            efficiency = {
                sizes[0]: {
                    class_names[0]: {
                        10 <= flw <= 70: -0.00391 * flw**2 + 0.72319 * flw + 9.10455,
                        flw > 70: 0.00452 * flw + 40.3516
                    },
                    class_names[1]: {
                        10 <= flw <= 80: -0.004941 * flw**2 + 0.79723 * flw + 11.4662,
                        flw > 80: 0.00416 * flw + 43.3735
                    },
                    class_names[2]: {
                        10 <= flw <= 80: -0.00547 * flw**2 + 0.83684 * flw + 14.1897,
                        flw > 80: 0.00665 * flw + 45.9939
                    }
                },
                sizes[1]: {
                    class_names[0]: {
                        10 <= flw <= 80: -0.00529 * flw**2 + 0.872715 * flw + 9.537107,
                        flw > 80: 45
                    },
                    class_names[1]: {
                        10 <= flw <= 80: -0.00533 * flw**2 + 0.877316 * flw + 12.55602,
                        flw > 80: 0.001262 * flw + 48.27767
                    },
                    class_names[2]: {
                        10 <= flw <= 80: -0.00537 * flw**2 + 0.881918 * flw + 15.57493,
                        flw > 80: 0.002524 * flw + 51.55534
                    }
                },
                sizes[2]: {
                    class_names[0]: {
                        10 <= flw <= 80: -0.00404 * flw**2 + 0.780302 * flw + 11.49017,
                        flw > 80: 0.000708 * flw + 48.80451
                    },
                    class_names[1]: {
                        10 <= flw <= 100: -0.00415 * flw**2 + 0.794382 * flw + 14.887615,
                        flw > 100: 0.000811 * flw + 52.76892
                    },
                    class_names[2]: {
                        10 <= flw <= 100: -0.00422 * flw**2 + 0.804941 * flw + 18.32636,
                        flw > 100: 0.001622 * flw + 56.53784
                    }
                },
                sizes[3]: {
                    class_names[0]: {
                        10 <= flw <= 90: -0.00459 * flw**2 + 0.8323 * flw + 12.45975,
                        flw > 90: 0.002905 * flw + 50.49753
                    },
                    class_names[1]: {
                        10 <= flw <= 130: -0.00365 * flw**2 + 0.735273 * flw + 17.21885,
                        flw > 130: 0.025 * flw + 51.75
                    },
                    class_names[2]: {
                        10 <= flw <= 130: -0.00274 * flw**2 + 0.633 * flw + 22.18402,
                        flw > 130: 59
                    }
                },
                sizes[4]: {
                    class_names[0]: {
                        10 <= flw <= 120: -0.00362 * flw**2 + 0.74961 * flw + 14.29928,
                        flw > 120: 0.0013342 * flw + 53.4038
                    },
                    class_names[1]: {
                        10 <= flw <= 140: -0.00294 * flw**2 + 0.680823 * flw + 19.07382,
                        flw > 140: 0.000511 * flw + 58.261
                    },
                    class_names[2]: {
                        10 <= flw <= 140: -0.00294 * flw**2 + 0.68821 * flw + 22.47907,
                        flw > 140: 0.000463 * flw + 62.7852
                    }
                },
                sizes[5]: {
                    class_names[0]: {
                        10 <= flw <= 310: -1.35 * 10**-8 * flw**4 + 1.25 * 10**-5 * flw**3 - 0.00438 * flw**2 + 0.70279 * flw + 14.33537,
                        flw > 310: 0.000117 * flw + 59.90954
                    },
                    class_names[1]: {
                        10 <= flw <= 310: -1.4 * 10**-8 * flw**4 + 1.29 * 10**-5 * flw**3 - 0.004425 * flw**2 + 0.700695 * flw + 18.36764,
                        flw > 310: 0.000146 * flw + 63.88693
                    },
                    class_names[2]: {
                        10 <= flw <= 310: -1.4 * 10**-8 * flw**4 + 1.33 * 10**-5 * flw**3 - 0.004471 * flw**2 + 0.6986 * flw + 22.39991,
                        flw > 310: 0.000175 * flw + 67.86431
                    }
                },
                sizes[6]: {
                    class_names[0]: {
                        750 <= flw <= 950: -6.6 * 10**-5 * flw**2 + 0.127514 * flw + 2.1,
                        flw > 950: 63.9
                    },
                    class_names[1]: {
                        750 <= flw <= 1000: -4.7 * 10**-5 * flw**2 + 0.097586 * flw + 21.15,
                        flw > 1000: 0.001105 * flw + 70.56579
                    },
                    class_names[2]: {
                        750 <= flw <= 1000: -5.6 * 10**-5 * flw**2 + 0.11255 * flw + 11.625,
                        flw > 1000: 0.000553 * flw + 67.23289
                    }
                },
                sizes[7]: {
                    class_names[0]: {
                        125 <= flw <= 700: -4.4 * 10**-5 * flw**2 + 0.058894 * flw + 46.17326,
                        flw > 700: 0.000414 * flw + 65.95011
                    },
                    class_names[1]: {
                        125 <= flw <= 800: -2.8 * 10**-5 * flw**2 + 0.044041 * flw + 52.43149,
                        flw > 800: 0.000399 * flw + 69.68868
                    },
                    class_names[2]: {
                        125 <= flw <= 900: -1.6 * 10**-5 * flw**2 + 0.031728 * flw + 58.3441,
                        flw > 900: 0.000204 * flw + 73.69864
                    }
                },
                sizes[8]: {
                    class_names[0]: {
                        150 <= flw <= 1000: -3.1 * 10**-5 * flw**2 + 0.056908 * flw + 43.9767,
                        flw > 1000: 6.27 * 10**-5 * flw + 53.4038
                    },
                    class_names[1]: {
                        150 <= flw <= 1000: -2.5 * 10**-5 * flw**2 + 0.046211 * flw + 51.19616,
                        flw > 1000: 0.000345 * flw + 72.76365
                    },
                    class_names[2]: {
                        150 <= flw <= 1000: -1.8 * 10**-5 * flw**2 + 0.035603 * flw + 58.3657,
                        flw > 1000: 0.000599 * flw + 75.76152
                    }
                },
                sizes[9]: {
                    class_names[0]: {
                        500 <= flw <= 2400: -4.8 * 10**-6 * flw**2 + 0.021907 * flw + 49.1653,
                        flw > 2400: 0.000103 * flw + 73.60673
                    },
                    class_names[1]: {
                        500 <= flw <= 3000: -3.7 * 10**-6 * flw**2 + 0.018934 * flw + 52.7882,
                        flw > 3000: 76.5
                    },
                    class_names[2]: {
                        500 <= flw <= 2200: -3.8 * 10**-6 * flw**2 + 0.019167 * flw + 54.7894,
                        flw > 2200: 0.000148 * flw + 78.4401
                    }
                },
            }
            e1e2e3 = np.array([efficiency[size][x][True] for x in class_names])
            if any(e1e2e3):
                index = np.searchsorted(e1e2e3, [eff])[0]
                result = (['-'] + class_names)[index]
        return result
