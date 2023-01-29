import os
from typing import Dict, List, Tuple

import sqlite3


dir = os.path.join("controller", "utils", "db", "finance.db")
print(dir)
conn = sqlite3.connect(dir)
cursor = conn.cursor()


def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def fetchall(table: str, columns: List[str]) -> List[Tuple]:
    columns_joined = ", ".join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            #print("index = ", index, " column= ", column)
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def delete(table: str, row_id: int, user_id: int) -> None:
    row_id = int(row_id)
    user_id = int(user_id)
    cursor.execute(f"delete from {table} where del_id={row_id} "
                   f"and user_id={user_id}")
    conn.commit()


def get_cursor():
    return cursor


def _init_db(name: str):
    """Инициализирует БД"""
    with open(f"controller/utils/{name}", "r", encoding="utf8") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute("DROP TABLE category")
    _init_db("category.sql")
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='expense'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db("createdb.sql")

check_db_exists()
