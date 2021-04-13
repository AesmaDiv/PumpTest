""" Created by AesmaDiv 2021
    Module containing classes to work with databases:
        Database - Interface for DB classes
        SqliteDB - Sqlite3 database class
        SqlQueryBuilder - class for building sql query from parameters
"""
import sqlite3
from os import path
from AesmaLib.decorators import Singleton


def connect_execute_disconnect(func):
    """ Декоратор для функции (подключиться)(выполнить)(отключиться) """
    def wrapped(self, *args, **kwargs):
        result = None
        if self.connect():
            result = func(self, *args, **kwargs)
            self.disconnect()
        return result
    return wrapped


class QueryParams():
    """ Класс параметров SQL запросов, принимает:\n
        table: str - имя таблицы ('table')\n
        columns: list - список столбцов для выбора ['ID','Name']\n
        conditions: list(dict) - список условий для Where X=Y [{'X': Y}]\n
        order_by: str - сотрировка для Order by 'X Asc'
    """
    def __init__(self, table: str, columns: list=None,
                 conditions: list=None, order_by: str=None):
        self._attrs = {
           'table': table,
           'columns': columns if columns else [],
           'conditions': conditions if conditions else [],
           'order_by': order_by if order_by else None
       }

    def __getattr__(self, name) -> any:
        """ предоставляет доступ к полю аттрибутов класса """
        if name in self._attrs:
            return self._attrs[name]
        return None


class Database(metaclass=Singleton):
    """ Интерфейс для классов баз данных """
    def connect(self, db_path: str='') -> bool:
        """ подключение к бд """

    def disconnect(self):
        """ отключение от бд """

    def select_qp(self, query_params: QueryParams) -> list:
        """ возвращает список записей из БД """

    def select(self, table: str, columns: list=None,
               conditions: dict=None, order_by:str='') -> list:
        """ возвращает список записей из БД """

    def insert(self, table: str, record: dict) -> int:
        """ вставляет новую запись в БД и возвращает её номер """

    def update(self, table: str, record: dict, conditions: dict=None) -> bool:
        """ обновляет запись в БД и возвращает успех """

    def delete(self, table: str, conditions: dict) -> bool:
        """ удаляет запись из БД и возвращает успех """

    def execute(self, query: str) -> bool:
        """ выполняет SQL запрос и возвращает успех """


class SqliteDB(Database):
    """ Класс для Sqlite3 баз данных """
    def __init__(self, db_path:str=''):
        self._is_connected = False
        self._connection = None
        self._cursor = None
        self._db_path = db_path
        self._builder = SqlQueryBuilder()

    def set_path(self, db_path: str):
        """ задает путь к файлу БД """
        self._db_path = db_path

    def connect(self, db_path="") -> bool:
        """ подключение к БД """
        if not self._is_connected:
            if self._check_db_path(db_path):
                self._connection = sqlite3.connect(self._db_path)
                self._connection.row_factory = sqlite3.Row
                self._cursor = self._connection.cursor()
                self._is_connected = True
        return self._is_connected

    def disconnect(self):
        """ отключение от БД """
        if self._is_connected:
            self._cursor = None
            self._connection.close()
            self._is_connected = False

    @connect_execute_disconnect
    def select_qp(self, query_params: QueryParams) -> list:
        """ возвращает список записей из БД """
        result = []
        query = self._builder.build_select_qp(query_params)
        if self.execute(query):
            records = self._cursor.fetchall()
            result = [dict(row) for row in records]
        return result

    @connect_execute_disconnect
    def select(self, table: str, columns: list=None,
               conditions: dict=None, order_by: str='') -> list:
        """ возвращает список записей из БД """
        query_params = QueryParams(table, columns, conditions, order_by)
        return self.select_qp(query_params)

    @connect_execute_disconnect
    def insert(self, table: str, record: dict) -> int:
        """ вставляет новую запись в БД и возвращает её номер """
        query = self._builder.build_insert(table, record)
        return self._cursor.lastrowid if self.execute(query) else 0

    @connect_execute_disconnect
    def update(self, table: str, record: dict, conditions: dict=None) -> bool:
        """ обновляет запись в БД и возвращает успех """
        query = self._builder.build_update(table, record, conditions)
        return self.execute(query)

    @connect_execute_disconnect
    def delete(self, table: str, conditions: dict) -> bool:
        """ удаляет запись из БД и возвращает успех """
        query = self._builder.build_delete(table, conditions)
        return self.execute(query)

    @connect_execute_disconnect
    def execute_with_retval(self, query: str):
        """ выполняет SQL запрос и возвращает результат выполнения """
        result = None
        if self.execute(query):
            records = self._cursor.fetchall()
            result = [dict(row) for row in records]
        return result


    def execute(self, query: str) -> bool:
        """ выполняет SQL запрос и возвращает успех """
        try:
            self._cursor.execute(query)
            self._connection.commit()
            return True
        except sqlite3.OperationalError as error:
            print(__name__, f"\tError:: {str(error)}")
            return False
        except sqlite3.IntegrityError as error:
            print(__name__, f"\tError:: {str(error)}")
            return False

    def _check_db_path(self, db_path: str) -> bool:
        """ проверяет наличие файла БД по указаному пути """
        if db_path:
            self._db_path = db_path
        if not path.exists(self._db_path):
            print(__name__, f"\tError:: wrong database file {self._db_path}")
            return False
        return True


class SqlQueryBuilder(metaclass=Singleton):
    """ Класс для построения SQL запросов к БД """
    def build_select_qp(self, query_params: QueryParams) -> str:
        """ строит запрос выборки SELECT """
        result = ""
        qp = query_params
        if qp.table:
            cols = ",".join(map(str, qp.columns)) if qp.columns else "*"
            conds = self._create_conditions(qp.conditions)
            ordr = self._create_order(qp.order_by)
            result = f"Select {cols} From {qp.table} {conds} {ordr}"
            result = self._secure(result)
        return result

    def build_select(self, table: str, columns: list,
                     conditions: list=None, order_by: str=None) -> str:
        """ строит запрос выборки SELECT """
        qp = QueryParams(table, columns, conditions, order_by)
        return self.build_select_qp(qp)

    def build_insert(self, table: str, record: dict) -> str:
        """ строит запрос вставки INSERT"""
        result = ""
        if table and record:
            rec = record.copy()
            if 'ID' in rec:
                rec.pop('ID')
            cols = ",".join(map(self._key_to_str, rec.keys()))
            vals = ",".join(map(self._val_to_str, rec.values()))
            result = f"Insert Into {table} ({cols}) Values ({vals})"""
            result = self._secure(result)
        return result

    def build_update(self, table: str, record: dict,
                     conditions: dict=None) -> str:
        """ строит запрос обновления UPDATE """
        result = ""
        if table and record:
            rec = record.copy()
            rec_id = rec.pop('ID') if 'ID' in rec else 0
            vals = self._create_values(rec)
            conds = self._create_conditions(conditions)
            if conds == "":
                if rec_id:
                    conds = f"Where ID={rec_id}"
                else:
                    return result
            result = f"Update {table} Set {vals} {conds}"
            result = self._secure(result)
        return result

    def build_delete(self, table: str, conditions: dict) -> str:
        """ строит запрос удаления DELETE """
        result = ""
        if table and conditions:
            conds = self._create_conditions(conditions)
            result = f"Delete From {table} {conds}"
            result = self._secure(result)
        return result

    def _create_values(self, pairs: dict, separator=",") -> str:
        """ строит строку содержащую пары ключ-значение разделенные запятой """
        result = ""
        if isinstance(pairs, dict) and pairs:
            f_key = self._key_to_str
            f_val = self._val_to_str
            vals = [f"{f_key(k)}={f_val(v)}" for k, v in pairs.items()]
            result = separator.join(vals)
        return result

    def _create_conditions(self, conditions: dict) -> str:
        """ строит строки содержащую условия выборки WHERE """
        result = ""
        if conditions:
            vals = self._create_values(conditions, " And ")
            if vals:
                result = f"Where {vals}"
        return result

    @staticmethod
    def _create_order(order: str) -> str:
        """ строит строку содержащую условия сортировки ORDER BY """
        return f"Order by {order}" if order else ""

    @staticmethod
    def _check_not_empty(args: list) -> bool:
        """ проверяет, чтоб критические агрументы не были None """
        if isinstance(args, list):
            return next((False for arg in args if not arg), True)
            # for arg in args:
            #     if arg is None or len(arg) == 0:
            #         return False
            # return True
        return False

    @staticmethod
    def _secure(query: str) -> str:
        """ Fixing query by striping unwanted characters
            and remove possible injections
            TODO
        """
        query += " "
        return f"{query[:query.find(';')].strip(' .,=;')};"

    @staticmethod
    def _key_to_str(key) -> str:
        """ конвертирует ключ в совместимый формат для SQL запроса """
        return f"`{key}`" if not isinstance(key, str) else key

    @staticmethod
    def _val_to_str(val) -> str:
        """ конвертирует значение в совместимый формат для SQL запроса """
        return f"'{val}'" if isinstance(val, str) else str(val) if val else "NULL"
