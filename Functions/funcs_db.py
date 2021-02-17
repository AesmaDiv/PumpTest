"""
    Функции работы с базой данных
"""
from Globals import gvars

def execute_query(query: str):
    """ Выполенение запроса к БД """
    result = None
    if gvars.db.connect():
        result = gvars.db.execute(query)
        gvars.db.disconnect()
    return result


def get_value(table: str, column: str, condition: dict):
    """ Получение значения из записи """
    records = get_records(table, [column], condition)
    result = records[0] if not records is None else None
    return result


def get_record(table: str, columns: list=None, conditions: dict=None) -> dict:
    """ Получение записи (строки) из БД """
    result = get_records(table, columns, conditions)
    return result[0] if not result is None else None


def get_records(table: str, columns: list=None,
                conditions: dict=None, order_by='') -> list:
    """ Получение нескольких записей (строк), удовлетворяющих условие """
    result = gvars.db.select(table, columns, conditions, order_by)
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
