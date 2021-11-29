class AxisParams:
    DIVIDERS = (10,8,7,6,5,4)
    _params = {
        'min': 0.0,
        'max': 1.0,
        'div': 1,
        'prc': 1.0,
        'len': 1
    }

    @staticmethod
    def calculate(v0: float, v1: float):
        params = AxisParams._params
        params['len'] = max(map(len, (str(v0), str(v1))))
        params['min'] = v0 if abs(v0) < abs(v1) else v1
        params['max'] = v0 if abs(v0) > abs(v1) else v1
        AxisParams._calculateMax()
        if all((v0, v1)):
            AxisParams._calculateMin()
        AxisParams._normalize()
        return params

    @staticmethod
    def _calculateMax():
        params = AxisParams._params
        sval = "{0:.1e}".format(params['max'])
        val, exp = list(map(float, sval.split('e')))
        val, exp = val * 10, exp - 1
        found, divider = False, 0
        while not found:
            val += -1 * (val < 0) + (val > 0)
            for div in AxisParams.DIVIDERS:
                found = (val % div == 0)
                if found:
                    divider = div
                    break
        if divider:
            params['max'] = round(val * 10 ** exp, params['len'])
            params['div'] = int(divider)
            params['prc'] = abs(round(params['max'] / divider, params['len']))

    @staticmethod
    def _calculateMin():
        params = AxisParams._params
        sign_min = -1 if params['min'] < 0 else 1
        sign_max = -1 if params['max'] < 0 else 1
        divider = int(abs(params['min']) // params['prc'])
        if sign_min == sign_max:
            params['div'] -= divider
        else:
            divider += 1
            params['div'] += divider
        params['min'] = round(params['prc'] * divider * sign_min, params['len'])

    @staticmethod
    def _normalize():
        params = AxisParams._params
        if params['min'] > params['max']:
            params['min'], params['max'] = params['max'], params['min']
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
        params = AxisParams.calculate(*axis)
        print(f"{axis}\n{params}")
        len = max(map(len, (str(params['min']), str(params['max']))))
        print([func(params, x, len) for x in range(params['div'] + 1)])
