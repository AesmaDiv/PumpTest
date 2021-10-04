"""
    Модуль описывающий классы для Испытания, Насоса и Типоразмера
"""
from Classes.Data.alchemy_tables import Type, Pump, Test


class Record():
    """ Класс-шаблон описания записи таблицы БД """
    def __init__(self, db_manager, parent_class: str, rec_id=0):
        self._db_manager = db_manager
        self._parent_class = parent_class
        self._current = None
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
        self.clear()
        query = self._db_manager.session().query(
            self._parent_class
        ).where(self._parent_class.ID == rec_id)
        if query.count():
            self._current = query.one()
            self._props = {
                k: self._current.__dict__[k] for k in self._props.keys()
            }
            return True
        return False

    def create(self) -> bool:
        """ создаёт пустую запись для таблицы БД
        -> возвращает успех """
        self._current = self._parent_class()
        table_columns = self._parent_class.__table__.columns.keys()
        if table_columns:
            self._props = dict.fromkeys(table_columns)
            return True
        return False

    def clear(self):
        """ очищает все данные в записи """
        self._current = self._parent_class()
        self._props = dict.fromkeys(self._props)

    def check_exist(self, conditions: dict=None):
        """ проверяет, существует ли запись с такими условиями """
        if not conditions:
            conditions = [{'ID': self._props['ID']}]
        items = self._db_manager.select(self._parent_class, ['ID'], conditions)
        if items:
            return items[0]['ID']
        return 0

    def save(self) -> bool:
        """ сохраняет запись в таблицу БД:
        добавляет новую и сохраняет ID или обновляет существующую
        -> возвращает успех """
        if self._ready:
            with self._db_manager.session() as session:
                self._current.__dict__.update(self._props)
                session.add(self._current)
                session.flush()
                session.refresh(self._current)
                session.commit()
                return self._current.ID > 0
        return False


class RecordType(Record):
    """ Класс информации о типоразмере """
    def __init__(self, db_manager, parent_class=Type, rec_id=0):
        super().__init__(db_manager, parent_class, rec_id)
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


class RecordPump(Record):
    """ Класс информации о насосе """
    def __init__(self, db_manager, parent_class=Pump, rec_id=0):
        super().__init__(db_manager, parent_class, rec_id)


class RecordTest(RecordType):
    """ Класс информации об испытании """
    def __init__(self, db_manager, parent_class=Test, rec_id=0):
        RecordType.__init__(self, db_manager, parent_class, rec_id)
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
