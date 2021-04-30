#!/usr/bin/python3
import os, sqlite3


def reverse_value(value):
    arr_values = value.split(',')
    arr_values = arr_values[::-1]
    return ','.join(arr_values)


def update_record(cursor, rec_id, value):
    query = f"Update Types set Flows='{value}' where ID={rec_id}"
    cursor.execute(query)


if __name__ == "__main__":
    print("*** Reversing Flows column in Types table ***")
    folder = os.path.dirname(os.path.realpath(__file__))
    path = f'{folder}/pump.sqlite'
    with sqlite3.connect(path) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        try:
            if cur.execute('Select ID, Flows from Types'):
                recs = cur.fetchall()
                if recs:
                    for rec in recs:
                        rec_id, value = rec['ID'], rec['Flows']
                        value = reverse_value(value)
                        update_record(cur, rec_id, value)
                con.commit()
                print(f"{len(recs)} rows processed")
        except sqlite3.OperationalError as err:
            print(f'Error::{str(err)}')
    print("*** End ***")
