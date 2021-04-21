from PyQt5.QtCore import QThread, QObject, pyqtSignal
from AesmaLib.Hardware.Adam5k import Adam5K
import threading
from Globals import gvars, adam_config


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


def changeConnectionState():
    state = False
    if not __private.adam.isConnected():
        state = startDisplaying()
    else:
        stopDisplaying()
    return state


def startDisplaying():
    if __private.adam.connect():
        __private.adam.startReading()
        __private.display_iteration = 0
        __private.is_displaying = True
        threading.Thread(target=__displayTimerThread).start()
        return True
    else:
        return False


def stopDisplaying():
    __private.is_displaying = False
    while __private.is_timer_active:
        continue
    __private.adam.stopReading()
    __private.adam.disconnect()


def __displayTimerThread():
    print('funcsAdam:', '\tdisplayTimer started...')
    __private.is_timer_active = True
    while __private.is_displaying:
        timer = threading.Timer(1, __displayTimerTick)
        timer.start()
        timer.join()
    __private.is_timer_active = False
    print('funcsAdam:', '\tdisplayTimer stopped')


def __displayTimerTick():
    __getValuesFromRegisters()
    __calculateRealValues()
    broadcaster.event.emit(sensors)
    print('funcsAdam:', '\tdisplayTick iteration:', __private.display_iteration)
    __private.display_iteration += 1


def __getValuesFromRegisters():
    sensors['rpm'] = __getValueFromRegister(*adam_config.rpm)
    sensors['torque'] = __getValueFromRegister(*adam_config.torque)
    sensors['pressure_in'] = __getValueFromRegister(*adam_config.pressure_in)
    sensors['pressure_out'] = __getValueFromRegister(*adam_config.pressure_out)
    sensors['flw05'] = __getValueFromRegister(*adam_config.flw05)
    sensors['flw1'] = __getValueFromRegister(*adam_config.flw1)
    sensors['flw2'] = __getValueFromRegister(*adam_config.flw2)


def __getValueFromRegister(name):
    return __private.adam.getValue(Adam5K.SlotType.ANALOG, name)


def __calculateRealValues():
    sensors['rpm'] = (sensors['rpm'] - 32767) * 10000 / 65535
    sensors['torque'] = (sensors['torque'] - 32767) * 20000 / 65535
    sensors['pressure_in'] *= (600 * 0.145 / 65535)
    sensors['pressure_out'] *= (6000 / 65535)
    sensors['flw05'] *= (1282 * 0.158 / 65535)
    sensors['flw1'] *= (1700 * 0.158 / 65535)
    sensors['flw2'] *= (13000 * 0.158 / 65535)
