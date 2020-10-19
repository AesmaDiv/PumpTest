from AesmaLib import Journal
import vars


def execute_query(query: str):
    result = None
    try:
        if vars.db.connect(vars.path_to_db):
            result = vars.db.read_query(query)
            vars.db.disconnect()
    except IOError as error:
        Journal.log(__name__ + " Error: " + str(error))
    return result


def get_value(table: str, column: str, condition: dict):
    records = get_records(table, [column], condition)
    result = records[0] if records and len(records) > 0 else None
    return result


def get_record(table: str, columns: list = None, conditions: dict = None):
    if columns is None: columns = []
    if conditions is None: conditions = {}
    result = get_records(table, columns, conditions)
    return result[0] if result and len(result) > 0 else None


def get_records(table: str, columns: list = None, conditions: dict = None, order_by=''):
    result = None
    if columns is None: columns = []
    if conditions is None: conditions = {}
    try:
        if vars.db.connect(vars.path_to_db):
            result = vars.db.read(table, columns, conditions, order_by)
            vars.db.disconnect()
    except IOError as error:
        Journal.log(__name__ + " Error: " + str(error))
    return result


def insert_record(table: str, record: dict):
    result = False
    try:
        if vars.db.connect(vars.path_to_db):
            result = vars.db.write(table, record)
            vars.db.disconnect()
    except BaseException as error:
        Journal.log(__name__ + " Error: " + str(error))
    return result


def update_record(table: str, record: dict):
    result = False
    try:
        if vars.db.connect(vars.path_to_db):
            result = vars.db.update(table, record)
            vars.db.disconnect()
    except BaseException as error:
        Journal.log(__name__ + " Error: " + str(error))
    return result


def set_permission(table: str, permission: bool):
    result = False
    try:
        if vars.db.connect(vars.path_to_db):
            if permission:
                cmd = 'DROP TRIGGER block_update'
            else:
                cmd = "CREATE TRIGGER block_update\n" \
                    + "BEFORE UPDATE OF Flows, Lifts, Powers\n" \
                    + "ON Tests\n" \
                    + "WHEN old.Flows=NULL\n" \
                    + "BEGIN\n" \
                    + "SELECT RAISE(ABORT, 'updates not allowed');\n" \
                    + "End;\n"
            result = vars.db.execute(cmd)
            vars.db.disconnect()
    except BaseException as error:
        Journal.log(__name__ + " Error: " + str(error))
    return result
