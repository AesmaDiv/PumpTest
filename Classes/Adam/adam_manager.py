import threading
from PyQt5.QtCore import QThread, QObject, pyqtSignal
from Classes.Adam import adam_config
from AesmaLib.Hardware.Adam5k import Adam5K


class Privategvars:
    is_displaying = False
    is_timer_active = False
    display_iteration: int = 0
    adam = Adam5K(
        adam_config.ip,
        adam_config.port,
        adam_config.modbus
    )


class Broadcaster(QObject):
    event = pyqtSignal(dict)


class AdamManager:
    __private = Privategvars()
    broadcaster = Broadcaster()
    sensors = {
        'rpm': 0.0,
        'torque': 0.0,
        'pressure_in': 0.0,
        'pressure_out': 0.0,
        'flw05': 0.0,
        'flw1': 0.0,
        'flw2': 0.0
    }

    def changeConnectionState(self):
        state = False
        if not self.__private.adam.isConnected():
            state = self.startDisplaying()
        else:
            self.stopDisplaying()
        return state

    def startDisplaying(self):
        if self.__private.adam.connect():
            self.__private.adam.startReading()
            self.__private.display_iteration = 0
            self.__private.is_displaying = True
            threading.Thread(target=AdamManager.__displayTimerThread).start()
            return True
        return False

    def stopDisplaying(self):
        self.__private.is_displaying = False
        while self.__private.is_timer_active:
            continue
        self.__private.adam.stopReading()
        self.__private.adam.disconnect()

    def __displayTimerThread(self):
        print('funcsAdam:', '\tdisplayTimer started...')
        self.__private.is_timer_active = True
        while self.__private.is_displaying:
            timer = threading.Timer(1, AdamManager.__displayTimerTick)
            timer.start()
            timer.join()
        self.__private.is_timer_active = False
        print('funcsAdam:', '\tdisplayTimer stopped')

    def __displayTimerTick(self):
        self.__getValuesFromRegisters()
        self.__calculateRealValues()
        self.broadcaster.event.emit(self.sensors)
        print('funcsAdam:', '\tdisplayTick iteration:', self.__private.display_iteration)
        self.__private.display_iteration += 1

    def __getValuesFromRegisters(self):
        self.sensors['rpm'] = AdamManager.__getValueFromRegister(*adam_config.rpm)
        self.sensors['torque'] = AdamManager.__getValueFromRegister(*adam_config.torque)
        self.sensors['pressure_in'] = AdamManager.__getValueFromRegister(*adam_config.pressure_in)
        self.sensors['pressure_out'] = AdamManager.__getValueFromRegister(*adam_config.pressure_out)
        self.sensors['flw05'] = AdamManager.__getValueFromRegister(*adam_config.flw05)
        self.sensors['flw1'] = AdamManager.__getValueFromRegister(*adam_config.flw1)
        self.sensors['flw2'] = AdamManager.__getValueFromRegister(*adam_config.flw2)

    def __getValueFromRegister(self, name):
        return self.__private.adam.getValue(Adam5K.SlotType.ANALOG, name, None)

    def __calculateRealValues(self):
        self.sensors['rpm'] = (self.sensors['rpm'] - 32767) * 10000 / 65535
        self.sensors['torque'] = (self.sensors['torque'] - 32767) * 20000 / 65535
        self.sensors['pressure_in'] *= (600 * 0.145 / 65535)
        self.sensors['pressure_out'] *= (6000 / 65535)
        self.sensors['flw05'] *= (1282 * 0.158 / 65535)
        self.sensors['flw1'] *= (1700 * 0.158 / 65535)
        self.sensors['flw2'] *= (13000 * 0.158 / 65535)
