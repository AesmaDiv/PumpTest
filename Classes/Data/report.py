"""
    Модуль описания класса протокола об испытании
"""
import os
from matplotlib.cbook import delete_masked_points
import numpy as np
from jinja2 import FileSystemLoader, Environment
from jinja2.exceptions import  UndefinedError, TemplateSyntaxError
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
        self._webview = None
        self._printer = None
        self._context = None
        self._template_folder = template_folder
        self._db_manager = data_manager
        self._graph_manager = graph_manager
        self._path_to_img = os.path.join(
            self._template_folder,
            self._NAMES["image"]
        )
        self._base_url = QUrl.fromLocalFile(self._template_folder + os.path.sep)

    @Journal.logged
    def print(self, parent):
        """ Генерирование протокола """
        if not self._printer:
            self._initPrinter()
        page = self.createWeb()
        webview = QWebEngineView(parent=parent)
        webview.show()
        webview.setZoomFactor(1)
        webview.setBaseSize(3508, 2480)
        webview.setHtml(page, QUrl("file://"))
        if QPrintDialog(self._printer).exec_():
            print("Report\t\t->отправка протокола на печать")
            page = webview.page()
            page.print(self._printer, self._onPrinted)
        self._removeGraphImage()

    def createWeb(self):
        """ создание web страницы протокола """
        try:
            self._createGraphImage()
            result = self._loadTemplate()
            result = result.render(self._context if self._context else self.createContext())
        except (TypeError, UndefinedError, TemplateSyntaxError) as err:
            print("Protocol::createWeb error:\t", err.message)
            result = ""
        return result

    def createContext(self):
        """ создание контекста для заполнение шаблона данными об испытании """
        td = self._db_manager.testdata
        self._addNamesForIDs(td)
        point_tst = self._getPointsForTest()
        point_rng = self._getPointsForRanges()
        point_tst = self._insertsPoints(point_tst, point_rng)
        point_etl = self._getPointsForEtalon(point_tst)
        deltas = self._getDeltas()
        vibration = self._getMaxVibration()
        efficiency = self._getEfficiency(td.pump_.SizeName, point_rng)
        self._context = {
            "info_pump": td.pump_,
            "info_test": td.test_,
            "info_type": td.type_,
            "point_tst": point_tst,
            "point_etl": point_etl,
            "deltas": deltas,
            "vibration": vibration,
            "efficiency": efficiency,
            "limits": self._LIMITS
        }
        return self._context

    def _initPrinter(self):
        """ инициализация представления и принтера при первом запросе """
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

    def _removeGraphImage(self):
        if os.path.exists(self._path_to_img):
            os.remove(self._path_to_img)

    @staticmethod
    def _onPrinted(result: bool):
        """ callback вызова печати """
        print(f"Report\t\t->{'успех' if result else 'ошибка'}")

    def _print(self, report):
        """ печать протокола испытания """
        self._webview.setZoomFactor(1)
        self._webview.setHtml(report, baseUrl=self._base_url)
        if QPrintDialog(self._printer).exec_():
            print("Report\t\t->отправка протокола на печать")
            self._webview.page().print(self._printer, self._onPrinted)
        os.remove(self._path_to_img)

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
        result = {
                'flw': None,
                'lft': None,
                'pwr': None,
                'eff': None,
                'vbr': None,
                'wob': None,
                'mom': None
        }
        point_dlt = self._getDeltaList(list(result.keys())[1:4])
        if point_dlt:
            # транспонирование массивов значений
            point_dlt = np.array(point_dlt).T.tolist()
            tst = self._db_manager.testdata.test_
            # заполнение результата
            result.update({
                'flw': self._getOptimalDelta(),
                'lft': max(point_dlt[1], key=abs),
                'pwr': max(point_dlt[2], key=abs),
                'eff': max(point_dlt[3], key=abs),
                'vbr': max(tst.values_vbr) if tst.values_vbr else 0.0,
                'wob': tst['ShaftWobb'],
                'mom': tst['ShaftMomentum']
            })
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
                round(t.Flw, 2),
                round(100.0 * (-1 + t.Lft / e.Lft), 2),
                round(100.0 * (-1 + t.Pwr / e.Pwr), 3),
                round(t.Eff - e.Eff, 2)
            ]
            result = [func(t,e) for t,e in zip(point_tst, point_etl)]
        return result

    def _getOptimalDelta(self) -> float:
        """ получение отклонения оптимальной подачи """
        result = 0.0
        chart = self._graph_manager.getChart("tst_eff")
        if chart:
            curve = chart.regenerateCurve()
            if len(curve):
                flw_nom = float(self._db_manager.testdata.type_['Nom'])
                flw_opt = self._getEffMaxPoint(curve)[0]
                result = 100.0 * (flw_opt / flw_nom - 1)
        return round(result, 2)

    def _getEffMaxPoint(self, curve) -> tuple:
        """ получение точки с максимальным КПД """
        index = np.where(curve['y'] == max(curve['y']))[0]
        x = float(curve['x'][index])
        y = float(curve['y'][index])
        return (x, y)

    def _getMaxVibration(self):
        vbr = self._db_manager.testdata.test_.values_vbr
        return max(vbr) if vbr else 0.0

    def _getEfficiency(self, size: str, points_rng) -> str:
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
