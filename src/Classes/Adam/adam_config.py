"""
    Конфигурация Adam5000TCP
    имя_параметра = (слот, канал)
"""
from Classes.Adam.adam_5k import SlotType, Param
from Classes.Adam.adam_names import ChannelNames


IP              = '127.0.0.1'
PORT            = 502
ADDRESS         = 1

PARAMS = {
    # "имя": ((тип_слота, слот, канал), (диапазон, смещение, макс.цифр)
    # данные
    ChannelNames.ALARM:   Param(SlotType.DIGITAL, 3, 0,     0, 0x0000, 0xFF00), # 0 - отжата <> 1 - нажата
    ChannelNames.FLW_0:   Param(SlotType.ANALOG,  0, 0,   203, 0x0000, 0xFFFF),
    ChannelNames.FLW_1:   Param(SlotType.ANALOG,  0, 1,   269, 0x0000, 0xFFFF),
    ChannelNames.FLW_2:   Param(SlotType.ANALOG,  0, 2,  2054, 0x0000, 0xFFFF),
    ChannelNames.RPM:     Param(SlotType.ANALOG,  0, 6, 20000, 0x7FFF, 0xFFFF),
    ChannelNames.TORQUE:  Param(SlotType.ANALOG,  0, 5, 10000, 0x7FFF, 0xFFFF),
    ChannelNames.PSI_IN:  Param(SlotType.ANALOG,  0, 7,    87, 0x0000, 0xFFFF),
    ChannelNames.PSI_OUT: Param(SlotType.ANALOG,  0, 4,  6000, 0x0000, 0xFFFF),
    # управление (_ в конце имени)
    ChannelNames.ENGINE:  Param(SlotType.DIGITAL, 2, 0,     0, 0x0000, 0xFF00), # 0 - выкл <> 1 - вкл
    ChannelNames.ROTATE:  Param(SlotType.DIGITAL, 2, 1,     0, 0x0000, 0xFF00), # 0 - пр(отч) <> 1 - лв(брж)
    ChannelNames.SPEED:   Param(SlotType.ANALOG,  1, 0,  3000, 0x0000, 0x0FFF),
    ChannelNames.VLV_2:   Param(SlotType.DIGITAL, 2, 3,     0, 0x0000, 0xFF00), # 0 - 2" <> 1 - 1"(0.5")
    ChannelNames.VLV_1:   Param(SlotType.DIGITAL, 2, 4,     0, 0x0000, 0xFF00), # 0 - 1" <> 1 - 0.5"
    ChannelNames.VLV_WTR: Param(SlotType.DIGITAL, 2, 6,     0, 0x0000, 0xFF00), # 0 - закр <> 1 - откр
    ChannelNames.VLV_AIR: Param(SlotType.DIGITAL, 2, 7,     0, 0x0000, 0xFF00), # 0 - закр <> 1 - откр
    ChannelNames.VLV_TST: Param(SlotType.DIGITAL, 2, 2,     0, 0x0000, 0xFF00), # 0 - обкатка <> 1 - тест
    ChannelNames.VLV_FLW: Param(SlotType.ANALOG,  1, 1,  4095, 0x0000, 0x0FFF),
}

COEFS = {
    ChannelNames.FLW_0:   1.0,
    ChannelNames.FLW_1:   1.0,
    ChannelNames.FLW_2:   1.0,
    ChannelNames.RPM:     1.0,
    ChannelNames.TORQUE:  1.0,
    ChannelNames.PSI_IN:  1.0,
    ChannelNames.PSI_OUT: 1.0
}
