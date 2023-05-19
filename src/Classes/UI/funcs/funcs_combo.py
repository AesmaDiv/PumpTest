"""
    Модуль содержит функции для работы с комбобоксами главного окна
"""
from PyQt6.QtWidgets import QComboBox

from Classes.UI.models import ComboItemModel
from Classes.Data.db_tables import (Customer, Producer, Test, Type, Owner,
    Material, Size, SectionStatus, SectionType, Party, Connection)


def fillCombos(window, db_manager, initial=True):
    """инициализирует комбобоксы -->"""
    fillCombos_Pump_Producer(window, db_manager)
    fillCombos_Pump_Type(window, db_manager)
    if initial:
        defaults = ('Name', ['ID', 'Name'])
        fillComboBox(window.cmbParty, db_manager, Party, *defaults)
        fillComboBox(window.cmbMaterial, db_manager, Material, *defaults)
        fillComboBox(window.cmbSize, db_manager, Size, *defaults)
        fillComboBox(window.cmbConnection, db_manager, Connection, *defaults)
    fillComboBox(window.cmbCustomer, db_manager, Customer, *defaults)
    fillComboBox(window.cmbOwner, db_manager, Owner, *defaults)
    fillComboBox(window.cmbSectionStatus, db_manager, SectionStatus, *defaults)
    fillComboBox(window.cmbSectionType, db_manager, SectionType, *defaults)


def fillCombos_Pump_Producer(window, db_manager):
    """инициализирует комбобокс для производителей"""
    fillComboBox(window.cmbProducer, db_manager, Producer, 'Name', ['ID', 'Name'])


def fillCombos_Pump_Type(window, db_manager):
    """инициализирует комбобокс для типоразмеров"""
    fillComboBox(window.cmbType, db_manager, Type, 'Name', ['ID', 'Name', 'Producer'])


def fillComboBox(combo, db_manager, table_class, display_key, keys, sort_key=""):
    """инициализирует фильтр и заполняет комбобокс"""
    model = ComboItemModel(combo)
    setattr(model, 'TableClass', table_class)
    unsorted = db_manager.getListFor(table_class, keys)
    data = sorted(unsorted, key=lambda item: item[sort_key]) if sort_key else unsorted
    data.insert(0, {key: None for key in keys})
    model.fill(data, display_key)
    combo.setModel(model)


def resetFilters_pumpInfo(window):
    """сбрасывает фильт для комбобоксов насоса"""
    # resetFilter(window.cmbSerial)
    resetFilter(window.cmbType)


def resetFilter(combo):
    """сбрасывает фильт для комбобокса"""
    combo.setCurrentIndex(-1)
    combo.model().resetFilter()


def filterByCondition(combo, condition):
    """фильтрация элементов, удовлетворяющих условию"""
    if not combo.model().checkAlreadySelected(condition):
        combo.model().applyFilter(condition)


def selectContains(combo, condition):
    """выбор элемента, удовлетворяющего условию"""
    if not combo.model().checkAlreadySelected(condition):
        combo.model().selectContains(condition)


def findItem(combo: QComboBox, value: str) -> int:
    """поиск элемента, содержащего значение"""
    index = combo.findText(value)
    return index


def checkExists(combo: QComboBox, value: str) -> bool:
    """проверка на наличие элемента, содержащего значение"""
    return findItem(combo, value) >= 0


def addItem(combo: QComboBox, db_manager, data: dict, check=False) -> int:
    """добавление элемента"""
    display_key = combo.model().display
    if check:
        index = findItem(combo, data[display_key])
        if index >= 0:
            return index
    table_class = getattr(combo.model(), 'TableClass')
    new_id = db_manager.createRecord(table_class, data)
    data.update({'ID': new_id})
    combo.addItem(data[display_key], data)
    return combo.count() - 1

def checkAddAndSelect(combo: QComboBox, db_manager):
    """проверка присутствия (добавление) и выбор элемента"""
    value = combo.currentText()
    index = findItem(combo, value)
    if index == -1:
        index = addItem(combo, db_manager, {'Name': value})
    combo.setCurrentIndex(index)
