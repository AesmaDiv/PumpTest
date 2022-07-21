"""
    Модуль содержит функцию и класс привязки значений из переданного словаря (data)
    к одноименным полям интерфейса переданного родителя (parent)
"""
from loguru import logger

from PyQt5.QtCore import QVariant, QRegExp
from PyQt5.QtWidgets import QWidget, QLineEdit, QTextEdit, QComboBox


def bind(objectName: str, propertyName: str):
    """создание привязки к свойству виджета"""
    def _getter(self):
        return self.findChild(QWidget, objectName).property(propertyName)
    def _setter(self, value):
        self.findChild(QWidget, objectName).setProperty(propertyName, QVariant(value))
    return property(fget=_getter, fset=_setter)


class Binding:
    """Класс привязки данных об испытании к полям интерфейса"""
    def __init__(self, parent, data):
        self.parent = parent
        self.data = data
        self.bindings = {}

    def generate(self):
        """генерация привязок к значениям полей"""
        obj_name = self.parent.objectName()
        data_name = self.data.__class__.__name__
        logger.debug(f"генерация привязок полей {obj_name} к {data_name}")
        classes = (QLineEdit, QTextEdit, QComboBox)
        widgets = self.parent.findChildren(classes, QRegExp('[(txt)(cmb)]'))
        widgets = list(filter(lambda item: item.objectName()[3:] in self.data.keys(), widgets))
        for widget in widgets:
            obj_name = widget.objectName()
            name = obj_name[3:]
            if name in ('Producer', 'Type'):
                continue
            prp_name = 'text'
            if isinstance(widget, QTextEdit):
                prp_name = 'plainText'
            if isinstance(widget, QComboBox):
                prp_name = 'currentIndex'
                # исключительные случаи
                if name == 'Serial':
                    prp_name = 'currentText'
            # setattr(self, name, )
            self.bindings.update({name: bind(obj_name, prp_name)})

    def toWidgets(self):
        """запись из данных в поля"""
        for name, binding in self.bindings.items():
            binding.fset(self.parent, self.data[name])

    def toData(self):
        """запись из полей в данные"""
        for name, binding in self.bindings.items():
            self.data[name] = binding.fget(self.parent)

    def getValue(self, name):
        """возвращает значение из привязанного виджета"""
        if name in self.bindings:
            return self.bindings[name].fget(self.parent)
        return None
