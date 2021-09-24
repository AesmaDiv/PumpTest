"""
    Модуль описания класса протокола об испытании
"""
import os, jinja2
from PyQt5.QtGui import QPageSize
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from Classes.graph_manager import GraphManager
from Classes.record import TestInfo


class Report:
    """ Класс протокола об испытании """
    def __init__(self, path_to_template: str,
                 graph_manager: GraphManager,
                 test_info: TestInfo):
        self._webview = None
        self._printer = None
        self._template_folder = path_to_template
        self._test_info = test_info
        self._graph_manager = graph_manager
        self._template_name = "template.html"
        self._report_name = "report.pdf"
        self._base_url = QUrl.fromLocalFile(path_to_template + os.path.sep)

    def generate_report(self):
        """ Генерирование протокола """
        if not self._webview:
            self.__init_printer()
        self.__create_graph_image()
        report = self.__create_report()
        self.__print_report(report)

    def __init_printer(self):
        """ инициализация представления и принтера при первом запросе """
        self._webview = QWebEngineView()
        self._printer = QPrinter(QPrinter.ScreenResolution)
        self._printer.setOutputFormat(QPrinter.NativeFormat)
        self._printer.setPageSize(QPageSize(QPageSize.A4))

    def __create_graph_image(self):
        """ сохранение графика испытания в jpg"""
        img_size = QSize(794, 450)
        path_to_img = os.path.join(self._template_folder, "graph_image.jpg")
        self._graph_manager.switch_palette('report')
        self._graph_manager.render_to_image(img_size, path_to_img)
        self._graph_manager.switch_palette('application')

    def __create_report(self):
        """ создание web страницы протокола """
        result = self.__load_template()
        result = self.__fill_report(result)
        return result

    def __print_report(self, report):
        """ печать протокола испытания """
        self._webview.setZoomFactor(1)
        self._webview.setHtml(report, baseUrl=self._base_url)
        if QPrintDialog(self._printer).exec_():
            print("Report\t\t->отправка протокола на печать")
            self._webview.page().print(self._printer, self.__on_printed)

    def __on_printed(self, result: bool):
        """ callback вызова печати """
        print(f"Report\t\t->{'успех' if result else 'ошибка'}")

    def __load_template(self):
        """ загрузка html шаблона """
        loader = jinja2.FileSystemLoader(self._template_folder)
        jinja_env = jinja2.Environment(loader=loader, autoescape=True)
        result = jinja_env.get_template(self._template_name)
        return result

    def __fill_report(self, template):
        """ заполнение шаблона данными об испытании """
        context = {
            "pump_info": self._test_info.pump_,
            "test_info": self._test_info.test_,
            "type_info": self._test_info.type_,
            "delta_lft": self._test_info.dlts_['lft'],
            "delta_pwr": self._test_info.dlts_['pwr'],
            "delta_eff": self._test_info.dlts_['eff'],
        }
        result = template.render(context)
        return result
