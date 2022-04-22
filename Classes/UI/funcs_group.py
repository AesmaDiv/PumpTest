"""
    Модуль содержит функции для работы с группбоксами главного окна
"""
from PyQt5.QtWidgets import QGroupBox, QWidget, QToolButton, QPushButton
from PyQt5.QtWidgets import QLineEdit, QComboBox, QTextEdit
from PyQt5.QtCore import QRegExp
from AesmaLib.journal import Journal
from AesmaLib.message import Message


def groupDisplay(group: QGroupBox, record, log=False):
    """ отображает информацию записи в полях группы """
    Journal.log(f"{__name__}::\t заполняет поля группы {group.objectName()}")
    for name, value in record.items():
        if name in ('ID', 'Type', 'Producer'):
            continue
        item = group.findChildren(QWidget, QRegExp(name))
        if item:
            if isinstance(item[0], QLineEdit | QTextEdit):
                item[0].setText(str(value))
            elif isinstance(item[0], QComboBox):
                item[0].model().selectContains(value)
            if log:
                Journal.log(f"{item[0].objectName()} <== {value}")


def groupClear(group: QGroupBox):
    """ очищает отображаемую информацию записи в полях группы """
    Journal.log(f"{__name__}::\t очищает поля группы {group.objectName()}")
    widgets = group.findChildren(QWidget)
    for item in widgets:
        if isinstance(item, QLineEdit | QTextEdit):
            item.clear()
        elif isinstance(item, QComboBox):
            item.model().resetFilter()
            item.model().select(0)
    group.repaint()


def groupValidate(group: QGroupBox):
    """ проверяет заполнение всех полей группы """
    Journal.log(f"{__name__}::\t проверяет заполнение",
                f"всех полей группы {group.objectName()}")
    items = group.findChildren(QLineEdit) + group.findChildren(QComboBox)
    empty_fields = [
        item.toolTip() for item in items
        if (item.objectName().startswith('txt') and not item.text()) or \
        (item.objectName().startswith('cmb') and not item.currentText())
    ]
    if empty_fields:
        Message.show(
            "ВНИМАНИЕ",
            "Необходимо заполнить поля:\n->  " + "\n->  ".join(empty_fields)
        )
        return False
    return True


def groupSave(group: QGroupBox, record, keep_id=False, log=False):
    """ сохраняет информацию записи в полях группы """
    Journal.log(f"{__name__}::\t сохраняет значения",
                f"из полей группы {group.objectName()}")
    if not keep_id:
        record['ID'] = None
    for name in record.keys():
        widget = group.findChildren(QWidget, QRegExp(name))
        if widget:
            if isinstance(widget[0], QLineEdit):
                record[name] = int(widget[0].text()) \
                    if name in ('Stages', "DaysRun") \
                    else widget[0].text()
            if isinstance(widget[0], QTextEdit):
                record[name] = widget[0].toPlainText()
            elif isinstance(widget[0], QComboBox):
                item = widget[0].currentData()['ID']
                if item:
                    record[name] = item
                else:
                    text = widget[0].currentText()
                    record[name] = text if text else None
            if log:
                Journal.log(f"{widget[0].objectName()} ==> {record[name]}")


def groupLock(group: QGroupBox, state: bool):
    """ блокирует поля группы от изменений """
    Journal.log(f"{__name__}::\t"
                f"{'устанавливает' if state else 'снимает'} блокировку полей группы")
    widgets = group.findChildren(QWidget)
    for widget in widgets:
        if isinstance(widget, QLineEdit | QTextEdit):
            widget.setReadOnly(state)
        elif isinstance(widget, QComboBox | QToolButton):
            widget.setEnabled(not state)
        elif isinstance(widget, QPushButton):
            if 'Edit' in widget.objectName():
                _ = widget.show() if state else widget.hide()
            else:
                _ = widget.hide() if state else widget.show()
        if state:
            widget.clearFocus()
    group.repaint()
    group.setStyleSheet(group.styleSheet())
