"""
    Модуль описывающий классы для Испытания, Насоса и Типоразмера
"""
from AesmaLib.database import SqliteDB


class Record():
    """ Класс-шаблон описания записи таблицы БД """
    def __init__(self, db: SqliteDB, table: str, rec_id=0):
        self._db = db
        self._table = table
        self._props = {}
        self._ready = self.load(rec_id) if rec_id else self.create()

    def __getitem__(self, key) -> any:
        """ возвращает значение поля записи по имени """
        return self._props[key] if key in self._props else None

    def __setitem__(self, key, value):
        """ задает значение поля записи по имени """
        if key in self._props:
            self._props[key] = value

    def __getattr__(self, name) -> any:
        """ предоставляет доступ к полю записи по имени """
        if name in self._props:
            return self._props[name]
        return None

    def keys(self):
        ''' возвращает список имен столбцов '''
        return self._props.keys()

    def values(self):
        ''' возвращает список значений столбцов '''
        return self._props.values()

    def items(self):
        ''' возвращает список имен столбцов '''
        return self._props.items()

    def load(self, rec_id) -> bool:
        """ загружает запись из таблицы БД по ID
        -> возвращает успех """
        items = self._db.select(self._table, '*', {'ID': rec_id})
        if items:
            self._props = items[0]
            return True
        return False

    def create(self) -> bool:
        """ создаёт пустую запись для таблицы БД
        -> возвращает успех """
        query = f'Select name from pragma_table_info("{self._table}")'
        table_columns = self._db.execute_with_retval(query)
        if table_columns:
            keys = [item['name'] for item in table_columns]
            self._props = dict.fromkeys(keys)
            return True
        return False

    def clear(self):
        """ очищает все данные в записи """
        self._props = dict.fromkeys(self._props)

    def check_exist(self, conditions: dict=None):
        """ проверяет, существует ли запись с такими условиями """
        if not conditions:
            conditions = [{'ID': self._props['ID']}]
        items = self._db.select(self._table, ['ID'], conditions)
        if items:
            return items[0]['ID']
        return 0

    def save(self) -> bool:
        """ сохраняет запись в таблицу БД:
        добавляет новую и сохраняет ID или обновляет существующую
        -> возвращает успех """
        if self._ready:
            if self._props['ID']:
                return self._db.update(self._table, self._props,
                                       {'ID': self._props['ID']})
            self._props['ID'] = self._db.insert(self._table, self._props)
            return self.ID > 0
        return False


class RecordPump(Record):
    """ Класс информации о насосе """
    def __init__(self, db: SqliteDB, table='Pumps', rec_id=0):
        super().__init__(db, table, rec_id)


class RecordType(Record):
    """ Класс информации о типоразмере """
    def __init__(self, db: SqliteDB, table='Types', rec_id=0):
        super().__init__(db, table, rec_id)
        self.values_vbr = []
        self.values_flw = []
        self.values_lft = []
        self.values_pwr = []

    def load(self, rec_id) -> bool:
        """ загружает запись из таблицы БД по ID
        -> возвращает успех """
        result = super().load(rec_id)
        if result:
            if self.Flows and self.Lifts and self.Powers:
                self.values_flw = list(map(float, self.Flows.split(',')))
                self.values_lft = list(map(float, self.Lifts.split(',')))
                self.values_pwr = list(map(float, self.Powers.split(',')))
                self.values_eff = RecordType.calculate_effs(
                    self.values_flw, self.values_lft, self.values_pwr
                )
            else:
                self.values_flw = []
                self.values_lft = []
                self.values_pwr = []
                self.values_eff = []
        return result

    @staticmethod
    def calculate_effs(flws: list, lfts: list, pwrs: list):
        """ расчёт точек КПД """
        result = []
        count = len(flws)
        if count == len(lfts) and count == len(pwrs):
            result = [RecordType.calculate_eff(flws[i], lfts[i], pwrs[i]) \
                    for i in range(count)]
        return result

    @staticmethod
    def calculate_eff(flw: float, lft: float, pwr: float):
        """ вычисление КПД """
        return 9.81 * lft * flw / (24 * 3600 * pwr) * 100 \
            if flw and lft and pwr else 0

    def num_points(self) -> int:
        """ проверяет есть ли точки и возвращает их количество (наименьшее) """
        if self.values_flw and self.values_lft and self.values_pwr:
            num_flw = len(self.values_flw)
            num_lft = len(self.values_lft)
            num_pwr = len(self.values_pwr)
            return min(num_flw, num_lft, num_pwr)
        return 0


class RecordTest(RecordType):
    """ Класс информации об испытании """
    def __init__(self, db: SqliteDB, table='Tests', rec_id=0):
        RecordType.__init__(self, db, table, rec_id)
        self.values_vbr = []

    def load(self, rec_id) -> bool:
        """ загружает запись из таблицы БД по ID
        -> возвращает успех """
        result = super().load(rec_id)
        if result:
            if self.Vibrations:
                self.values_vbr = list(map(float, self.Vibrations.split(',')))
            else:
                self.values_vbr = []
        return result

class TestInfo:
    """ Класс для полной информации об испытании """
    def __init__(self, db) -> None:
        self.type_ = RecordType(db)
        self.pump_ = RecordPump(db)
        self.test_ = RecordTest(db)
        self.dlts_ = {}
