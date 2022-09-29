"""
    Модуль содержит методы проверки и сохранения записей
"""
from datetime import datetime
from loguru import logger
from Classes.UI.funcs import funcs_aux

from Classes.UI.funcs.funcs_group import groupValidate
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


def saveInfo_Pump(wnd, binding: Binding, pump_: Record, do_update: bool = False) -> bool:
    """сохранение данных о насосе"""
    logger.debug(saveInfo_Pump.__doc__)
    # поля необходимые для заполнения
    need_to_validate = [
        'txtStages', 'txtLength', 'cmbConnection', 'cmbProducer',
        'cmbGroup', 'cmbMaterial', 'cmbSize', 'cmbSerial', 'cmbType'
    ]
    if not groupValidate(wnd.groupPumpInfo, need_to_validate):
        logger.warning("заполнены не все необходимые поля")
        return False
    # сохраняем информацию о типоразмере
    type_data = wnd.cmbType.currentData()
    if not type_data:
        logger.warning("не удалось сохранить данные о насос")
        return False
    if not do_update:
        pump_.clear()
    # сохраняем значения из привязанных полей
    binding.toData()
    data = dict(pump_.items())
    data['Type'] = type_data['ID']
    # записываем
    result = wnd.db_manager.writeRecord(pump_.subclass, data)
    logger.debug("данные о насосе успешно сохранены")
    return result


def findInfo_Test(wnd, order_num: str) -> tuple:
    """проверка присутствия наряд-заказа в базе"""
    logger.debug(f"{findInfo_Test.__doc__} -> {order_num}")
    test = wnd.db_manager.findRecord_Test(order_num)
    # если есть
    if test:
        result = Message.choice(
            "Внимание",
            "Запись с таким наряд-заказом "
            "уже присутствует в базе данных.\n"
            "Хотите выбрать её, обновить или создать новую?",
            ["Выбрать", "Обновить", "Отмена"]
        )
        if result < 2:
            return (test, ("select", "update")[result])
    return (None, None)


def saveInfo_Test(wnd, binding: Binding, test_: Record, do_update: bool = False) -> bool:
    """сохранение нового теста"""
    logger.debug(saveInfo_Test.__doc__)
    result = False
    # поля необходимые для заполнения
    need_to_validate = [
        'txtDateAssembled', '', 'txtLocation', 'txtShaftOut', 'txtDaysRun',
        'txtLease', 'txtShaftDiameter', 'txtWell', 'txtShaftIn', 'txtDateTime',
        'txtShaftWobb', 'txtShaftMomentum', 'txtOrderNum',
        'cmbCustomer', 'cmbSectionStatus', 'cmbSectionType', 'cmbOwner'
    ]
    if not groupValidate(wnd.groupTestInfo, need_to_validate):
        logger.warning("Заполнены не все необходимые поля")
        return result
    # сохраняем информацию об испытании
    pump_data = wnd.cmbSerial.currentData()
    if pump_data:
        if not do_update:
            test_.clear()
            test_['DateTime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif not funcs_aux.askPassword():
            logger.error("Обновление записи отменено.")
            return result
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
