"""
    AesmaDiv 2021
    Модуль для работы с Advantech Adam5000TCP
"""
import socket
import threading
from enum import Enum
from array import array
from bitstring import BitArray
from bitarray import bitarray


class Adam5K:
    """ Класс для работы с Advantech Adam5000TCP """
    class SlotType(Enum):
        """ Тип слота """
        ALL = 'ALL'
        ANALOG = 'ANALOG'
        DIGITAL = 'DIGITAL'

    def __init__(self, host: str, port: int, modbus: int):
        self._conn = (host, port)
        self._modbus = modbus.to_bytes(1, 'big')[0]
        self._is_connected = False
        self._is_reading = False
        self._is_timer_alive = False
        self._is_paused = False
        self._thread_iteration = 0
        self._read_interval_secs: float = 1.0
        self._slots = {
            Adam5K.SlotType.ANALOG:  {
                'READ':  bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x6,
                                    self._modbus, 0x4, 0x0, 0x0, 0x0, 0x40]),
                'WRITE': bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x6,
                                    self._modbus, 0x6, 0x0, 0x0, 0x0, 0x0]),
                'DATA':  []
            },
            Adam5K.SlotType.DIGITAL: {
                'READ':  bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x6,
                                    self._modbus, 0x1, 0x0, 0x0, 0x0, 0x80]),
                'WRITE': bytearray([0x0, 0x0, 0x0, 0x0, 0x0, 0x6,
                                    self._modbus, 0x5, 0x0, 0x0, 0x0, 0x0]),
                'DATA':  []
            }
        }
        self._commands = []
        try:
            self._sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except BaseException as ex:
            print('Adam5K:', '\tinitialization error: ' + str(ex))
        print('Adam5K:', '\tinitialized')

    def __del__(self):
        self.disconnect()
        print('Adam5K:', '\tdestroyed')

    def connect(self):
        if self._is_connected:
            msg = 'already connected'
        else:
            try:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.connect(self._conn)
                self._is_connected = True
                self._is_reading = False
                msg = 'socket connected'
            except BaseException as ex:
                msg = 'error connecting socket:', self._conn
        print('Adam5K:', '\tconnect:', msg)
        return self._is_connected

    def disconnect(self):
        if not self._is_connected:
            msg = 'not connected'
        else:
            self._is_reading = False
            while self._is_timer_alive:
                # print('Adam5K:', 'disconnect', 'waiting thread to end..')
                continue
            self._sock.close()
            self._is_connected = False
            msg = 'socket disconnected'
        print('Adam5K:', '\tdisconnect:', msg)

    def startReading(self):
        if not self._is_connected:
            print('Adam5K:', '\tstartReading:', 'not connected')
        elif self._is_reading:
            print('Adam5K:', '\tstartReading:', 'already reading', )
        else:
            self._is_reading = True
            self._thread_iteration = 0
            threading.Thread(target=self.__readingTimerThread).start()

    def stopReading(self):
        self._is_reading = False
        while self._is_timer_alive:
            continue

    def isBusy(self):
        return len(self._commands)

    def isConnected(self):
        return self._is_connected

    def pause(self):
        self._is_paused = True

    def unpause(self):
        self._is_paused = False

    def clearCommands(self):
        self._commands.clear()

    def setReadingInterval(self, seconds: float):
        self._read_interval_secs = seconds

    def setValue(self, slot_type: SlotType, slot: int, channel: int, value):
        command = self._buildCommand_Register('WRITE', slot_type, slot, channel, value)
        self._sendCommand(command)
        print('Adam5K:', '\tsetValue:', slot_type.value, slot, channel, value)

    def setSlot(self, slot_type: SlotType, slot: int, pattern: list):
        command = self._buildCommand_Slot(slot_type, slot, pattern)
        self._sendCommand(command)
        print('Adam5K:', '\tsetSlot:', slot_type.value, slot, pattern)

    def getValue(self, slot_type: SlotType, slot: int, channel: int):
        if not self._is_reading:
            self._readValuesFromDevice()
        result = self._readValuesFromData(slot_type, slot, channel)
        return result

    def getValueFromDevice(self, slot_type: SlotType, slot: int, channel: int):
        command = self._buildCommand_Register('READ', slot_type, slot, channel)
        values = self._getValues(slot_type, command)
        result = values[0]
        if slot_type == Adam5K.SlotType.DIGITAL:
            return result == 1
        return result

    def _readValuesFromData(self, slot_type: SlotType, slot: int, channel: int):
        result = 0
        if 0 <= slot < 8 and 0 <= channel < 8:
            try:
                if slot_type == Adam5K.SlotType.DIGITAL:
                    if len(self._slots[slot_type]['DATA']) == 16:
                        value = self._slots[Adam5K.SlotType.DIGITAL]['DATA'][slot]
                        bits = self._getBits(value)
                        result = bits[channel] == '1'
                else:
                    if len(self._slots[slot_type]['DATA']) == 64:
                        result = self._slots[slot_type]['DATA'][slot * 8 + channel]
            except BaseException as ex:
                result = -1
        return result

    def _readValuesFromDevice(self, slot_type: SlotType = SlotType.ALL):
        if slot_type == Adam5K.SlotType.ALL:
            self._readValuesFromDevice(Adam5K.SlotType.ANALOG)
            self._readValuesFromDevice(Adam5K.SlotType.DIGITAL)
        else:
            values: array = self._getValues(slot_type, self._slots[slot_type]['READ'])
            self._slots[slot_type]['DATA'] = values.tolist()

    def _getValues(self, slot_type: SlotType, command: bytearray):
        result = array('H')
        try:
            data_bytes = self._execute(command)
            if len(data_bytes) > 8:
                data_count = data_bytes[8]
                data_bytes = data_bytes[9:9 + data_count]
            result = self._parseBytes(slot_type, data_bytes)
        except BaseException as ex:
            print('Adam5K:', '\t_getValues error:', str(ex))
        return result

    def _getBits(self, value: int):
        bits = list(BitArray(uint=value, length=8).bin)
        bits.reverse()
        return bits

    def _parseBytes(self, slot_type: SlotType, slots_data: bytearray):
        result = array('H')
        if len(slots_data) % 2 > 0:
            slots_data.append(0)
        result.frombytes(slots_data)
        if slot_type == Adam5K.SlotType.ANALOG:
            result.byteswap()
        return result

    def _buildCommand_Register(self, command: str, slot_type: SlotType, slot: int, channel: int, value=0):
        result = self._slots[slot_type][command].copy()
        coef = 8 if slot_type == Adam5K.SlotType.ANALOG else 16
        result[9] = coef * slot + channel
        if command == 'READ':
            result[10:] = b'\x00\01'
        elif slot_type == Adam5K.SlotType.ANALOG:
            result[10:] = value.to_bytes(length=2, byteorder='big')
        else:
            result[10:] = b'\xff\00' if value else b'\x00\00'
        return result

    def _buildCommand_Slot(self, slot_type: SlotType, slot: int, pattern: list):
        address = slot * (16 if slot_type == Adam5K.SlotType.DIGITAL else 8)
        result = bytearray([self._modbus, 0xf])
        result.extend(address.to_bytes(2, 'big'))
        if slot_type == Adam5K.SlotType.DIGITAL:
            bits = bitarray(pattern)
            bits.reverse()
            values = bits.tobytes()
            result.extend((len(bits) * 2).to_bytes(2, 'big'))
            result.extend((len(values) * 2).to_bytes(1, 'big'))
            for value in values:
                result.extend(value.to_bytes(2, 'little'))
        else:
            result.extend([0x0, 0x8])
            result.extend(pattern)
        prefix = bytearray(len(result).to_bytes(6, 'big'))
        result[0:0] = prefix
        print('Adam5K:', '\t_buildSlotCommand:', 'command=', result)
        return result

    def _sendCommand(self, command):
        if self._is_reading:
            self._commands.append(command)
        else:
            retval = self._execute(command)

    def _execute(self, command: bytearray):
        result = bytearray([])
        self.__read(command, result)
        # thread = threading.Thread(target=self.__read, args=(command, result))
        # thread.start()
        # thread.join()
        return result

    def __readingTimerThread(self):
        print('Adam5K:', '\treadingTimer started ...')
        self._is_timer_alive = True
        while self._is_reading:
            timer = threading.Timer(self._read_interval_secs, self.__readingTimerTick)
            timer.start()
            timer.join()
        self._is_timer_alive = False
        print('Adam5K:', '\treadingTimer stopped')

    def __readingTimerTick(self):
        if len(self._commands):
            command = self._commands.pop(0)
            retval = self._execute(command)
            print('retval', retval)
        else:
            self._readValuesFromDevice()
        print('Adam5K:', '\treadingTick iteration', self._thread_iteration)
        self._thread_iteration += 1

    def __read(self, command: bytearray, result: bytearray):
        if self.__write(command):
            b = bytearray(self._sock.recv(0x89))
            result.extend(b)

    def __write(self, command: bytes):
        if self._sock and self._is_connected:
            return self._sock.send(command) == len(command)
        else:
            return False

    def __clear_buffer(self):
        try:
            self._sock.setblocking(False)
            while self._sock.recv(1024):
                pass
            self._sock.setblocking(True)
        except BlockingIOError as ex:
            pass
