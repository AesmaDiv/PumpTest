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

    def check_exist(self, conditions: dict):
        """ проверяет, существует ли запись с такими условиями """
        items = self._db.select(self._table, 'ID', conditions)
        if items:
            return items[0]['ID']
        return 0


    def save(self) -> bool:
        """ сохраняет запись в таблицу БД:
        добавляет новую и сохраняет ID или обновляет существующую
        -> возвращает успех """
        if self._ready:
            if self._props['ID']:
                return self._db.update(self._table, self._props, {'ID': self._props['ID']})
            self._props['ID'] = self._db.insert(self._table, self._props)
            return self.ID > 0
        return False


class RecordTest(Record):
    """ Класс информации об испытании """
    def __init__(self, db: SqliteDB, rec_id=0):
        super().__init__(db, 'Tests', rec_id)


class RecordPump(Record):
    """ Класс информации о насосе """
    def __init__(self, db: SqliteDB, rec_id=0):
        super().__init__(db, 'Pumps', rec_id)


class RecordType(Record):
    """ Класс информации о типоразмере """
    def __init__(self, db: SqliteDB, rec_id=0):
        super().__init__(db, 'Types', rec_id)
