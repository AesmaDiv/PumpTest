"""
    Модуль для работы с оборудованием,
    поддерживающим протокол Modbus
"""
from enum import Enum
from AesmaLib.decorators import Singleton


class CommandBuilder(metaclass=Singleton):
    """ Класс для построения команд протокола Modbus """
    class CommandType(Enum):
        """ Типы команды """
        READ = 0    # чтение
        WRITE = 1   # запись
        MULTI = 2   # несколько???

    class TargetType(Enum):
        """ Типы блока """
        REGISTER = 0    # регистр
        COIL = 1        # бит состояния

    def __init__(self, address, with_crc=False):
        self.__address = address    # адрес modbus
        self.__withcrc = with_crc   # добавлять ли CRC сумму
        self.commands = {           # коды команд
            CommandBuilder.TargetType.REGISTER: {
                CommandBuilder.CommandType.READ: 0x4,
                CommandBuilder.CommandType.WRITE: 0x6,
                CommandBuilder.CommandType.MULTI: 0x0
            },
            CommandBuilder.TargetType.COIL: {
                CommandBuilder.CommandType.READ: 0x1,
                CommandBuilder.CommandType.WRITE: 0x5,
                CommandBuilder.CommandType.MULTI: 0xf
            }
        }

    def build_set(self, target_type: TargetType, register: int, value: int):
        """ Создание команды записи """
        result = bytearray([
            self.__address,
            self.commands[target_type][CommandBuilder.CommandType.WRITE]
        ])
        result.extend(register.to_bytes(2, 'big'))
        result.extend(value.to_bytes(2, 'big'))

    def build_get(self, target_type: TargetType, register: int, count: int):
        """ Создание команды чтения """
        result = bytearray([
            self.__address,
            self.commands[target_type][CommandBuilder.CommandType.READ]
        ])
        result.extend(register.to_bytes(2, 'big'))
        result.extend(count.to_bytes(2, 'big'))
