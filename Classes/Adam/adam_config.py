"""
    Конфигурация Adam5000TCP
    имя_параметра = (слот, канал)
"""
from Classes.Adam.adam_5k import SlotType, Param

IP              = '10.10.10.11'
PORT            = 502
ADDRESS         = 1

params = {
    # "имя": ((тип_слота, слот, канал), (диапазон, смещение, макс.цифр)
    # данные
    "torque":       Param(SlotType.ANALOG, 2, 0,    1000, 0x0, 0x0FFF),
    "pressure_in":  Param(SlotType.ANALOG, 2, 1,    1000, 0x0, 0x0FFF),
    "pressure_out": Param(SlotType.ANALOG, 2, 2,    1000, 0x0, 0x0FFF),
    "rpm":          Param(SlotType.ANALOG, 2, 3,    1000, 0x0, 0x0FFF),
    "flw0":        Param(SlotType.ANALOG, 2, 0,    1000, 0x0, 0x0FFF),
    "flw1":         Param(SlotType.ANALOG, 2, 1,    1000, 0x0, 0x0FFF),
    "flw2":         Param(SlotType.ANALOG, 2, 2,    1000, 0x0, 0x0FFF),
    # управление
    "engine":       Param(SlotType.DIGITAL, 0, 1,      0, 0x0, 0xFF00),
    "valve":        Param(SlotType.ANALOG,  2, 0,      0, 0x0, 0xFFFF),
    "speed":        Param(SlotType.ANALOG,  2, 1,      0, 0x0, 0xFFFF)
}
