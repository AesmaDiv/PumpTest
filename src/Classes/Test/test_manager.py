"""
    Модуль управления процессом испытания
"""
from enum import Enum, auto
from loguru import logger

from Classes.Adam.adam_manager import AdamManager
from Classes.Adam.adam_config import PARAMS
from Classes.Adam.adam_names import ChannelNames as CN
from Classes.UI.funcs.funcs_aux import pause


class TestMode(Enum):
    """Режимы работы стенда"""
    TEST = auto()   # тест
    IDLING = auto() # обкатка
    PURGE = auto()  # продувка


class Flowmeter(Enum):
    """Расходомеры"""
    FLW_0 = auto()
    FLW_1 = auto()
    FLW_2 = auto()


class TestManager:
    """Менеджер управления процессом испытания"""
    SENSORS = (CN.FLW_0, CN.FLW_1, CN.FLW_2, CN.PSI_IN, CN.PSI_OUT, CN.RPM, CN.TORQUE,
               CN.VLV_2, CN.VLV_1,CN.VLV_WTR,CN.VLV_AIR,CN.VLV_TST)
    # Имена полей для данных с датчиков.
    # Менять с осторожностью -> от них зависят привязки к полям формы
    SENS_NAMES = ('RPM','Torque','PsiIn','PsiOut','Flow0','Flow1','Flow2','Flow','Lift','Power')


    def __init__(self, adam_manager: AdamManager, callback=None):
        self._adam: AdamManager = adam_manager
        self._callback = callback
        self._is_running = False
        self._points_num = 10
        self._active_flw = CN.FLW_2
        self._testmode = TestMode.IDLING
        self._adam.setSensors(TestManager.SENSORS)
        self._sensors = dict.fromkeys(self.SENS_NAMES, 0.0)

    @property
    def isEngineRunning(self):
        """проверка статуса главного привода"""
        return self._adam.getValue(PARAMS[CN.ENGINE]) is True

    @property
    def sensors(self):
        """показания датчиков"""
        return self._sensors

    @property
    def testMode(self):
        """текущий режим"""
        return self._testmode

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
        self._adam.setValue(PARAMS[CN.VLV_1],       False)
        self._adam.setValue(PARAMS[CN.ROTATE],      True)
        self._adam.setValue(PARAMS[CN.VLV_FLW],     0x0000)
        self._adam.setValue(PARAMS[CN.SPEED],       0x0A7F)
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

    def updateSensors(self, adam_data: dict, stages: int, base_rpm: int):
        """обновление значений с датчиков"""
        self._sensors['RPM']    = round(adam_data[CN.RPM],0)          # об.мин
        self._sensors['Torque'] = abs(round(adam_data[CN.TORQUE],2))  # lb-in
        self._sensors['PsiIn']  = round(adam_data[CN.PSI_IN],2)       # psi
        self._sensors['PsiOut'] = round(adam_data[CN.PSI_OUT],2)      # psi
        self._sensors['Flow0']  = round(adam_data[CN.FLW_0],2)        # м/сут
        self._sensors['Flow1']  = round(adam_data[CN.FLW_1],2)        # м/сут
        self._sensors['Flow2']  = round(adam_data[CN.FLW_2],2)        # м/сут
        flw, lft, pwr = self._getCalculatedVals(float(base_rpm))
        self._sensors['Flow']   = round(flw, 2)                       # м/сут
        self._sensors['Lift']   = round(lft / float(stages), 2)       # метры
        self._sensors['Power']  = round(pwr / float(stages), 4)       # кВт

    def sliderToAdam(self, name: str, slider_value: int):
        """установка значения канала из слайдера"""
        param = {
            'sliderSpeed': PARAMS[CN.SPEED],
            'sliderFlow': PARAMS[CN.VLV_FLW]
        }[name]
        # пока управление сладйдерами напрямую - значение слайдера летит прямо в адам
        # adam_value = int(slider_value * param.dig_max / param.val_rng)
        self._adam.setValue(param, slider_value)

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
            Flowmeter.FLW_0: self.setFlowmeter_0,
            Flowmeter.FLW_1: self.setFlowmeter_1,
            Flowmeter.FLW_2: self.setFlowmeter_2
        }[flowmeter]()

    def setFlowmeter_0(self):
        """переключение на 1/2 дюймовый расходомер"""
        logger.debug(self.setFlowmeter_0.__doc__)
        self._setFlowmeter(vlv1=True, vlv2=True)

    def setFlowmeter_1(self):
        """переключение на 1 дюймовый расходомер"""
        logger.debug(self.setFlowmeter_1.__doc__)
        self._setFlowmeter(vlv1=False, vlv2=True)

    def setFlowmeter_2(self):
        """переключение на 2 дюймовый расходомер"""
        logger.debug(self.setFlowmeter_2.__doc__)
        self._setFlowmeter(vlv1=False, vlv2=False)

    def _setFlowmeter(self, vlv1: bool, vlv2: bool):
        """переключение расходомера"""
        #                 кран1 кран2
        # расходомер 0.5"   1     1
        # расходомер   1"   0     1
        # расходомер   2"   0     0
        self._active_flw = CN.FLW_0 if vlv1 else CN.FLW_1 if vlv2 else CN.FLW_2
        self._adam.setValue(PARAMS[CN.VLV_2],  vlv2)
        self._adam.setValue(PARAMS[CN.VLV_1], vlv1)
#endregion <- РАСХОДОМЕРЫ

#region РЕЖИМЫ РАБОТЫ ->
    def switchTestMode(self, testmode: TestMode):
        """переключение режима работы стенда"""
        {
            TestMode.IDLING: self._setMode_Idling,
            TestMode.PURGE: self._setMode_Purge,
            TestMode.TEST: self._setMode_Test
        }[testmode]()

    def _setMode_Purge(self):
        """переключение в режим продувки"""
        logger.debug(self._setMode_Purge.__doc__)
        # если продувка уже включена - выключаем и выходим
        if self._testmode == TestMode.PURGE:
            self._adam.setValue(PARAMS[CN.VLV_AIR], False)
            self._testmode = TestMode.IDLING
            return
        self._onEvent("Идёт переключение в режим продувки...")
        self._adam.setValue(PARAMS[CN.VLV_WTR], False)
        # ЗАДЕРЖКА
        # pause(10)
        self._adam.setValue(PARAMS[CN.VLV_AIR], self._testmode != TestMode.PURGE)
        self._onEvent(None)
        self._testmode = TestMode.PURGE

    def _setMode_Idling(self):
        """переключение в режим обкатки"""
        logger.debug(self._setMode_Idling.__doc__)
        self._onEvent("Идёт переключение в режим обкатки...")
        self.setFlowmeter_2()
        self._adam.setValue(PARAMS[CN.VLV_TST], False)
        # pause(5)
        self._onEvent(None)
        self._testmode = TestMode.IDLING

    def _setMode_Test(self):
        """переключение в режим тестирования"""
        logger.debug(self._setMode_Test.__doc__)
        if self._testmode == TestMode.PURGE:
            logger.error("Нельзя переключаться в режим тестирования при продувке")
            return
        self._onEvent("Идёт переключение в режим теста...")
        self._adam.setValue(PARAMS[CN.VLV_TST], True)
        # pause(5)
        self._onEvent(None)
        self._testmode = TestMode.TEST
#endregion РЕЖИМЫ РАБОТЫ <-

#region ПРОЧЕЕ ->
    def _fillWithWater(self):
        """заполнение насоса водой"""
        logger.debug(self._fillWithWater.__doc__)
        self._adam.setValue(PARAMS[CN.VLV_AIR], False)
        # ЗАДЕРЖКА
        # pause(1)
        self._adam.setValue(PARAMS[CN.VLV_WTR], True)
        # ЗАДЕРЖКА
        # pause(1)
        self._onEvent("Идёт заполнение водой...")
        # pause(10)
        self._onEvent("ИДЁТ ИСПЫТАНИЕ...")

    def _getCalculatedVals(self, base_rpm: float):
        """получение расчётных значений """
        flowmeter = {
            CN.FLW_0: "Flow0",
            CN.FLW_1: "Flow1",
            CN.FLW_2: "Flow2"
        }[self._active_flw]
        flw = self._sensors[flowmeter]
        lft = self._calculateLift()
        pwr = self._calculatePower()
        flw, lft, pwr = self._applySpeedFactor(base_rpm, flw, lft, pwr)
        return flw, lft, pwr

    def _calculateLift(self):
        """рассчёт потребляемой мощности"""
        psi_diff = (self._sensors['PsiOut'] - self._sensors['PsiIn'])
        # 1 psi поднимает воду на 2.31 фута * перевод в метры
        lift =  max(psi_diff, 0) * 2.31 * 0.3048
        return lift

    def _calculatePower(self):
        """рассчёт потребляемой мощности"""
        # перевод из lb-in в Н/м
        npm = self._sensors['Torque'] * 0.113
        power = self._sensors['RPM'] * npm / 9549.0
        return power

    def _applySpeedFactor(self, base_rpm: float, flw: float, lft: float, pwr: float):
        """применение фактора скорости"""
        if self._sensors['RPM']:
            coeff = base_rpm / self._sensors['RPM']
            flw *= coeff
            lft *= coeff ** 2
            pwr *= coeff ** 3
        return flw, lft, pwr

    def _onEvent(self, message):
        """трансляция сообщения о событии"""
        if self._callback:
            self._callback(message)
#endregion <- ПРОЧЕЕ
