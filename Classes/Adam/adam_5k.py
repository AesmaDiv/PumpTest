"""
    AesmaDiv 2021
    Модуль для работы с Advantech Adam5000TCP
"""
import socket
from time import sleep
from threading import Thread
from dataclasses import dataclass
from enum import Enum
from array import array
from bitstring import BitArray
from bitarray import bitarray


class CommandType(Enum):
    """ Типы команды """
    READ = 0    # чтение
    WRITE = 1   # запись
    MULTI = 2   # несколько???

class SlotType(Enum):
    """ Тип слота """
    ALL = 'ALL'
    ANALOG = 'ANALOG'
    DIGITAL = 'DIGITAL'

@dataclass
class Param:
    """ Класс параметров канала """
    slot_type: SlotType = SlotType.ALL
    slot: int = 0
    channel: int = 0
    val_rng: float = 0.0
    offset: int = 0x0
    dig_max: int = 0x0FFF

class CommandBuilder:
    """ Класс строителя комманд """
    def __init__(self, address: int):
        self._address = address
        self._default_commands = {
            SlotType.ANALOG: {
                CommandType.READ: bytearray([
                    0x0, 0x0, 0x0, 0x0, 0x0, 0x6,
                    self._address, 0x4, 0x0, 0x0, 0x0, 0x40
                ]),
                CommandType.WRITE: bytearray([
                    0x0, 0x0, 0x0, 0x0, 0x0, 0x6,
                    self._address, 0x6, 0x0, 0x0, 0x0, 0x0
                ])
            },
            SlotType.DIGITAL: {
                CommandType.READ: bytearray([
                    0x0, 0x0, 0x0, 0x0, 0x0, 0x6,
                    self._address, 0x1, 0x0, 0x0, 0x0, 0x80
                ]),
                CommandType.WRITE: bytearray([
                    0x0, 0x0, 0x0, 0x0, 0x0, 0x6,
                    self._address, 0x5, 0x0, 0x0, 0x0, 0x0
                ])
            }
        }

    def get_default_command(self, slot_type, command_type):
        """ получение команды по умолчанию """
        return self._default_commands[slot_type][command_type]

    def build_register(self, command_type, slot_type, slot, channel, value=0):
        """ построение комманды для чтения/записи регистра канала """
        result = self._default_commands[slot_type][command_type].copy()
        coef = 8 if slot_type == SlotType.ANALOG else 16
        result[9] = coef * slot + channel
        if command_type == CommandType.READ:
            result[10:] = b'\x00\01'
        elif slot_type == SlotType.ANALOG:
            result[10:] = value.to_bytes(length=2, byteorder='big')
        else:
            result[10:] = b'\xff\00' if value else b'\x00\00'
        print('build_register cmd =', result)
        return result

    def build_slot(self, slot_type: SlotType, slot: int, pattern: list):
        """ построение комманды для чтения из регистров слота """
        address = slot * (16 if slot_type == SlotType.DIGITAL else 8)
        result = bytearray([self._address, 0xf])
        result.extend(address.to_bytes(2, 'big'))
        if slot_type == SlotType.DIGITAL:
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
        print('build_slot cmd =', result)
        return result

class Adam5K:
    """ Класс для работы с Advantech Adam5000TCP """

    _states = {
        "is_connected": False,
        "is_reading": False,
        "is_paused": False
    }

    def __init__(self, host: str, port=502, address=1):
        self._conn = (host, port)
        self._builder = CommandBuilder(address.to_bytes(1, 'big')[0])
        self._sock: socket.socket = None
        self._interval = 1.0
        self._commands = []
        self._data = {
            SlotType.ANALOG: [],
            SlotType.DIGITAL: []
        }
        self._thread: Thread = Thread(
            name="Adam5k polling thread",
            target=self._timer_thread
        )

    def __del__(self):
        self.disconnect()
        print('Adam5K:', '\tdestroyed')

    def connect(self) -> bool:
        """ подключение """
        if self._states["is_connected"]:
            msg = 'already connected'
        else:
            try:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.connect(self._conn)
                self._states["is_connected"] = True
                self._states["is_reading"] = False
                msg = 'socket connected'
            except socket.error as ex:
                msg = 'error', self._conn, ex.strerror
        print(f'Adam5K::connect:\t{msg}')
        return self._states["is_connected"]

    def disconnect(self):
        """ отключение """
        if not self._states["is_connected"]:
            msg = 'not connected'
        else:
            self._states["is_reading"] = False
            while self._thread.is_alive():
                continue
            self._sock.close()
            self._sock = None
            self._states["is_connected"] = False
            msg = 'socket disconnected'
        print(f'Adam5K::disconnect:\t{msg}')

    def is_busy(self):
        """ возвращает занят ли контроллер (есть ли команды в очереди)"""
        return len(self._commands)

    def is_connected(self) -> bool:
        """ возвращает статус подключения """
        return self._states["is_connected"]

    def pause(self):
        """ приостановка опроса """
        self._states["is_paused"] = True

    def unpause(self):
        """ возобновление опроса """
        self._states["is_paused"] = False

    def clear_сommands(self):
        """ очистка очереди команд """
        self._commands.clear()

    def set_interval(self, seconds: float):
        """ установка интервала опроса """
        self._interval = seconds

    def set_reading_state(self, state: bool) -> bool:
        """ вкл/выкл режима чтения """
        # проверка подключения
        if not self._states["is_connected"]:
            print('Adam5K::set_reading_state:\t not connected')
            return False
        self._states["is_reading"] = state
        # запуск потока таймера опроса
        if state:
            self._thread.start()
        else:
        # остановка таймера опроса
            while self._thread.is_alive(): #self._states["is_timer_alive"]:
                continue
        print(f'Adam5K::set_reading_state:\t{state} results in {self._states["is_reading"]}')
        return True

    def set_channel_value(self, slot_type: SlotType, slot: int, channel: int, value):
        """ установка значения для канала """
        command = self._builder.build_register(
            CommandType.WRITE, slot_type, slot, channel, value
        )
        self._send_сommand(command)
        print(f'Adam5K::set_channel_value:\t{slot_type.value}, {slot}, {channel}, {value}')

    def set_slot_values(self, slot_type: SlotType, slot: int, pattern: list):
        """ установка значений для слота """
        command = self._builder.build_slot(slot_type, slot, pattern)
        self._send_сommand(command)
        print(f'Adam5K::set_slot_value:\t{slot_type.value}, {slot}, {pattern}')

    def get_value(self, slot_type: SlotType, slot: int, channel: int):
        """ получение значения канала """
        if not self._states["is_reading"]:
            self.__read_all_values_from_device()
        result = self.get_value_from_data(slot_type, slot, channel)
        return result

    def get_value_from_device(self, slot_type: SlotType, slot: int, channel: int):
        """ получение значения канала из устройства """
        command = self._builder.build_register(
            CommandType.READ, slot_type, slot, channel
        )
        values = self._execute(command)
        result = values[0]
        if slot_type == SlotType.DIGITAL:
            return result == 1
        return result

    def get_value_from_data(self, slot_type: SlotType, slot: int, channel: int):
        """ чтение значения канала из массива считанных """
        result = 0
        if 0 <= slot < 8 and 0 <= channel < 8:
            if slot_type == SlotType.DIGITAL:
                if len(self._data[slot_type]) == 16:
                    value = self._data[SlotType.DIGITAL][slot]
                    bits = self._to_bits(value)
                    result = bits[channel] == '1'
            else:
                if len(self._data[slot_type]) == 64:
                    result = self._data[slot_type][slot * 8 + channel]
        return result

    def _timer_thread(self):
        """ поток чтения данных из устройства """
        print('Adam5K::\tзапущен таймер опроса устройства...')
        while self._states["is_reading"]:
            if not self._states["is_paused"]:
                thr = Thread(
                    name="Adam5k polling subthread",
                    target=self._timer_tick
                )
                thr.start()
                thr.join()
            sleep(self._interval)
        print('Adam5K::\tтаймер опроса устройства остановлен')

    def _timer_tick(self):
        """ тик таймера отправки команд в устройство """
        # если в очереди есть комманды - выполнить
        if self._commands:
            command = self._commands.pop(0)
            _ = self._execute(command)
        # если нет - читать все значения
        else:
            self.__read_all_values_from_device()

    def __read_all_values_from_device(self, slot_type: SlotType = SlotType.ALL):
        """ чтение всех значений в слоте из устройства """
        if slot_type == SlotType.ALL:
            self.__read_all_values_from_device(SlotType.ANALOG)
            self.__read_all_values_from_device(SlotType.DIGITAL)
        else:
            result = array('H')
            command = self._builder.get_default_command(slot_type, CommandType.READ)
            data_bytes = self._execute(command)
            if len(data_bytes) > 8:
                data_count = data_bytes[8]
                data_bytes = data_bytes[9:9 + data_count]
            result = self._parse_bytes(slot_type, data_bytes)
            self._data[slot_type] = result.tolist()

    @staticmethod
    def _to_bits(value: int):
        """ конвертирование значения в биты """
        bits = list(BitArray(uint=value, length=8).bin)
        bits.reverse()
        return bits

    @staticmethod
    def _parse_bytes(slot_type: SlotType, slots_data: bytearray):
        """ получение списка байт из массива байт """
        result = array('H')
        if len(slots_data) % 2 > 0:
            slots_data.append(0)
        result.frombytes(slots_data)
        if slot_type == SlotType.ANALOG:
            result.byteswap()
        return result

    def _send_сommand(self, command):
        """ отправка команды """
        if self._states["is_reading"]:
            self._commands.append(command)
        else:
            _ = self._execute(command)

    def _execute(self, command: bytearray):
        """ выполнение команды """
        result = bytearray([])
        self.__read(command, result)
        return result

    def __read(self, command: bytearray, result: bytearray):
        """ запись / чтение из устройства """
        if self.__write(command):
            data = bytearray(self._sock.recv(0x89))
            result.extend(data)

    def __write(self, command: bytes):
        """ запись команды в устройство """
        if self._sock and self._states["is_connected"]:
            return self._sock.send(command) == len(command)
        return False

    # def __clear_buffer(self):
    #     """ очистка буффера сокета """
    #     try:
    #         self._sock.setblocking(False)
    #         while self._sock.recv(1024):
    #             pass
    #         self._sock.setblocking(True)
    #     except BlockingIOError as ex:
    #         print(f'Adam5K::clear buffer: error {ex.strerror}')


if __name__ == '__main__':
    adam = Adam5K('10.10.10.11', 502, 1)
    if adam.connect():
        adam.set_reading_state(True)
        # adam.set_slot_values(SlotType.DIGITAL, 0, [False] * 8 * 4)
        adam.set_channel_value(SlotType.ANALOG, 2, 0, 1222)
        # adam.set_slot_values(SlotType.DIGITAL, 3, [True] * 8 * 4)
        while adam.is_busy():
            sleep(1.5)
            continue
        adam.set_reading_state(False)
        adam.disconnect()
