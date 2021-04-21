"""
    Модуль содержит функции работы с базой данных
"""
from AesmaLib.database import QueryParams
from Globals import gvars


def execute_query(query: str):
    """ Выполенение запроса к БД """
    result = gvars.db.execute_with_retval(query)
    return result


def get_value(table: str, column: str, conditions: dict):
    """ Получение значения из записи """
    records = get_records(QueryParams(table, [column], conditions))
    result = records[0] if not records is None else None
    return result


def get_record(query_params: QueryParams) -> dict:
    """ Получение записи (строки) из БД """
    result = get_records(query_params)
    return result[0] if not result is None else None


def get_records(query_params: QueryParams) -> list:
    """ Получение нескольких записей (строк), удовлетворяющих условие """
    result = gvars.db.select_qp(query_params)
    return result if result else None


def insert_record(table: str, record: dict) -> int:
    """ Добавление новой записи в БД """
    result = gvars.db.insert(table, record)
    return result > 0


def update_record(table: str, record: dict):
    """ Изменение (обновление) записи в БД """
    result = gvars.db.update(table, record)
    return result


def set_permission(table: str, permission: bool):
    """ Установка разрешения на внесение изменений в БД """
    result = False
    if gvars.db.connect():
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
        result = gvars.db.execute(cmd)
        gvars.db.disconnect()
    return result
