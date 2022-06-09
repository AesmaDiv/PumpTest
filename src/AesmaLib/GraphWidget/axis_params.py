"""
    Модуль содержит класс, для расчёта параметров оси:
    мин.значение, макс.значение, кол-во делений, цена деления, общая длина"""
LOG = False
def log(string):
    """логирование в консоль"""
    if LOG:
        print(string)


class AxisParams:
    """Класс расчёта параметров оси"""
    DIVISIONS = (3,4,5,6,7,8,9,10)# приемлимое кол-во делений
    PRICES = (10.0,5.0,4.0,2.0) # допустимые делители
    _params = {                 # параметры оси
        'min': 0.0,             # мин.значение
        'max': 1.0,             # макс.значение
        'div': 0,               # кол-во делений
        'prc': 1.0,             # цена деления
        'len': 1                # общая длина
    }

    @staticmethod
    def calculate(vmin: float, vmax: float, divs=0):
        """расчёт параметров оси"""
        params = AxisParams._params
        # расчет длины строкового представления числа, для длины округления
        params['len'] = max(map(len, (str(vmin), str(vmax))))
        # определение большой и малой полуосей
        params['min'] = vmin if abs(vmin) < abs(vmax) else vmax
        params['max'] = vmin if abs(vmin) > abs(vmax) else vmax
        params['div'] = divs
        # расчёт
        log(f"Расчёт для {params['max']}")
        AxisParams._calculateMax()
        if all((vmin, vmax)):
            AxisParams._calculateMin()
        AxisParams._normalize()
        return params

    @staticmethod
    def _calculateMax():
        """расчет параметров большой полуоси"""
        params = AxisParams._params
        # для расчёта нужны первые две значимые цифры из числа,
        # т.е. 0.0123 -> 12, 456.78 -> 45
        # поэтому переводим число к экспоненциальному виду
        # и получаем эти две цифры и экспоненту
        sval = "{0:.1e}".format(params['max'])
        val, exp = list(map(float, sval.split('e')))
        val, exp = val * 10, exp - 1
        divs, price = params['div'], 0
        # ищем подходящее кол-во делений
        if not divs:
            val, price, divs = AxisParams._findPriceAndDivisions(val)
        else:
            val, price = AxisParams._findPrice(val, divs)
        # когда делитель найден, сохраняем параметры
        if divs:
            params['max'] = round(val * 10 ** exp, params['len'])
            params['div'] = int(divs)
            params['prc'] = round(price * 10 ** exp, params['len'])

    @staticmethod
    def _findPriceAndDivisions(value):
        """расчёт новой длинны, цены деления и кол-ва делений"""
        result = {'val': value, 'prc': value, 'div': 1.0}
        options = []    # найденные варианты
        val, limit = value, abs(value * 1.5) # текущее макс.значение и предел
        while abs(val) < limit:
            # цена деления должна быть кратна одному из допустимых значений
            val += -1 * (val < 0) + (val > 0)
            price = next(filter(lambda x: val % x == 0, AxisParams.PRICES), 0.0)
            if not price:
                continue
            # количество делений оси должно быть равно одному из допустимых
            divisions = abs(round(val / price, AxisParams._params['len']))
            if divisions in AxisParams.DIVISIONS:
                # добавляем найденный вариант в список
                result = {'val': val, 'prc': price, 'div': divisions}
                options.append(result)
        if options:
            # выбираем вариант с наименьшим макс.значением
            result = min(options, key=lambda x: abs(x['val']))
            # если кол-во делений меньше или равно 5
            # удваиваем кол-во делений и уменьшаем вдвое цену деления
            if result['div'] <= 5:
                result['div'] *= 2
                result['prc'] /= 2
        log(result)
        return result.values()

    @staticmethod
    def _findPrice(value, divisions):
        """расчёт новой длины и цены деления для заданного кол-ва делений"""
        while True:
            value += -1 * (value < 0) + (value > 0)
            price = abs(round(value / divisions, AxisParams._params['len']))
            if next(filter(lambda x: price % x == 0, AxisParams.PRICES), 0):
                break
        return value, price

    @staticmethod
    def _calculateMin():
        """расчёт параметров малой полуоси"""
        params = AxisParams._params
        sign_min = -1 if params['min'] < 0 else 1
        sign_max = -1 if params['max'] < 0 else 1
        # расчёт кол-ва делений
        divider = int(abs(params['min']) // params['prc'])
        # если оба значения на одной стороне полуоси..
        if sign_min == sign_max:
            params['div'] -= divider
        # если на разных..
        else:
            divider += 1
            params['div'] += divider
        params['min'] = round(params['prc'] * divider * sign_min, params['len'])

    @staticmethod
    def _normalize():
        """нормализация"""
        params = AxisParams._params
        # правильный порядок большего и меньшего края оси
        if params['min'] > params['max']:
            params['min'], params['max'] = params['max'], params['min']
        # полная длина оси
        params['len'] = params['max'] - params['min']

if __name__ == "__main__":
    axes = [
        (-2.2, -1.1),
        (-1.1, -2.2),
        (-1.1, 2.2),
        (1.1, 2.1),
        (0, 0.0123),
        (-0.0123, 0),
        (23.345, 45.678),
        (1023.12, 1245.56)
    ]
    func = lambda x, y, r: round(x['min'] + y * x['prc'], r)
    for axis in axes:
        prms = AxisParams.calculate(*axis)
        print(f"{axis}\n{prms}")
        str_len = max(map(len, (str(prms['min']), str(prms['max']))))
        print([func(prms, x, str_len) for x in range(prms['div'] + 1)])
