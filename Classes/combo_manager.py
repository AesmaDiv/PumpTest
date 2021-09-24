from re import I
from PyQt5.QtWidgets import QHeaderView, QGroupBox, QWidget, QTableView
from PyQt5.QtWidgets import QPushButton, QLineEdit, QComboBox
from PyQt5.QtCore import Qt, QRegExp, QPointF
from Classes.table_manager import TableManager

from GUI import models
from AesmaLib.journal import Journal
from AesmaLib.database import QueryParams


class ComboManager:
    @Journal.logged
    @staticmethod
    def fill(window, db_manager):
        """ инициализирует комбобоксы --> """
        ComboManager.fill_test(window, db_manager)
        ComboManager.fill_pump(window, db_manager)

    @staticmethod
    def fill_test(window, db_manager):
        """ инициализирует комбобоксы для теста --> """
        ComboManager.fill_customers(window, db_manager)
        ComboManager.fill_assembly(window, db_manager)

    @staticmethod
    def fill_pump(window, db_manager):
        """ инициализирует комбобоксы для насоса --> """
        ComboManager.fill_producers(window, db_manager)
        ComboManager.fill_types(window, db_manager)
        ComboManager.fill_serials(window, db_manager)

    @Journal.logged
    @staticmethod
    def fill_customers(window, db_manager):
        """ --> заполняет заказчик (cmbCustomer) """
        qp = QueryParams('Customers', ['ID', 'Name'])
        ComboManager.fill_combo(window.cmbCustomer, db_manager, qp)

    @Journal.logged
    @staticmethod
    def fill_assembly(window, db_manager):
        """ --> заполняет сборка (cmbAssembly) """
        qp = QueryParams('Assemblies', ['ID', 'Name'])
        ComboManager.fill_combo(window.cmbAssembly, db_manager, qp)

    @Journal.logged
    @staticmethod
    def fill_producers(window, db_manager):
        """ --> заполняет производитель (cmbProducer) """
        qp = QueryParams('Producers', ['ID', 'Name'])
        ComboManager.fill_combo(window.cmbProducer, db_manager, qp)

    @Journal.logged
    @staticmethod
    def fill_types(window, db_manager):
        """ --> заполняет типоразмер (cmbType) """
        qp = QueryParams('Types', ['ID', 'Name', 'Producer'])
        ComboManager.fill_combo(window.cmbType, db_manager, qp)

    @Journal.logged
    @staticmethod
    def fill_serials(window, db_manager):
        """ --> заполняет зав.номер (cmbSerial) """
        qp = QueryParams('Pumps', ['ID', 'Serial', 'Type'])
        ComboManager.fill_combo(window.cmbSerial, db_manager, qp)

    @staticmethod
    def fill_combo(combo: QComboBox, db_manager, query_params):
        """ инициализирует фильтр и заполняет комбобокс """
        model = models.ComboItemModel(combo)
        display = query_params.columns[1]
        data = None
        data = db_manager.get_records(query_params)
        data.insert(0, {key: None for key in query_params.columns})
        model.fill(data, display)
        combo.setModel(model)

    @staticmethod
    def filters_reset(window):
        """ сбрасывает фильт для комбобоксов насоса """
        window.cmbType.model().resetFilter()
        window.cmbSerial.model().resetFilter()

