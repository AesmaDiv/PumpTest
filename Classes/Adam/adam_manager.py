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

    def data_received(self):
        """ ссылка на событие прибытие данных """
        return self._broadcaster.event

    def set_polling_state(self, state: bool, interval=1):
        """ вкл/выкл опрос устройства """
        if state and self.connect():
            self.set_interval(interval)
            return self.set_reading_state(True)
        self.set_reading_state(False)
        self.disconnect()
        return False

    def set_value(self, param: Param, value: int) -> bool:
        """ установка значения для канала """
        if self.check_params(param, value):
            self.set_channel_value(
                param.slot_type, param.slot, param.channel, value
            )
            return True
        return False

    @staticmethod
    def check_params(params: Param, value) -> bool:
        """ проверка параметров """
        if params.slot_type in (SlotType.ANALOG, SlotType.DIGITAL):
            if 0 <= params.slot < 8 and 0 <= params.channel < 8:
                if 0 <= value < params.dig_max:
                    return True
        return False

    def _timer_tick(self):
        """ тик таймера опроса устройства """
        super()._timer_tick()
        self.__read_registers()
        self.__calculate_real_values()
        self.data_received().emit(self.sensors)

    def __read_registers(self):
        """ чтение регистров """
        for key in self.sensors:
            self.sensors[key] = self.__read_register(adam.params[key])

    def __read_register(self, param: Param):
        """ чтение региста аналогового слота"""
        return self.get_value(param.slot_type, param.slot, param.channel)

    def __calculate_real_values(self):
        """ расчёт значений """
        for key, value in self.sensors.items():
            param = adam.params[key]
            value = param.val_rng * (value - param.offset) / param.dig_max
            self.sensors[key] = round(value, 2)
