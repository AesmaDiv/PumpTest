"""
    Конфигурация Adam5000TCP
    имя_параметра = (слот, канал)
"""
from Classes.Adam.adam_5k import SlotType, Param
from Classes.Adam.adam_names import ChannelNames


IP              = '10.10.10.10'
PORT            = 502
ADDRESS         = 1

PARAMS = {
    # "имя": ((тип_слота, слот, канал), (диапазон, смещение, макс.цифр)
    # данные
    ChannelNames.ALARM:   Param(SlotType.DIGITAL, 3, 0,     0, 0x0000, 0xFF00), # аварийный стоп 0 - отжата <> 1 - нажата
    ChannelNames.FLW_0:   Param(SlotType.ANALOG,  0, 0,  1000, 0x7FFF, 0xFFFF), # расходомер 0.5"
    ChannelNames.FLW_1:   Param(SlotType.ANALOG,  0, 7,   100, 0x7FFF, 0xFFFF), # расходомер 1"
    ChannelNames.FLW_2:   Param(SlotType.ANALOG,  0, 2,    10, 0x7FFF, 0xFFFF), # расходомер 2"
    ChannelNames.RPM:     Param(SlotType.ANALOG,  0, 6,  6000, 0x7FFF, 0xFFFF), # скорость вращения
    ChannelNames.TORQUE:  Param(SlotType.ANALOG,  0, 5,     1, 0x7FFF, 0xFFFF), # крутящий момент
    ChannelNames.PSI_IN:  Param(SlotType.ANALOG,  0, 3,     0, 0x7FFF, 0xFFFF), # давление на входе
    ChannelNames.PSI_OUT: Param(SlotType.ANALOG,  0, 4,   7.0, 0x7FFF, 0xFFFF), # давление на выходе
    # управление (_ в конце имени)
    ChannelNames.ENGINE:  Param(SlotType.DIGITAL, 2, 0,     0, 0x0000, 0xFF00), # гл.привод 0 - выкл <> 1 - вкл
    ChannelNames.ROTATE:  Param(SlotType.DIGITAL, 2, 1,     0, 0x0000, 0xFF00), # напр. вращения 0 - пр(отч) <> 1 - л(брж)
    ChannelNames.SPEED:   Param(SlotType.ANALOG,  1, 3,  3000, 0x0000, 0x0FFF), # частотник
    ChannelNames.VLV_2:   Param(SlotType.DIGITAL, 2, 3,     0, 0x0000, 0xFF00), # кран 0 - 2" <> 1 - 1"(0.5")
    ChannelNames.VLV_12:  Param(SlotType.DIGITAL, 2, 4,     0, 0x0000, 0xFF00), # кран 0 - 1" <> 1 - 0.5"
    ChannelNames.VLV_WTR: Param(SlotType.DIGITAL, 2, 6,     0, 0x0000, 0xFF00), # клапан вода 0 - закр <> 1 - откр
    ChannelNames.VLV_AIR: Param(SlotType.DIGITAL, 2, 7,     0, 0x0000, 0xFF00), # клапан воздух 0 - закр <> 1 - откр
    ChannelNames.VLV_TST: Param(SlotType.DIGITAL, 2, 2,     0, 0x0000, 0xFF00), # клапан 0 - обкатка <> 1 - тест
    ChannelNames.VLV_FLW: Param(SlotType.ANALOG,  1, 0,  4095, 0x0000, 0x0FFF), # клапан расхода
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
