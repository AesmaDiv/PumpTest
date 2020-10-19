import sqlite3
from os import path
from AesmaLib import Journal


class SqliteDB:

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, db_path: str):
        if path.exists(db_path):
            try:
                self.connection = sqlite3.connect(db_path)
                self.connection.row_factory = sqlite3.Row
                self.cursor = self.connection.cursor()
                return True
            except BaseException as error:
                Journal.log(__name__ + " error: " + str(error))
        return False

    def disconnect(self):
        self.cursor = None
        self.connection.close()

    def read(self, table: str, columns: list = [], conditions: dict = {}, order_by: str = ''):
        cmd = self.__build_cmd_read(table, columns, conditions, order_by)
        return self.read_query(cmd)

    def read_query(self, query: str):
        result: list = []
        try:
            if self.execute(query):
                records = self.cursor.fetchall()
                result = [dict(row) for row in records]
        except BaseException as error:
            Journal.log(__name__ + " error: " + str(error))
        return result

    def write(self, table: str, record: dict):
        return self.execute(self.__build_cmd_write(table, record))

    def update(self, table: str, record: dict):
        return self.execute(self.__build_cmd_update(table, record))

    def delete(self, table: str, condition: dict):
        return self.execute(self.__build_cmd_delete(table, condition))

    def execute(self, cmd: str):
        try:
            self.cursor.execute(cmd)
            self.connection.commit()
            return True
        except BaseException as error:
            Journal.log(__name__ + " error: " + str(error))
            return False

    @staticmethod
    def __build_cmd_read(table: str, columns: list, conditions: dict, order_by: str):
        result: str = "Select "
        result += ", ".join(map(str, columns)) if columns else "*"
        result += " From " + table
        if conditions:
            result += " Where "
            for key, value in conditions.items():
                quotes = "'" if isinstance(value, str) else ""
                result += str(key) + "=" + quotes + str(value) + quotes
                result += " And "
            result = result[:-5]
        if order_by:
            result += " Order by " + order_by
        return result

    @staticmethod
    def __build_cmd_write(table: str, record: dict):
        temp = record
        if 'ID' in temp:
            del temp['ID']
        columns: str = ""
        values: str = ""
        for key, value in record.items():
            if value:
                columns += key + ","
                quotes = "'" if isinstance(value, str) else ""
                values += quotes + str(value) + quotes + ","
        columns = columns[:-1]
        values = values[:-1]

        result: str = "Insert Into %s (%s) Values (%s)" % (table, columns, values)
        return result

    @staticmethod
    def __build_cmd_update(table: str, record: dict):
        values: str = ""
        quotes: str = ""
        for key, value in record.items():
            if key == 'ID':
                continue
            elif isinstance(value, str):
                quotes = "" if not value else "'"
            else:
                quotes = ""
            value = 'NULL' if not value else str(value)
            values += str(key) + '=' + quotes + value + quotes + ","
        values = values[:-1]
        result: str = "Update %s Set %s Where ID=%s" % (table, values, record['ID'])
        return result

    @staticmethod
    def __build_cmd_delete(table: str, condition: dict):
        where: str = ""
        quotes: str = ""
        for key, value in condition.items():
            if isinstance(value, str):
                quotes = "'"
            else:
                quotes = ""
            where += str(key) + '=' + quotes + str(value) + quotes + ' And '
        where = where[:-5]
        result: str = "Delete From %s Where %s" % (table, where)
        return result
