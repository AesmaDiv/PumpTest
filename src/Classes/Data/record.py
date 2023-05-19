"""
    Модуль описывающий классы для Испытания, Насоса и Типоразмера
"""
from dataclasses import dataclass, field
from loguru import logger
import sqlalchemy as sql
import numpy as np

from Classes.Data.db_tables import Type, Test


@dataclass
class Point:
    """структура хранения данных о точках"""
    Flw: float
    Lft: float
    Pwr: float
    Eff: float


@dataclass
class TestData:
    """Класс для полной информации об испытании"""
    def __init__(self) -> None:
        self.test_ = RecordTest()
        self.type_ = RecordType()
        self.dlts_ = field(default_factory=dict)

    def clear(self):
        """очистка информации о записи"""
        logger.debug(self.clear.__doc__)
        self.test_.clear()
        self.type_.clear()
        self.dlts_ = {}

    def load(self, data: list):
        """парсинг данных полученных из БД"""
        logger.debug(self.load.__doc__)
        if data and len(data) == 3:
            self.test_.load(data[0])
            self.type_.load(data[1])
            self.type_.ProducerName = data[2]['Name']


class Record():
    """Класс-шаблон описания записи таблицы БД"""
    subclass = None
    def __init__(self, rec_id=0):
        self._props = {}
        _ = self.read(rec_id) if rec_id else self.create()

    def __getitem__(self, key) -> any:
        """возвращает значение поля записи по имени"""
        return self._props[key] if key in self._props else None

    def __setitem__(self, key, value):
        """задает значение поля записи по имени"""
        if key in self._props:
            self._props[key] = value

    def __getattr__(self, name) -> any:
        """предоставляет доступ к полю записи по имени"""
        return self.__getitem__(name)

    def keys(self):
        ''' возвращает список имен столбцов '''
        return self._props.keys()

    def values(self):
        ''' возвращает список значений столбцов '''
        return self._props.values()

    def items(self):
        ''' возвращает список элементы столбцов '''
        return self._props.items()

    def load(self, props: dict):
        """парсинг данных"""
        if props:
            self._props = {k: props[k] for k in self._props.keys()}
            return True
        return False

    def create(self) -> bool:
        """создаёт пустую запись для таблицы БД
        -> возвращает успех"""
        self._current = self.subclass
        table_columns = self.subclass.__table__.columns.keys()
        if table_columns:
            self._props = dict.fromkeys(table_columns)
            return True
        return False

    def clear(self):
        """очищает все данные в записи"""
        self._props = dict.fromkeys(self._props)

    def checkExists(self, conditions: dict=None):
        """проверяет, существует ли запись с такими условиями"""
        if not conditions:
            conditions = [{'ID': self._props['ID']}]
        def func(**kwargs):
            result = kwargs['session'].select(self.subclass, ['ID'], conditions)
            return result
        items = self._db_manager.execute(func)
        if items:
            return items[0]['ID']
        return 0

    def write(self) -> bool:
        """сохраняет запись в таблицу БД:
        добавляет новую и сохраняет ID или обновляет существующую
        -> возвращает успех"""
        def func(**kwargs):
            data = self._props.copy()
            id_ = data.pop('ID')
            item = kwargs['session'].query(self.subclass).get(id_) if id_ else self.subclass
            for k in data.keys():
                setattr(item, k, data[k])
            kwargs['session'].add(item)
            try:
                kwargs['session'].commit()
                self._props.update({'ID': item.ID })
            except sql.exc.IntegrityError:
                return False
            return item.ID > 0
        return self._db_manager.execute(func)


class RecordType(Record):
    """Класс информации о типоразмере"""
    subclass=Type
    def __init__(self, rec_id=0):
        super().__init__(rec_id)
        self.points = []
        if self.__class__ is RecordType:
            self.ProducerName = ""

    def load(self, props: dict):
        if not super().load(props):
            return False
        if self.Flows and self.Lifts and self.Powers:
            # парсим строки значений в массивы и приводим к общей длинне
            points = {
                'flws': list(map(float, self.Flows.split(','))),
                'lfts': list(map(float, self.Lifts.split(','))),
                'pwrs': list(map(float, self.Powers.split(',')))
            }
            RecordType._normalize(points)
            # транспонируем и рассчитываем КПД
            points = np.array(list(points.values())).T
            points = sorted(points, key=lambda x: x[0])
            points = np.column_stack((points, RecordType.calculate_effs(points)))
            # создаем данные о точках
            self.points = [Point(p[0], p[1], p[2], p[3]) for p in points]
        else:
            self._clear()
        return True

    def clear(self):
        """полная очистка информации о типоразмере"""
        self._clear()
        return super().clear()

    @staticmethod
    def calculate_effs(points: np.ndarray):
        """расчёт точек КПД"""
        def func(f, l, p):
            return 9.81 * l * f / (24 * 3600 * p) * 100 if f and l and p else 0
        result = [func(flw, lft, pwr) for flw, lft, pwr in points]
        return result

    @staticmethod
    def _normalize(points: dict):
        """приведение к общей длинне"""
        new_len = min(map(len, points.values()))
        for key, values in points.items():
            points[key] = values[:new_len]

    def _clear(self):
        """очистка точек кривой и производителя"""
        self.points  = []
        if self.__class__ is RecordType:
            self.ProducerName = ""


class RecordTest(RecordType):
    """Класс информации об испытании"""
    subclass=Test
    def __init__(self, rec_id=0):
        super().__init__(rec_id)
        self.values_vbr = []

    def load(self, props: dict) -> bool:
        """загружает запись из таблицы БД по ID
        -> возвращает успех"""
        if not super().load(props):
            return False
        if self.Vibrations:
            self.values_vbr = list(map(float, self.Vibrations.split(',')))
        else:
            self.values_vbr = []
        return True
