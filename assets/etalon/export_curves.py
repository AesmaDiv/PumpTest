"""
    Модуль экспорта DTA файлов в таблицу типов
"""
from os import listdir
from os.path import isfile, join
from codecs import open as cdc_open
import sqlite3
import pathlib
from typing import NamedTuple


PumpType = NamedTuple(
    "PumpType",
    [
     ("manufacturer", str),
     ("name", str),
     ("date", str),
     ("rpm", int),
     ("minimum", float),
     ("nominal", float),
     ("maximum", float),
     ("flow", list),
     ("lift", list),
     ("power", list),
    ]
)


def get_files(dir_path):
    """получение списка DTA файлов в папке"""
    return [
      join(dir_path, f) for f in listdir(dir_path)
        if isfile(join(dir_path, f)) and f.endswith(".DTA") and f != ".DTA"
    ]

def read_file(file_path):
    """получение строк из DTA файла"""
    file = cdc_open(file_path, "r", "cp1251")
    lines = list(map(lambda l: l[:l.index("_")].strip(), file.readlines()))
    return lines

def get_data(lines: list):
    """парсинг строк из DTA в класс типоразмера"""
    try:
        flows_ = list(
            map(lambda x: round(x, 2), [x * float(lines[16]) / 6 for x in range(6, -1, -1)]))
        lifts_ = list(
            map(lambda x: round(x, 2), [float(lines[x]) for x in range(18, 25)]))
        powers_ = list(
            map(lambda x: round(x, 5), [float(lines[x]) * 0.7457 for x in range(29, 36)]))
        result = PumpType(
            manufacturer = lines[1],
            name = lines[2],
            date = lines[3],
            rpm = int(lines[4]),
            minimum = float(lines[13]),
            nominal = float(lines[14]),
            maximum = float(lines[15]),
            flow = flows_,
            lift = lifts_,
            power = powers_,
          )
        return result
    except (AttributeError, ValueError) as err:
        print("Catch error", lines[2], err)
        return None

def write_to_db(pts: list, db_path: str):
    """запись типоразмера в БД"""
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        for pt in pts:
            sql = f"""
            Insert Into TypesNew
                (Name, ProducerName, Date, Rpm, Min, Nom, Max, Flows, Lifts, Powers)
            Values 
                ('{pt.name}','{pt.manufacturer}','{pt.date}',
                  {pt.rpm},{pt.minimum},{pt.nominal},{pt.maximum},
                 '{",".join(map(str, pt.flow))}',
                 '{",".join(map(str, pt.lift))}',
                 '{",".join(map(str, pt.power))}')
            """
            conn.cursor().execute(sql)
            conn.commit()
    except sqlite3.Error as err:
        print("Error: ", err)


if __name__ == '__main__':
    current = pathlib.Path(__file__).parent.resolve()
    types = list(
        filter(
            lambda x: x is not None,
            [get_data(read_file(fl)) for fl in get_files(join(current, "curves"))]
        )
    )
    write_to_db(types, join(current, "../pump.sqlite"))
