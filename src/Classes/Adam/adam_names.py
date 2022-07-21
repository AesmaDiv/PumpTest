"""
    Именя каналов
"""
from enum import Enum, auto


class ChannelNames(Enum):
    """Имена каналов"""
    # данные
    ALARM = auto()
    FLW_0 = auto()
    FLW_1 = auto()
    FLW_2 = auto()
    RPM = auto()
    TORQUE = auto()
    PSI_IN = auto()
    PSI_OUT = auto()
    # управление
    ENGINE = auto()
    ROTATE = auto()
    SPEED = auto()
    VLV_2 = auto()
    VLV_12 = auto()
    VLV_WTR = auto()
    VLV_AIR = auto()
    VLV_TST = auto()
    VLV_FLW = auto()
