"""
    Модуль содержит функции для работы с группбоксами главного окна
"""
from loguru import logger

from PyQt6.QtWidgets import QGroupBox, QWidget, QToolButton, QPushButton
from PyQt6.QtWidgets import QLineEdit, QComboBox, QTextEdit, QTableView
from PyQt6.QtCore import QRegularExpression

from AesmaLib.message import Message


def groupDisplay(group: QGroupBox, record):
    """отображает информацию записи в полях группы"""
    logger.debug(f"заполняет поля группы {group.objectName()}")
    for name, value in record.items():
        if name in ('ID', 'Type', 'Producer'):
            continue
        item = group.findChildren(QWidget, QRegularExpression(name))
        if item:
            if isinstance(item[0], QLineEdit | QTextEdit):
                item[0].setText(str(value))
            # elif isinstance(item[0], QComboBox):
            #     item[0].model().selectContains(value)
            # logger.debug(f"{item[0].objectName()} <== {value}")


def groupClear(group: QGroupBox):
    """очищает отображаемую информацию записи в полях группы"""
    logger.debug(f"очищает поля группы {group.objectName()}")
    widgets = group.findChildren(QWidget)
    for item in widgets:
        if isinstance(item, QLineEdit | QTextEdit):
            item.clear()
        elif isinstance(item, QComboBox):
            item.setCurrentIndex(0)
            item.model().select(0)
            item.model().resetFilter()
    group.repaint()


def groupValidate(group: QGroupBox, names: list):
    """проверяет заполнение всех полей группы"""
    logger.debug(f"проверяет заполнение всех полей группы {group.objectName()}")
    # items = group.findChildren(QLineEdit) + group.findChildren(QComboBox)
    # names = list(map(lambda i: i.objectName(), items))
    # print(names)
    empty_fields = []
    for name in names:
        if name.startswith('txt'):
            widget: QLineEdit = group.findChild(QLineEdit, name)
            if widget and not widget.text():
                empty_fields.append(widget.toolTip())
        if name.startswith('cmb'):
            widget: QComboBox = group.findChild(QComboBox, name)
            if widget and not widget.currentText():
                empty_fields.append(widget.toolTip())
    if empty_fields:
        Message.show(
            "ВНИМАНИЕ",
            "Необходимо заполнить поля:\n->  " + "\n->  ".join(empty_fields)
        )
        return False
    return True


def groupSave(group: QGroupBox, record, keep_id=False):
    """сохраняет информацию записи в полях группы"""
    logger.debug(f"сохраняет значения из полей группы {group.objectName()}")
    if not keep_id:
        record['ID'] = None
    for name in record.keys():
        widget = group.findChildren(QWidget, QRegularExpression(name))
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
            logger.debug(f"{widget[0].objectName()} ==> {record[name]}")


def groupLock(group: QGroupBox, state: bool):
    """блокирует поля группы от изменений"""
    logger.debug(f"{'устанавливает' if state else 'снимает'} блокировку полей группы {group.objectName()}")
    widgets = group.findChildren(QWidget)
    for widget in widgets:
        if isinstance(widget, QLineEdit | QTextEdit):
            widget.setReadOnly(state)
        elif isinstance(widget, QComboBox | QToolButton | QTableView):
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
