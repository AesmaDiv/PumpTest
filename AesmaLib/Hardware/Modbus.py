from enum import Enum


class Modbus:
    class CommandType(Enum):
        READ = 0,
        WRITE = 1,
        MULTI = 2

    class TargetType(Enum):
        REGISTER = 0,
        COIL = 1

    def __init__(self, address, with_crc=False):
        self.__address = address
        self.__withcrc = with_crc
        self.commands = {
            Modbus.TargetType.REGISTER: {
                Modbus.CommandType.READ: 0x4,
                Modbus.CommandType.WRITE: 0x6,
                Modbus.CommandType.MULTI: 0x0
            },
            Modbus.TargetType.COIL: {
                Modbus.CommandType.READ: 0x1,
                Modbus.CommandType.WRITE: 0x5,
                Modbus.CommandType.MULTI: 0xf
            }
        }

    def buildCommand_Set(self, target_type: TargetType, address: int, value: int):
        result = bytearray([
            self.__address,
            self.commands[target_type][Modbus.CommandType.WRITE]
        ])
        result.extend(address.to_bytes(2, 'big'))
        result.extend(value.to_bytes(2, 'big'))

    def buildCommand_Get(self, target_type: TargetType, address: int, count: int):
        result = bytearray([
            self.__address,
            self.commands[target_type][Modbus.CommandType.READ]
        ])
        result.extend(address.to_bytes(2, 'big'))
        result.extend(count.to_bytes(2, 'big'))

