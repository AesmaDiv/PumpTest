"""
    Модуль содержит методы проверки и сохранения записей
"""
from loguru import logger

from Classes.UI.funcs_group import groupValidate
from Classes.UI.bindings import Binding
from Classes.Data.record import Record

from AesmaLib.message import Message


def checkExists_Type(wnd, type_name: str) -> int:
    """проверка присутствия типоразмера"""
    logger.debug(f"{checkExists_Type.__doc__} {type_name}")
    index = wnd.cmbType.findText(type_name)
    return index >= 0


def addNew_Type(wnd, type_name: str, producer_name: str=""):
    """запрос на добавление нового типоразмера"""
    logger.debug(f"{addNew_Type.__doc__} {type_name}")
    if Message.ask("Внимание", "Типоразмер не найден. Добавить новый?"):
        data = {
            'ProducerName': producer_name,
            'TypeName': type_name
        }
        wnd.signalTypeChangeRequest.emit(data)


def findInfo_Pump(wnd, serial: str, type_id: int) -> dict:
    """проверка присутствия насоса в базе"""
    logger.debug(f"{findInfo_Pump.__doc__} {serial}")
    pump = wnd.db_manager.findRecord_Pump(serial, type_id)
    # если есть - выбираем
    if pump and Message.ask(
        "Внимание",
        "Насос с таким заводским номером "
        "уже присутствует в базе данных.\n"
        "Хотите выбрать его?",
        "Выбрать", "Отмена"
        ):
        return pump
    return None


def saveInfo_Pump(wnd, binding: Binding, pump_: Record) -> bool:
    """сохранение данных о насосе"""
    logger.debug(saveInfo_Pump.__doc__)
    result = False
    if not groupValidate(wnd.groupPumpInfo):
        logger.warning("Заполнены не все необходимые поля")
        return result
    # сохраняем информацию о типоразмере
    type_data = wnd.cmbType.currentData()
    if type_data:
        pump_.clear()
        binding.toData()    # сохраняем значения из привязанных полей
        data = dict(pump_.items())
        data['Type'] = type_data['ID']
        # записываем
        result = wnd.db_manager.writeRecord(pump_.subclass, data)
    logger.debug({
        True: "данные о насосе успешно сохранены",
        False: "не удалось сохранить данные о насосе"
    }[result])
    return result


def findInfo_Test(wnd, order_num: str) -> dict:
    """проверка присутствия наряд-заказа в базе"""
    logger.debug(f"{findInfo_Test.__doc__} -> {order_num}")
    test = wnd.db_manager.findRecord_Test(order_num)
    # если есть - выбираем
    if test and Message.ask(
        "Внимание",
        "Запись с таким наряд-заказом "
        "уже присутствует в базе данных.\n"
        "Хотите выбрать её или создать новую?",
        "Выбрать", "Отмена"
        ):
        return test
    return None


def saveInfo_Test(wnd, binding: Binding, test_: Record) -> bool:
    """сохранение нового теста"""
    logger.debug(saveInfo_Test.__doc__)
    result = False
    if not groupValidate(wnd.groupTestInfo):
        logger.warning("Заполнены не все необходимые поля")
        return result
    # сохраняем информацию об испытании
    pump_data = wnd.cmbSerial.currentData()
    if pump_data:
        test_.clear()
        binding.toData()    # сохраняем значения из привязанных полей
        data = dict(test_.items())
        data['Pump'] = pump_data['ID']
        # записываем
        result = wnd.db_manager.writeRecord(test_.subclass, data)
    logger.debug({
        True: "данные об испытании успешно сохранены",
        False: "не удалось сохранить данные об испытании"
    }[result])
    return result
