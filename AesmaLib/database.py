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
    """ Decorator for funcs to (connect)(call func)(disconnect) """
    def wrapped(self, *args, **kwargs):
        result = None
        if self.connect():
            result = func(self, *args, **kwargs)
            self.disconnect()
        return result
    return wrapped


class Database(metaclass=Singleton):
    """ Interface for DB classes """
    def connect(self, db_path: str='') -> bool:
        """ Connecting to database"""

    def disconnect(self):
        """ Disconnecting from database """

    def select(self, table: str, columns: list=None,
               conditions: dict=None, order_by:str='') -> dict:
        """ Getting records from database"""

    def insert(self, table: str, record: dict) -> int:
        """ Inserting record to database """

    def update(self, table: str, record: dict, conditions: dict=None) -> bool:
        """ Updating record in database """

    def delete(self, table: str, conditions: dict) -> bool:
        """ Deleting record from database """

    def execute(self, query: str) -> bool:
        """ Executing sql query"""


class SqliteDB(Database):
    """ Class for Sqlite3 database """
    def __init__(self, db_path:str=''):
        self._is_connected = False
        self._connection = None
        self._cursor = None
        self._db_path = db_path
        self._builder = SqlQueryBuilder()

    def set_path(self, db_path: str):
        """ Setting path to db file """
        self._db_path = db_path

    def connect(self, db_path="") -> bool:
        """ Connecting to database"""
        if not self._is_connected:
            if self._check_db_path(db_path):
                self._connection = sqlite3.connect(self._db_path)
                self._connection.row_factory = sqlite3.Row
                self._cursor = self._connection.cursor()
                self._is_connected = True
        return self._is_connected

    def disconnect(self):
        """ Disconnecting from database """
        if self._is_connected:
            self._cursor = None
            self._connection.close()
            self._is_connected = False

    @connect_execute_disconnect
    def select(self, table: str, columns: list=None,
               conditions: dict=None, order_by: str='') -> list:
        """ Getting records from database"""
        result = []
        query = self._builder.build_select(table, columns, conditions, order_by)
        if self.execute(query):
            records = self._cursor.fetchall()
            result = [dict(row) for row in records]
        return result

    @connect_execute_disconnect
    def insert(self, table: str, record: dict) -> int:
        """ Inserting record to database """
        query = self._builder.build_insert(table, record)
        return self._cursor.lastrowid if self.execute(query) else 0

    @connect_execute_disconnect
    def update(self, table: str, record: dict, conditions: dict=None) -> bool:
        """ Updating record in database """
        query = self._builder.build_update(table, record, conditions)
        return self.execute(query)

    @connect_execute_disconnect
    def delete(self, table: str, conditions: dict) -> bool:
        """ Deleting record from database """
        query = self._builder.build_delete(table, conditions)
        return self.execute(query)

    @connect_execute_disconnect
    def execute_with_retval(self, query: str):
        """ Executing sql query WITH return value """
        result = None
        if self.execute(query):
            records = self._cursor.fetchall()
            result = [dict(row) for row in records]
        return result


    def execute(self, query: str) -> bool:
        """ Executing sql query WITHOUT return value """
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
        """ Checking if database file exists """
        if not db_path == "":
            self._db_path = db_path
        if not path.exists(self._db_path):
            print(__name__, f"\tError:: wrong database file {self._db_path}")
            return False
        return True


class SqlQueryBuilder(metaclass=Singleton):
    """ Class for building Sql queries to databases """
    def build_select(self, table: str, columns: list,
                     conditions: list=None, order: str=None) -> str:
        """ Building SQL query to SELECT records """
        result = ""
        if self._check_not_empty([table]):
            cols = ",".join(map(str, columns)) if columns else "*"
            conds = self._create_conditions(conditions)
            ordr = self._create_order(order)
            result = f"Select {cols} From {table} {conds} {ordr}"
            result = self._secure(result)
        return result

    def build_insert(self, table: str, record: dict) -> str:
        """ Building SQL query to INSERT record """
        result = ""
        if self._check_not_empty([table, record]):
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
        """ Building SQL query to UPDATE record """
        result = ""
        if self._check_not_empty([table, record]):
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
        """ Building SQL query to DELETE record """
        result = ""
        if self._check_not_empty([table, conditions]):
            conds = self._create_conditions(conditions)
            result = f"Delete From {table} {conds}"
            result = self._secure(result)
        return result

    def _create_values(self, pairs: dict, separator=",") -> str:
        """ Creating string containing pairs KEY=VALUE separated by comma """
        result = ""
        if self._check_not_empty([pairs]):
            f_key = self._key_to_str
            f_val = self._val_to_str
            vals = [f"{f_key(k)}={f_val(v)}" for k, v in pairs.items()]
            result = separator.join(vals)
        return result

    def _create_conditions(self, conditions: dict) -> str:
        """ Creating string containing WHERE conditions for Sql query """
        result = ""
        if self._check_not_empty([conditions]):
            vals = self._create_values(conditions, " And ")
            if vals:
                result = f"Where {vals}"
        return result

    @staticmethod
    def _create_order(order: str) -> str:
        """ Creating string containing ORDER BY for Sql query """
        return f"Order by {order}" if order else ""

    @staticmethod
    def _check_not_empty(args: list) -> bool:
        """ Checking vital arguments not to be None or Empty """
        if isinstance(args, list):
            for arg in args:
                if arg is None or len(arg) == 0:
                    return False
            return True
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
        """ Converting KEY to proper string format for Sql query """
        return f"`{key}`" if not isinstance(key, str) else key

    @staticmethod
    def _val_to_str(val) -> str:
        """ Converting VALUE to proper string format for Sql query """
        return f"'{val}'" if isinstance(val, str) else str(val) if val else "NULL"
