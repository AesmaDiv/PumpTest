"""
    Модуль содержит функции для работы с комбобоксами главного окна
"""
from AesmaLib.journal import Journal
from Classes.UI import models
from Classes.Data.alchemy_tables import Assembly, Customer, Producer, Type, Pump


@Journal.logged
def fill_combos(window, db_manager):
    """ инициализирует комбобоксы --> """
    fill_combos_test(window, db_manager)
    fill_combos_pump(window, db_manager)


def fill_combos_test(window, db_manager):
    """ инициализирует комбобоксы для теста --> """
    fill_combo_customers(window, db_manager)
    fill_combo_assembly(window, db_manager)


def fill_combos_pump(window, db_manager):
    """ инициализирует комбобоксы для насоса --> """
    fill_combo_producers(window, db_manager)
    fill_combo_types(window, db_manager)
    fill_combo_serials(window, db_manager)


@Journal.logged
def fill_combo_customers(window, db_manager):
    """ --> заполняет заказчик (cmbCustomer) """
    # qp = QueryParams('Customers', ['ID', 'Name'])
    # fill_combo(window.cmbCustomer, db_manager, qp)
    fill_combobox(window.cmbCustomer, db_manager, Customer, ['ID', 'Name'])


@Journal.logged
def fill_combo_assembly(window, db_manager):
    """ --> заполняет сборка (cmbAssembly) """
    # qp = QueryParams('Assemblies', ['ID', 'Name'])
    # fill_combo(window.cmbAssembly, db_manager, qp)
    fill_combobox(window.cmbAssembly, db_manager, Assembly, ['ID', 'Name'])


@Journal.logged
def fill_combo_producers(window, db_manager):
    """ --> заполняет производитель (cmbProducer) """
    # qp = QueryParams('Producers', ['ID', 'Name'])
    # fill_combo(window.cmbProducer, db_manager, qp)
    fill_combobox(window.cmbProducer, db_manager, Producer, ['ID', 'Name'])


@Journal.logged
def fill_combo_types(window, db_manager):
    """ --> заполняет типоразмер (cmbType) """
    # qp = QueryParams('Types', ['ID', 'Name', 'Producer'])
    # fill_combo(window.cmbType, db_manager, qp)
    fill_combobox(window.cmbType, db_manager, Type, ['ID', 'Name', 'Producer'])


@Journal.logged
def fill_combo_serials(window, db_manager):
    """ --> заполняет зав.номер (cmbSerial) """
    # qp = QueryParams('Pumps', ['ID', 'Serial', 'Type'])
    # fill_combo(window.cmbSerial, db_manager, qp)
    fill_combobox(window.cmbSerial, db_manager, Pump, ['ID', 'Serial', 'Type'])


def fill_combo(combo, db_manager, query_params):
    """ инициализирует фильтр и заполняет комбобокс """
    model = models.ComboItemModel(combo)
    display = query_params.columns[1]
    data = None
    data = db_manager.get_records(query_params)
    data.insert(0, {key: None for key in query_params.columns})
    model.fill(data, display)
    combo.setModel(model)


def fill_combobox(combo, db_manager, table_class, fields):
    """ инициализирует фильтр и заполняет комбобокс """
    model = models.ComboItemModel(combo)
    data = db_manager.get_list_for(table_class, fields)
    data.insert(0, {key: None for key in fields})
    model.fill(data, fields[1])
    combo.setModel(model)


def filters_reset(window):
    """ сбрасывает фильт для комбобоксов насоса """
    window.cmbType.model().resetFilter()
    window.cmbSerial.model().resetFilter()


def select_contains(combo, condition):
    if not combo.model().check_already_selected(condition):
        combo.model().select_contains(condition)
