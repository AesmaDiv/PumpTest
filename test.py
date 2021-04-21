import math


def nice_number(value, round_=False):
    '''nice_number(value, round_=False) -> float'''
    exponent = math.floor(math.log(value, 10))
    fraction = value / 10 ** exponent

    if round_:
        if fraction < 1.5:
            nice_fraction = 1.
        elif fraction < 3.:
            nice_fraction = 2.
        elif fraction < 7.:
            nice_fraction = 5.
        else:
            nice_fraction = 10.
    else:
        if fraction <= 1:
            nice_fraction = 1.
        elif fraction <= 2:
            nice_fraction = 2.
        elif fraction <= 5:
            nice_fraction = 5.
        else:
            nice_fraction = 10.

    return nice_fraction * 10 ** exponent


def nice_bounds(axis_start, axis_end, num_ticks=10):
    '''
    nice_bounds(axis_start, axis_end, num_ticks=10) -> tuple
    @return: tuple as (nice_axis_start, nice_axis_end, nice_tick_width)
    '''
    axis_width = axis_end - axis_start
    if axis_width == 0:
        nice_tick = 0
    else:
        nice_range = nice_number(axis_width)
        nice_tick = nice_number(nice_range / (num_ticks - 1), round_=True)
        axis_start = math.floor(axis_start / nice_tick) * nice_tick
        axis_end = math.ceil(axis_end / nice_tick) * nice_tick

    return axis_start, axis_end, nice_tick


def calc():
    AxisStart = 0
    AxisEnd   = 0.12283
    NumTicks  = 10

    AxisWidth = AxisEnd - AxisStart
    if (AxisWidth == 0.0):
        return (0.0)

    NiceRange = nice_number(AxisEnd - AxisStart, 0)
    NiceTick = nice_number(NiceRange/(NumTicks - 1), 1)

    NewAxisStart = math.floor(AxisStart/NiceTick)*NiceTick
    NewAxisEnd = math.ceil(AxisEnd/NiceTick)*NiceTick

    AxisStart = NewAxisStart
    AxisEnd = NewAxisEnd

    return(NewAxisStart, NewAxisEnd, NiceTick)

print(calc())