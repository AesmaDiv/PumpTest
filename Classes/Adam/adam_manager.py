"""
    Модуль содержит классы для работы с Advantech ADAM 5000 TCP
"""
from PyQt5.QtCore import pyqtSignal, QObject
from .adam_5k import Adam5K, Param, SlotType
from . import adam_config as adam


class AdamManager(Adam5K):
    """ Класс для связи контроллера Adam5000TCP с интерфейсом программы """
    class Broadcaster(QObject):
        """ Класс вещателя события """
        event = pyqtSignal(dict)

    sensors = {
        'rpm': 0.0,
        'torque': 0.0,
        'pressure_in': 0.0,
        'pressure_out': 0.0,
        'flw0': 0.0,
        'flw1': 0.0,
        'flw2': 0.0
    }

    def __init__(self, host, port=502, address=1) -> None:
        super().__init__(host=host, port=port, address=address)
        self._broadcaster = AdamManager.Broadcaster()

    def dataReceived(self):
        """ ссылка на событие прибытие данных """
        return self._broadcaster.event

    def setPollingState(self, state: bool, interval=1):
        """ вкл/выкл опрос устройства """
        if state and self.connect():
            self.setInterval(interval)
            return self.setReadingState(True)
        self.setReadingState(False)
        self.disconnect()
        return False

    def setValue(self, param: Param, value: int) -> bool:
        """ установка значения для канала """
        if self.checkParams(param, value):
            self.setChannelValue(
                param.slot_type, param.slot, param.channel, value
            )
            return True
        return False

    @staticmethod
    def checkParams(params: Param, value) -> bool:
        """ проверка параметров """
        if params.slot_type in (SlotType.ANALOG, SlotType.DIGITAL):
            if 0 <= params.slot < 8 and 0 <= params.channel < 8:
                if 0 <= value <= params.dig_max:
                    return True
        return False

    def _threadTick(self):
        """ тик таймера опроса устройства """
        super()._threadTick()
        self.__readRegisters()
        self.__calculateRealValues()
        self.dataReceived().emit(self.sensors)

    def __readRegisters(self):
        """ чтение регистров """
        for key in self.sensors:
            self.sensors[key] = self.__readRegister(adam.params[key])

    def __readRegister(self, param: Param):
        """ чтение региста аналогового слота"""
        return self.getValue(param.slot_type, param.slot, param.channel)

    def __calculateRealValues(self):
        """ расчёт значений """
        for key, value in self.sensors.items():
            param = adam.params[key]
            value = param.val_rng * (value - param.offset) / param.dig_max
            self.sensors[key] = round(value, 2)
