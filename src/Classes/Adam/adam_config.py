"""
    Конфигурация Adam5000TCP
    имя_параметра = (слот, канал)"""
from Classes.Adam.adam_5k import SlotType, Param

IP              = '10.10.10.11'
PORT            = 502
ADDRESS         = 1

params = {
    # "имя": ((тип_слота, слот, канал), (диапазон, смещение, макс.цифр)
    # данные
    "flw0":         Param(SlotType.ANALOG, 1, 0,    1000, 0x7FFF, 0xFFFF), #1000
    "flw1":         Param(SlotType.ANALOG, 1, 0,     100, 0x7FFF, 0xFFFF), #1000
    "flw2":         Param(SlotType.ANALOG, 1, 0,      10, 0x7FFF, 0xFFFF), #80
    "rpm":          Param(SlotType.ANALOG, 1, 1,    6000, 0x7FFF, 0xFFFF), #3000
    "torque":       Param(SlotType.ANALOG, 1, 2,     2.0, 0x7FFF, 0xFFFF), #0.2
    "psi_in":       Param(SlotType.ANALOG, 1, 3,       0, 0x7FFF, 0xFFFF), #0
    "psi_out":      Param(SlotType.ANALOG, 1, 3,     7.0, 0x7FFF, 0xFFFF), #3.5
    # управление (_ в конце имени)
    "engine_":      Param(SlotType.DIGITAL, 0, 0,      0, 0x0, 0xFF00),
    "flw0_":        Param(SlotType.DIGITAL, 0, 1,      0, 0x0, 0xFF00),
    "flw1_":        Param(SlotType.DIGITAL, 0, 2,      0, 0x0, 0xFF00),
    "flw2_":        Param(SlotType.DIGITAL, 0, 3,      0, 0x0, 0xFF00),
    "valve_":       Param(SlotType.ANALOG,  2, 0,      0, 0x0, 0x0400),
    "speed_":       Param(SlotType.ANALOG,  2, 1,      0, 0x0, 0x0400),
    # ВРЕМЕННО
    "torque_":      Param(SlotType.ANALOG,  2, 2,      0, 0x0, 0x0400),
    "pressure_":    Param(SlotType.ANALOG,  2, 3,      0, 0x0, 0x0400),
}
