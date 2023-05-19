"""
    Именя каналов
"""
from enum import Enum, auto


class ChannelNames(Enum):
    """Имена каналов"""
    # данные
    ALARM = auto()
    '''аварийный стоп'''
    FLW_0 = auto()
    '''расходомер 0.5"'''
    FLW_1 = auto()
    '''расходомер 1"'''
    FLW_2 = auto()
    '''расходомер 2"'''
    RPM = auto()
    '''скорость вращения'''
    TORQUE = auto()
    '''крутящий момент'''
    PSI_IN = auto()
    '''давление на входе'''
    PSI_OUT = auto()
    '''давление на выходе'''
    # управление
    
    ENGINE = auto()
    '''гл.привод'''
    ROTATE = auto()
    '''напр. вращения'''
    SPEED = auto()
    '''частотник'''
    VLV_2 = auto()
    '''кран 0 - 2"'''
    VLV_1 = auto()
    '''кран 0 - 1"'''
    VLV_WTR = auto()
    '''клапан вода'''
    VLV_AIR = auto()
    '''клапан воздух'''
    VLV_TST = auto()
    '''клапан обкатка/тест'''
    VLV_FLW = auto()
    '''клапан расхода'''