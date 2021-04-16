
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline


class GraphData:
    def __init__(self, flw:list, lft: list, pwr: list, line_style = '-'):
        _flw, _lft, _pwr = flw, lft[::-1], pwr[::-1]
        _clr = [clr+line_style for clr in ('k', 'b', 'r', 'g')]
        self._data = {
            'flw': {'spln': None, 'vals': _flw, 'color': _clr[0]},
            'lft': {'spln': None, 'vals': _lft, 'color': _clr[1]},
            'pwr': {'spln': None, 'vals': _pwr, 'color': _clr[2]},
            'eff': {'spln': None, 'vals': self.calculate_effs(
                _flw, _lft, _pwr), 'color': _clr[3]}
        }
        self._create_splines()

    def vals(self, name):
        return self._data[name]['vals'] if name in self._data else None

    def spline(self, name):
        return self._data[name]['spln'] if name in self._data else None

    def color(self, name):
        return self._data[name]['color'] if name in self._data else 'k'

    def _create_values(self, strs_of_vals: dict):
        for key in self._data:
            if not key == 'eff':
                vals = self.parse_values(strs_of_vals[key], not key == 'flw')
                self._data[key].update({'vals': vals})
            else:
                self._data[key].update({'vals': self.calculate_effs(
                    self.vals('flw'),
                    self.vals('lft'),
                    self.vals('pwr')
                )})

    def _create_splines(self):
        for key in ('lft', 'pwr', 'eff'):
            self._data[key].update({'spln': CubicSpline(
                self.vals('flw'),
                self.vals(key)
            )})

    @staticmethod
    def parse_values(str_of_vals, do_reverse):
        result = [float(val) for val in str_of_vals.split(',')]
        return result if not do_reverse else result[::-1]

    @staticmethod
    def calculate_effs(flw: list, lft: list, pwr: list):
        result = []
        count = len(flw)
        if count == len(lft) and count == len(pwr):
            for i in range(count):
                N = 9.81 * lft[i] * flw[i] / (24 * 3600)
                eff = N / pwr[i]
                # eff = flows[i] * lifts[i] / (136000 * powers[i]) * 100
                result.append(eff * 100)
        return result


class PumpGraph:
    def __init__(self):
        self._plots = {
            'lft':{
                'canvas': None,
                'curve': None,
                'label': 'Напор, м',
                'color': 'b',
                'limit': 1.1
            },
            'pwr':{
                'canvas': None,
                'curve': None,
                'label': 'Мощность, кВт',
                'color': 'r',
                'limit': 1.2
            },
            'eff':{
                'canvas': None,
                'curve': None,
                'label': 'КПД, %',
                'color': 'g',
                'limit': 1.8
            }
        }
        figure, self._plots['lft']['canvas'] = plt.subplots()
        figure.subplots_adjust(
            left=0.09, top=0.98, right=0.70)
        self._plots['pwr']['canvas'] = self._plots['lft']['canvas'].twinx()
        self._plots['eff']['canvas'] = self._plots['lft']['canvas'].twinx()
        self._plots['eff']['canvas'].spines.right.set_position(("axes", 1.3))

    def create_cubic_splines(self, pump_graph_data: GraphData):
        pgd = pump_graph_data
        rng = np.linspace(0, max(pgd.vals('flw')), 100)
        for name, item in self._plots.items():
            curves = item['canvas'].plot(
                rng, pgd.spline(name)(rng), pgd.color(name))
            item['curve'] = curves[0] if curves else None

    def setup_plots(self, pump_graph_data: GraphData):
        pgd = pump_graph_data
        tkw = dict(size=4, width=1.5)
        axis_x = self._plots['lft']['canvas']
        axis_x.set_xlabel('Расход, м³/сутки')
        axis_x.set_xlim(0, max(pgd.vals('flw')) * 1.1)
        axis_x.tick_params(axis='x', **tkw)
        for name, item in self._plots.items():
            item['canvas'].set_ylabel(item['label'])
            item['canvas'].set_ylim(0, max(pgd.vals(name)) * item['limit'])
            item['canvas'].yaxis.label.set_color(item['color'])
            item['canvas'].tick_params(axis='y', colors=item['color'], **tkw)

    def clear_data(self):
        for item in self._plots.values():
            item['curve'] = None

    def set_nominal(self, min: float, nom: float, max: float):
        axis_x = self._plots['lft']['canvas']
        axis_x.axvline(linestyle='--', color='k', x=min)
        axis_x.axvline(linestyle='--', color='k', x=nom)
        axis_x.axvline(linestyle='--', color='k', x=max)
        axis_x.grid(linestyle='--', linewidth=0.5, color='k')


data = {
    'flw': [0.0,10.3333,20.6667,31.0,41.3333,51.6667,62.0],
    'lft': [0.0,1.1165,2.101,2.718,3.0988,3.2432,3.2957],
    'pwr': [0.0306,0.0292,0.0275,0.0261,0.024,0.0218,0.0189]
}
dtat = {
    'flw': [0.0,9.3333,19.6667,30.0,40.3333,50.6667,61.0],
    'lft': [0.0,0.1165,1.101,1.718,2.0988,2.2432,2.2957],
    'pwr': [0.0206,0.0192,0.0175,0.0161,0.014,0.0118,0.0089]
}

pump_graph = PumpGraph()
graph_data = GraphData(**data, line_style=':')
graph_dtat = GraphData(**dtat)
pump_graph.create_cubic_splines(graph_data)
pump_graph.create_cubic_splines(graph_dtat)
pump_graph.setup_plots(graph_data)
pump_graph.set_nominal(20, 30, 40)
plt.show()
pass
