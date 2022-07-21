from dataclasses import dataclass
from loguru import logger
from enum import Enum, auto

from Classes.Adam.adam_manager import AdamManager
from Classes.Adam.adam_config import PARAMS
from Classes.Adam.adam_names import ChannelNames as CN
from Classes.UI.funcs.funcs_aux import pause, calculateLift, calculatePower, applySpeedFactor


class TestMode(Enum):
    """Режимы работы стенда"""
    TEST = auto()   # тест
    IDLING = auto() # обкатка
    PURGE = auto()  # продувка


class Flowmeter(Enum):
    """Расходомеры"""
    FLW_05 = auto()
    FLW_1 = auto()
    FLW_2 = auto()


class TestManager:
    """Менеджер управления процессом испытания"""
    SENSORS = (CN.FLW_0, CN.FLW_1, CN.FLW_2, CN.PSI_IN, CN.PSI_OUT, CN.RPM, CN.TORQUE)

    def __init__(self, adam_manager: AdamManager):
        self._adam: AdamManager = adam_manager
        self._is_running = False
        self._points_num = 10
        self._active_flw = CN.FLW_2
        self._testmode = TestMode.IDLING
        self._adam.setSensors(TestManager.SENSORS)
        self._sensors = {
            'RPM': 0.0,
            'Torque': 0.0,
            'PsiIn': 0.0,
            'PsiOut': 0.0,
            'Flow': 0.0,
            'Lift': 0.0,
            'Power': 0.0,
            'Flow0': 0.0,
            'Flow1': 0.0,
            'Flow2': 0.0
        }

    @property
    def isEngineRunning(self):
        """проверка статуса главного привода"""
        return self._adam.getValue(PARAMS[CN.ENGINE]) is True

    @property
    def sensors(self):
        """показания датчиков"""
        return self._sensors

    def switchConnection(self, state):
        """управление подключением к ADAM"""
        result = self._adam.setPollingState(state, 0.100)
        if result:
            self.setDefaults()
        return result

    def setDefaults(self):
        """установка оборудования в исходное состояние"""
        if not self._adam.isConnected:
            logger.error("Adam5KTCP не подключен.")
            return
        self._adam.setValue(PARAMS[CN.ENGINE],      False)
        self._adam.setValue(PARAMS[CN.VLV_AIR],     False)
        self._adam.setValue(PARAMS[CN.VLV_WTR],     False)
        self._adam.setValue(PARAMS[CN.VLV_TST],     False)
        self._adam.setValue(PARAMS[CN.VLV_2],       False)
        self._adam.setValue(PARAMS[CN.VLV_12],      False)
        self._adam.setValue(PARAMS[CN.ROTATE],      False)
        self._adam.setValue(PARAMS[CN.VLV_FLW],     0x0FFF)
        self._adam.setValue(PARAMS[CN.SPEED],       0x0F84)
        # ЗАДЕРЖКА
        pause(1)
        self._testmode = TestMode.IDLING
        self._active_flw = CN.FLW_2
        self._is_running = False
        logger.debug("Установлены значения по умолчанию")

    def startTesting(self):
        """начало испытания"""
        logger.debug(self.startTesting.__doc__)
        if self._testmode != TestMode.IDLING:
            logger.error("Неверный текущий режим")
            return False
        if self._is_running:
            logger.error("Главный привод уже запущен")
            return False
        self._fillWithWater()
        self._setEngineState(True)
        return True

    def stopTesting(self):
        """остановка испытания"""
        logger.debug(self.stopTesting.__doc__)
        if not self._is_running:
            logger.error("Главный привод не запущен")
            return True
        self.setDefaults()
        return True

    def updateSensors(self, adam_data: dict):
        """обновление значений с датчиков"""
        flw, lft, pwr = self._getCalculatedVals(adam_data)
        self._sensors['RPM']    = round(adam_data[CN.RPM],0)
        self._sensors['Torque'] = round(adam_data[CN.TORQUE],2)
        self._sensors['PsiIn']  = round(adam_data[CN.PSI_IN],2)
        self._sensors['PsiOut'] = round(adam_data[CN.PSI_OUT],2)
        self._sensors['Flow0']  = round(adam_data[CN.FLW_0],2)
        self._sensors['Flow1']  = round(adam_data[CN.FLW_1],2)
        self._sensors['Flow2']  = round(adam_data[CN.FLW_2],2)
        self._sensors['Flow']   = round(flw, 2)
        self._sensors['Lift']   = round(lft, 2)
        self._sensors['Power']  = round(pwr, 2)

    def sliderToAdam(self, name: str, slider_value: int):
        """установка значения канала из слайдера"""
        param = {
            'sliderSpeed': PARAMS[CN.SPEED],
            'sliderFlow': PARAMS[CN.VLV_FLW]
        }[name]
        adam_value = int(slider_value * param.dig_max / param.val_rng)
        self._adam.setValue(param, adam_value)

#region ГЛАВНЫЙ ПРИВОД ->
    def _setEngineState(self, state: bool):
        """вкл/выкл главный привод"""
        logger.debug(f"{'Запуск' if state else 'Остановка'} главного привода")
        self._adam.setValue(PARAMS[CN.ENGINE], state)
        self._is_running = state

    def setEngineRotation(self, to_left: bool) -> bool:
        """переключение направления вращения"""
        logger.debug(f"Выбор {'левого' if to_left else 'правого'} вращения")
        if self._is_running:
            logger.error("Нельзя при работающем главном приводе")
            return False
        self._adam.setValue(PARAMS[CN.ROTATE], to_left)
        return True
#endregion <- ГЛАВНЫЙ ПРИВОД

#region РАСХОДОМЕРЫ ->
    def switchFlowmeter(self, flowmeter: Flowmeter):
        """переключение активного расходомера"""
        {
            Flowmeter.FLW_05: self.setFlowmeter_05,
            Flowmeter.FLW_1: self.setFlowmeter_1,
            Flowmeter.FLW_2: self.setFlowmeter_2
        }[flowmeter]()

    def setFlowmeter_05(self):
        """переключение на 1/2 дюймовый расходомер"""
        logger.debug(self.setFlowmeter_05.__doc__)
        # self._active_flw = CN.FLW_0
        # self._adam.setValue(PARAMS[CN.VLV_2], True)
        # self._adam.setValue(PARAMS[CN.VLV_12], True)
        self._setFlowmeter({'flw': CN.FLW_0, 'vlv1': True, 'vlv2': True})

    def setFlowmeter_1(self):
        """переключение на 1 дюймовый расходомер"""
        logger.debug(self.setFlowmeter_1.__doc__)
        # self._active_flw = CN.FLW_1
        # self._adam.setValue(PARAMS[CN.VLV_2], True)
        # self._adam.setValue(PARAMS[CN.VLV_12], False)
        self._setFlowmeter({'flw': CN.FLW_1, 'vlv1': False, 'vlv2': True})

    def setFlowmeter_2(self):
        """переключение на 2 дюймовый расходомер"""
        logger.debug(self.setFlowmeter_2.__doc__)
        # self._active_flw = CN.FLW_2
        # self._adam.setValue(PARAMS[CN.VLV_2], False)
        # self._adam.setValue(PARAMS[CN.VLV_12], False)
        self._setFlowmeter({'flw': CN.FLW_2, 'vlv1': False, 'vlv2': False})

    def _setFlowmeter(self, params: dict):
        """переключение расходомера"""
        self._active_flw = params['flw']
        self._adam.setValue(PARAMS[CN.VLV_2],  params['vlv2'])
        self._adam.setValue(PARAMS[CN.VLV_12], params['vlv1'])
#endregion <- РАСХОДОМЕРЫ

#region РЕЖИМЫ РАБОТЫ ->
    def switchTestMode(self, testmode: TestMode):
        """переключение режима работы стенда"""
        {
            TestMode.IDLING: self._setMode_Idling,
            TestMode.PURGE: self._setMode_Purge,
            TestMode.TEST: self._setMode_Test
        }[testmode]()

    def switchPurge(self, state: bool) -> bool:
        """вкл/выкл продувки"""
        if state and self._is_running:
            logger.error("Нельзя при работающем главном приводе")
            return False
        if not state and self._testmode != TestMode.PURGE:
            logger.error("Стенд не в режиме продувки")
            return False
        self._setMode_Purge(state)
        return True

    def _setMode_Purge(self, state: bool):
        """переключение в режим продувки"""
        logger.debug(self._setMode_Purge.__doc__)
        if self._testmode != TestMode.IDLING:
            self._setMode_Idling()
        self._adam.setValue(PARAMS[CN.VLV_WTR], False)
        # ЗАДЕРЖКА
        pause(10)
        self._adam.setValue(PARAMS[CN.VLV_AIR], state)
        self._testmode = TestMode.PURGE

    def _setMode_Idling(self):
        """переключение в режим обкатки"""
        logger.debug(self._setMode_Idling.__doc__)
        self.setFlowmeter_2()
        self._adam.setValue(PARAMS[CN.VLV_TST], False)
        self._testmode = TestMode.IDLING

    def _setMode_Test(self):
        """переключение в режим тестирования"""
        logger.debug(self._setMode_Test.__doc__)
        if self._testmode == TestMode.PURGE:
            logger.error("Нельзя переключаться в режим тестирования при продувке")
            return
        self._adam.setValue(PARAMS[CN.VLV_TST], True)
        self._testmode = TestMode.TEST
#endregion РЕЖИМЫ РАБОТЫ <-

#region ПРОЧЕЕ ->
    def _fillWithWater(self):
        """заполнение насоса водой"""
        logger.debug(self._fillWithWater.__doc__)
        self._adam.setValue(PARAMS[CN.VLV_AIR], False)
        # ЗАДЕРЖКА
        pause(1)
        self._adam.setValue(PARAMS[CN.VLV_WTR], True)
        # ЗАДЕРЖКА
        pause(1)

    def _getCalculatedVals(self, adam_data: dict):
        """получение расчётных значений """
        rpm = adam_data[CN.RPM]
        flw = adam_data[self._active_flw]
        lft = calculateLift(adam_data[CN.PSI_IN], adam_data[CN.PSI_OUT])
        pwr = calculatePower(adam_data[CN.TORQUE], rpm)
        flw, lft, pwr = applySpeedFactor(flw, lft, pwr, rpm)
        return flw, lft, pwr
#endregion <- ПРОЧЕЕ
