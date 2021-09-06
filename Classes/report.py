"""
    Модуль описания класса протокола об испытании
"""
import os
import webbrowser
import jinja2
from .pump_classes import RecordPump, RecordTest, RecordType


class ReportInfo:
    """ Структура данных для протокола """
    pump_info: RecordPump = None
    test_info: RecordTest = None
    type_info: RecordType = None
    deltas: dict = {}


class Report:
    """ Класс протокола об испытании """
    def __init__(self, template_path, report_path):
        self.template_path = template_path
        self.report_path = report_path

    def generate_report(self, report_info: ReportInfo):
        """ Генерирование протокола """
        report = self.__load_template()
        report = self.__fill_report(report_info, report)
        self.__save_report(report)
        webbrowser.open_new_tab(self.report_path)

    def __load_template(self):
        """ загрузка html шаблона """
        loader = jinja2.FileSystemLoader(os.path.dirname(self.template_path))
        jinja_env = jinja2.Environment(loader=loader, autoescape=True)
        result = jinja_env.get_template(os.path.basename(self.template_path))
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
        }
        result = template.render(context)
        return result


    def __save_report(self, report):
        """ сохранение html файла протокола """
        with open(self.report_path, "w", encoding='utf8') as file_report:
            file_report.write(report)
            file_report.close()
