"""
    Модуль описания класса протокола об испытании
"""
import os, jinja2
from PyQt5.QtGui import QPageSize

from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from GUI.pump_graph import PumpGraph
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from .pump_classes import RecordPump, RecordTest, RecordType


class ReportInfo:
    """ Структура данных для протокола """
    pump_graph = None
    path_graph = ""
    pump_info: RecordPump = None
    test_info: RecordTest = None
    type_info: RecordType = None
    deltas: dict = {}


class Report:
    """ Класс протокола об испытании """
    def __init__(self, path_to_template):
        self._webview = None
        self._printer = None
        self._template_folder = path_to_template
        self._template_name = "template.html"
        self._report_name = "report.pdf"
        self._base_url = QUrl.fromLocalFile(path_to_template + os.path.sep)

    def generate_report(self, report_info: ReportInfo):
        """ Генерирование протокола """
        if not self._webview:
            self.__init_printer()
        self.__create_graph_image(report_info)
        report = self.__create_report(report_info)
        self.__print_report(report)

    def __init_printer(self):
        """ инициализация представления и принтера при первом запросе """
        self._webview = QWebEngineView()
        self._printer = QPrinter(QPrinter.ScreenResolution)
        self._printer.setOutputFormat(QPrinter.NativeFormat)
        self._printer.setPageSize(QPageSize(QPageSize.A4))

    def __create_graph_image(self, report_info: PumpGraph):
        """ сохранение графика испытания в jpg"""
        img_size = QSize(794, 450)
        path_to_img = os.path.join(self._template_folder, "graph_image.jpg")
        report_info.pump_graph.switch_palette('report')
        report_info.pump_graph.render_to_image(img_size, path_to_img)
        report_info.pump_graph.switch_palette('application')

    def __create_report(self, report_info):
        """ создание web страницы протокола """
        result = self.__load_template()
        result = self.__fill_report(report_info, result)
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

    def __fill_report(self, report_info, template):
        """ заполнение шаблона данными об испытании """
        context = {
            "pump_info": report_info.pump_info,
            "test_info": report_info.test_info,
            "type_info": report_info.type_info,
            "delta_lft": report_info.deltas['lft'],
            "delta_pwr": report_info.deltas['pwr'],
            "delta_eff": report_info.deltas['eff'],
            "path_graph": report_info.path_graph,
        }
        result = template.render(context)
        return result
