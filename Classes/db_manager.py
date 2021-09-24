"""
    Модуль содержит класс для работы с базой данных
"""
from AesmaLib.database import QueryParams
from AesmaLib.database import SqliteDB


class DBManager(SqliteDB):
    """ Класс менеджера базы данных """
    def execute_query(self, query: str):
        """ Выполенение запроса к БД """
        result = self.execute_with_retval(query)
        return result

    def get_value(self, table: str, column: str, conditions: dict):
        """ Получение значения из записи """
        records = self.get_records(QueryParams(table, [column], conditions))
        result = records[0] if not records is None else None
        return result

    def get_record(self, query_params: QueryParams) -> dict:
        """ Получение записи (строки) из БД """
        result = self.get_records(query_params)
        return result[0] if not result is None else None

    def get_records(self, query_params: QueryParams) -> list:
        """ Получение нескольких записей (строк), удовлетворяющих условие """
        result = self.select_qp(query_params)
        return result if result else None

    def insert_record(self, table: str, record: dict) -> int:
        """ Добавление новой записи в БД """
        result = self.insert(table, record)
        return result > 0

    def update_record(self, table: str, record: dict):
        """ Изменение (обновление) записи в БД """
        result = self.update(table, record)
        return result

    def set_permission(self, table: str, permission: bool):
        """ Установка разрешения на внесение изменений в БД """
        result = False
        if self.connect():
            if permission:
                cmd = "DROP TRIGGER block_update"
            else:
                cmd = f"""CREATE TRIGGER block_update
                        BEFORE UPDATE OF Flows, Lifts, Powers
                        ON {table}
                        WHEN old.Flows=NULL
                        BEGIN
                            SELECT RAISE(ABORT, 'updates not allowed');
                        END;"""
            result = self.execute(cmd)
            self.disconnect()
        return result
