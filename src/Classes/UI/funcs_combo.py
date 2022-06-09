"""
    Модуль содержит функции для работы с комбобоксами главного окна
"""
from PyQt5.QtWidgets import QComboBox

from Classes.UI.models import ComboItemModel
from Classes.Data.db_tables import (Customer, Producer, Type, Pump, Owner,
    Material, Size, SectionStatus, SectionType, Group, Connection)


def fillCombos(window, db_manager):
    """инициализирует комбобоксы -->"""
    fillCombos_Pump(window, db_manager, initial=True)
    fillCombos_Test(window, db_manager)


def fillCombos_Pump(window, db_manager, initial=False):
    """инициализирует комбобоксы для насоса -->"""
    default_params = ('Name', ['ID', 'Name'])
    fillComboBox(window.cmbProducer, db_manager, Producer, *default_params)
    fillComboBox(window.cmbType, db_manager, Type, 'Name', ['ID', 'Name', 'Producer'])
    fillComboBox(window.cmbSerial, db_manager, Pump, 'Serial', ['ID', 'Serial', 'Type'])
    if initial:
        fillComboBox(window.cmbGroup, db_manager, Group, *default_params)
        fillComboBox(window.cmbMaterial, db_manager, Material, *default_params)
        fillComboBox(window.cmbSize, db_manager, Size, *default_params)
        fillComboBox(window.cmbConnection, db_manager, Connection, *default_params)


def fillCombos_Test(window, db_manager):
    """инициализирует комбобоксы для теста -->"""
    default_params = ('Name', ['ID', 'Name'])
    fillComboBox(window.cmbCustomer, db_manager, Customer, *default_params)
    fillComboBox(window.cmbOwner, db_manager, Owner, *default_params)
    fillComboBox(window.cmbSectionStatus, db_manager, SectionStatus, *default_params)
    fillComboBox(window.cmbSectionType, db_manager, SectionType, *default_params)


def fillComboBox(combo, db_manager, table_class, display_key, keys):
    """инициализирует фильтр и заполняет комбобокс"""
    model = ComboItemModel(combo)
    setattr(model, 'TableClass', table_class)
    data = db_manager.getListFor(table_class, keys)
    data.insert(0, {key: None for key in keys})
    model.fill(data, display_key)
    combo.setModel(model)


def resetFilters_pumpInfo(window):
    """сбрасывает фильт для комбобоксов насоса"""
    resetFilter(window.cmbSerial)
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
