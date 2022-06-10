"""
    Модуль описывает класс окна информации о типоразмере"""
from loguru import logger

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox

from Classes.UI.funcs import funcs_combo
from Classes.Data.db_manager import DataManager
from Classes.Data.db_tables import Producer, Type, Efficiency

from AesmaLib.message import Message


class TypeWindow(QDialog):
    """Класс окна типоразмера"""
    def __init__(self, parent, path_to_gui):
        super().__init__(parent=parent)
        self._data_manager: DataManager = None
        self._is_ready = self._createGUI(path_to_gui)

    def setDataManager(self, data_manager: DataManager):
        """привязка менеджера базы данных"""
        self._data_manager = data_manager

    def showDialog(self, data: dict = None) -> bool:
        """вызов диалога создания нового типоразмера"""
        if not self._is_ready:
            logger.error("Не загружен файл графического интерфейса")
            return False
        if not self._data_manager:
            logger.error("Отсутствует привязка к менеджеру базы данных")
            return False
        self._prepareFields(data)
        while self.exec_() == QDialog.Accepted:
            if self._checkAllFilled():
                data = self._getFieldsData()
                if self._checkFieldsData(data):
                    return self.saveType(data)
        return False

    def saveType(self, type_data: dict) -> bool:
        """сохраняет информацию о типоразмере"""
        if self._is_ready:
            # если производитель не выбран, но указано его имя
            # добавляем нового и выбираем
            if not type_data['Producer'] and type_data['ProducerName']:
                type_data['Producer'] = self._data_manager.createRecord(
                    Producer,
                    {'Name': type_data.pop('ProducerName')}
                )
            # если производитель выбран
            # добавляем новый типоразмер
            if type_data['Producer']:
                result = self._data_manager.createRecord(Type, type_data)
                Message.show(
                    "УСПЕХ" if result else "ОШИБКА",
                    f"Новый типоразмер '{type_data['Name']}' добавлен" \
                        if result else "Ошибка добавление нового типоразмера"
                )
                return result
        return False

    def _createGUI(self, path_to_ui) -> bool:
        """загружает файл графического интерфейса"""
        try:
            if not uic.loadUi(path_to_ui, self):
                logger.error("Не удалось загрузить файл графического интерфейса")
                return False
            return True
        except IOError as error:
            logger.error("\tОшибка загрузки файла графического интерфейса")
            logger.error(error.strerror)
        return False

    def _prepareFields(self, data: dict):
        """подготовка списка производителей и типоразмера"""
        self._clearFields()
        funcs_combo.fillComboBox(self.cmbProducer, self._data_manager,
                                 Producer, 'Name', ['ID', 'Name'])
        funcs_combo.fillComboBox(self.cmbEfficiency, self._data_manager,
                                 Efficiency, 'Name', ['ID', 'Name'])
        self.cmbProducer.lineEdit().setObjectName("txtProducerName")
        if data:
            # выбор производителя как в основном окне
            index = self.cmbProducer.findText(data['ProducerName'])
            self.cmbProducer.setCurrentIndex(index)
            # перенос имени типоразмера из основного окна
            self.txtName.setText(data['TypeName'])

    def _clearFields(self):
        """очистка полей"""
        self.cmbProducer.clear()
        self.cmbEfficiency.clear()
        for item in self.findChildren(QLineEdit):
            item.setText("")

    def _checkAllFilled(self) -> bool:
        """проверка на заполнение всех полей"""
        # список пустых полей
        empty = []
        for item in self.findChildren((QLineEdit, QComboBox)):
            if isinstance(item, QLineEdit) and item.text():
                continue
            if isinstance(item, QComboBox) and item.currentText():
                continue
            empty.append(item.toolTip())
        # отображение списка пустых полей
        if empty:
            msg = ("\n->").join(empty)
            msg = f"Необходимо заполнить следующие поля:\n{msg}"
            Message.show("Внимание", msg)
            return False
        return True

    def _getFieldsData(self) -> dict:
        """получение значений из полей"""
        # производитель и энергоэффективность из комбобоксов
        result = {
            'Producer': self.cmbProducer.currentData()['ID'],
            'Efficiency': self.cmbEfficiency.currentData()['ID']
        }
        # остальные из текстовых полей
        result.update({
            item.objectName().replace("txt", ""): \
                item.text() for item in self.findChildren(QLineEdit)
        })
        return result

    def _checkFieldsData(self, data: dict) -> bool:
        """проверка значений"""
        if not self._checkProducer(data):
            return False
        if not self._checkNumeric(data):
            return False
        if not self._checkPoints(data):
            return False
        return True

    @staticmethod
    def _checkProducer(data: dict) -> bool:
        """проверка производителя"""
        if not isinstance(data['Producer'], int):
            Message.show('ОШИБКА', 'Неверно указан производитель')
            return False
        return True

    def _checkNumeric(self, data: dict) -> bool:
        """проверка числовых значений"""
        for name in ('Rpm', 'Min', 'Nom', 'Max'):
            if not data[name].isnumeric():
                elem = self.findChild(QLabel, f'lbl{name}')
                if elem:
                    name = elem.text()
                Message.show('ОШИБКА', f'Поле {name} должно содержать число')
                return False
        return True

    @staticmethod
    def _checkPoints(data: dict) -> bool:
        """проверка корректности и длины массивов точек"""
        try:
            vals_flw = list(map(float, data['Flows'].split(',')))
            vals_lft = list(map(float, data['Lifts'].split(',')))
            vals_pwr = list(map(float, data['Powers'].split(',')))
            if not len(vals_flw) == len(vals_lft) == len(vals_pwr):
                Message.show('ОШИБКА', 'Кол-во значений в полях точек не совпадает')
                return False
        except (TypeError, ValueError):
            Message.show('ОШИБКА', 'Неверный формат в полях точек')
            return False
        return True
