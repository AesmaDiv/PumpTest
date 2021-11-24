"""
# AesmaDiv 02.2020
# Класс для графиков. Параметры оси.
# Расчёт максимального и минимального значений по оси,
# количества делений и цены делений
"""
import math


class Axis:
    """ Класс оси """
    def __init__(self, axis_min: float = 0.0, axis_max: float = 0.0):
        keys = ['axis_min', 'axis_max', 'length', 'divs', 'price']
        self._params = dict.fromkeys(keys)
        self._divs_manually_set = False
        # если аргуметы переданы - расчет параметров оси
        if any((axis_min, axis_max)):
            self.calculate(axis_min, axis_max)

    def setMinimum(self, axis_min: float):
        """ установить минимальный предел оси """
        if self.getMaximum() > axis_min:
            self._params.update({'axis_min': axis_min})
            self.calculate(self.getMinimum(), self.getMaximum())

    def getMinimum(self):
        """ минимальный предел оси """
        return self._params['axis_min']

    def setMaximum(self, axis_max: float):
        """ установить максмальный предел оси """
        if self.getMinimum() < axis_max:
            self._params.update({'axis_max': axis_max})
            self.calculate(self.getMinimum(), self.getMaximum())

    def getMaximum(self):
        """ максимальный предел оси """
        return self._params['axis_max']

    def getLength(self):
        """ полная длина оси """
        return abs(self._params['axis_max'] - self._params['axis_min'])

    def setDivs(self, divs: int):
        """ задать количество делений на оси """
        divs = abs(divs) # должно быть положительное
        self._divs_manually_set = divs > 0
        self._params.update({'divs': divs})
        self.calculate(self.getMinimum(), self.getMaximum())

    def getDivs(self):
        """ количество делений на оси """
        return int(self._params['divs'])

    def getPrice(self):
        """ цена деления """
        return self._params['price']

    def generateDivSteps(self):
        """ генератор значений делений """
        for i in range(self.getDivs() + 1):
            result = float(i) * self._params['price'] + self._params['axis_min']
            yield i, result

    def calculate(self, axis_min: float, axis_max: float):
        """ расчёт параматров """
        params = {}
        amin, amax = Axis._fixMinMax(axis_min, axis_max)
        Axis._getLongShortLengths(amin, amax, params)
        Axis._prepareLong(params)
        if self._divs_manually_set:
            Axis._applyDivider(params, self._params['divs'])
        else:
            Axis._findDivider(params, self._params['divs'])
        Axis._finishLong(params)
        Axis._finishShort(params)
        self._assignParams(params)

    @staticmethod
    def _fixMinMax(minimal, maximal):
        """ приведение значений минимума и максимума к нужному порядку """
        if minimal > maximal:
            minimal, maximal = maximal, minimal
        return minimal, maximal

    @staticmethod
    def _getLongShortLengths(axis_min: float, axis_max: float, params):
        """ получение исходных параметров """
        # является ли максимум длинным участком
        params['long_is_max'] = abs(axis_max) > abs(axis_min)
        # сохраняю знаки для мин. и макс. (положительное или отрицательное)
        params['sign_short'] = -1 if axis_min < 0 else 1
        params['sign_long'] = -1 if axis_max < 0 else 1
        # выбираю длинный и короткий участки оси
        if params['long_is_max']:
            params['len_long'] = abs(axis_max)
            params['len_short'] = abs(axis_min)
        else:
            params['len_long'] = abs(axis_min)
            params['len_short'] = abs(axis_max)

    @staticmethod
    def _prepareLong(params):
        """ подготовка длинного участка (ключевая функция) """
        # вне зависимости от величины, значимыми являются две первые цифры
        # (0.023 - 23 или 3145.2 - 31), поэтому приводим значение к этому
        # виду и запоминаем степень 10-ти, для возврата
        value: float = params['len_long']
        pwr_of_ten, min_value, max_value = 0, 10, 100
        if value < min_value:
            while value < min_value:
                pwr_of_ten -= 1
                value *= 10
        elif value > max_value:
            while value > max_value:
                pwr_of_ten += 1
                value *= 0.1
        value = int(value + 1) if value % int(value) else int(value)
        params['len_long'] = value
        params['pwr_of_ten'] = pwr_of_ten

    @staticmethod
    def _applyDivider(params, divs=0):
        """ поиск подходящего кол-ва делений для длинного участка """
        # исходя из заданного кол-ва делений,
        # находим ближайшее большее для длины оси
        # делящееся на кол-во делений без остатка:
        value: float = params['len_long']
        while value % divs > 0:
            value += 1
        params['len_long'] = value
        params['divs'] = divs

    @staticmethod
    def _findDivider(params, divs=0):
        """ поиск подходящего кол-ва делений для длинного участка """
        value: float = params['len_long']
        if 10 < value < 100:
            value *= 1.1
            value /= 10.0
            val_min = math.floor(value)
            val_max = math.ceil(value)
            if value < (val_min + 0.5):
                params['divs'] = val_min * 2.0 + 1
                params['len_long'] = (val_min + 0.5) * 10.0
            else:
                params['divs'] = val_max
                params['len_long'] = val_max * 10.0
            if params['divs'] < 5:
                params['divs'] *= 2
        else:
            # другой вариант ::
            # перебираем делители для длины длинного участка
            # и если не подходят, то увеличиваем значение на 1
            # допустимые количества делений:
            divs = [10, 8, 5, 4]
            i = 0
            while value % divs[i] > 0:
                i += 1
                if i > len(divs) - 1:
                    i = 0
                    value += 1
            params['divs'] = divs[i]
            params['len_long'] = value

    @staticmethod
    def _finishLong(params):
        """ завершение расчёта для длинного участка """
        # возвращаем значение к прежнему виду, округляем
        # и получаем цену деления
        value: float = params['len_long']
        value *= 10 ** params['pwr_of_ten']
        params['len_long'] = round(value, abs(params['pwr_of_ten']))
        params['price'] = value / params['divs']

    @staticmethod
    def _finishShort(params):
        """ завершение расчёта для короткого участка """
        # в зависимости от знака и длины (относительно цены деления)
        # правим длину короткого участка и общее кол-во делений
        value: float = params['len_short']
        price: float = params['price']
        # если у участков одинаковый знак
        if params['sign_short'] == params['sign_long']:
            divs = value // price
            value = price * divs
            divs *= -1
        # если у участков разный знак
        else:
            divs = value // price if not value % price else value // price + 1
            value = price if value <= price else price * divs
        params['divs'] += int(divs)
        params['len_short'] = round(value, abs(params['pwr_of_ten']))

    def _assignParams(self, params):
        """ сохранение расчитанный параметров """
        if params['long_is_max']:
            self._params['axis_min'] = params['len_short']
            self._params['axis_max'] = params['len_long']
        else:
            self._params['axis_min'] = params['len_long']
            self._params['axis_max'] = params['len_short']
        self._params['axis_min'] *= params['sign_short']
        self._params['axis_max'] *= params['sign_long']
        self._params['length'] = abs(params['len_long'] - params['len_short'])
        self._params['price'] = params['price']
        self._params['divs'] = params['divs']
