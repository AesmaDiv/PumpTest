"""
    Модуль содержит классы для работы с Advantech ADAM 5000 TCP"""
import asyncio
from importlib import reload
from loguru import logger

from PyQt6.QtCore import pyqtSignal, QObject

from Classes.Adam.adam_5k import Adam5K, Param, SlotType
from Classes.Adam import adam_config as config


class AdamManager(QObject):
    """Класс для связи контроллера Adam5000TCP с интерфейсом программы"""
    _signal = pyqtSignal(dict, name="dataReceived")
    _probes = 10
    _sensors = {
        'rpm': [0.0] * _probes,
        'torque': [0.0] * _probes,
        'psi_in': [0.0] * _probes,
        'psi_out': [0.0] * _probes,
        'flw0': [0.0] * _probes,
        'flw1': [0.0] * _probes,
        'flw2': [0.0] * _probes
    }

    def __init__(self, host, port=502, address=1, parent=None) -> None:
        super().__init__(parent=parent)
        self._adam = Adam5K(host, port, address)
        self._adam.setCallback(self.__adamThreadTickCallback)

    @property
    def isConnected(self):
        """состояние подключения к Adam5000TCP"""
        return self._adam.isConnected

    def setSensors(self, sensor_names: list):
        """определение имён опрашиваемых каналов"""
        self._sensors = {
            name: [0.0] * self._probes if name in config.COEFS
                else False for name in sensor_names
        }

    def reloadConfig(self):
        """перезагрузка конфигурации"""
        self._adam.pause()
        try:
            global config
            config = reload(config)
        except BaseException as err:
            logger.error("Ошибка обновления конфигурации. Проверьте корректность данных.")
            logger.error(str(err))
        self._adam.unpause()

    def setPollingState(self, state: bool, interval=1):
        """вкл/выкл опрос устройства"""
        return AdamManager.__create_task(self.setPollingStateAsync(state, interval))

    async def setPollingStateAsync(self, state: bool, interval=1):
        """вкл/выкл опрос устройства (ассинхронная)"""
        if state and await self._adam.connect():
            self._adam.setInterval(interval)
            return self._adam.setReadingState(True)
        self._adam.setReadingState(False)
        await self._adam.disconnect()
        return False

    def setValue(self, param: Param, value: int) -> bool:
        """установка значения для канала"""
        return AdamManager.__create_task(self.setValueAsync(param, value))

    def getValue(self, param: Param):
        """получение значения из канала"""
        return AdamManager.__create_task(self.getValueAsync(param))

    async def setValueAsync(self, param: Param, value: int) -> bool:
        """установка значения для канала (ассинхронная)"""
        if self.checkParams(param, value):
            self._adam.setChannelValue(param.slot_type, param.slot, param.channel, value)
            return True
        return False

    async def getValueAsync(self, param: Param):
        """получение значения для канала (ассинхронная)"""
        if self.checkParams(param, 0):
            return self._adam.getValue(param.slot_type, param.slot, param.channel)
        return -1

    def checkParams(self, params: Param, value) -> bool:
        """проверка параметров"""
        if self._adam.isConnected:
            if params.slot_type in (SlotType.ANALOG, SlotType.DIGITAL):
                if 0 <= params.slot < 8 and 0 <= params.channel < 8:
                    if 0 <= value <= params.dig_max:
                        return True
        return False

    def __adamThreadTickCallback(self):
        """тик таймера опроса устройства"""
        self.__updateSensors()
        args = self.__createEventArgs()
        try:
            self._signal.emit(args)
        except RuntimeError as err:
            self._adam.disconnect()
            logger.error(err.args)

    def __updateSensors(self):
        for key in self._sensors:
            if not self._adam.isReading:
                self._sensors[key] = [0.0] * self._probes
                continue
            if key not in config.PARAMS:
                continue
            param = config.PARAMS[key]
            value = self._adam.getValue(param.slot_type, param.slot, param.channel)
            if key in config.COEFS:
                value = param.val_rng * (value - param.offset) / param.dig_max
                value *= config.COEFS[key]
                self._sensors[key].pop(0)
                self._sensors[key].append(round(value, 2))
            else:
                self._sensors[key] = value

    def __createEventArgs(self):
        return {
            key: sum(vals)/len(vals) if key in config.COEFS
                else vals for key, vals in self._sensors.items()
        }

    @staticmethod
    def __create_task(task):
        # try:
        #     loop = asyncio.new_event_loop()
        #     asyncio.set_event_loop(loop)
        #     return asyncio.create_task(task)
        # except RuntimeError as err:
        #     print("Async error:", err)
        return asyncio.run(task)
