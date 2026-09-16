import os
import sqlite3
import pandas as pd

from typing import Dict, List, Any, Optional


class SQLiteManager:
    """
    Универсальный менеджер SQLite.
    Работает на основе конфигурации (схемы), переданной при инициализации.
    """

    def __init__(
            self
            , db_path: str
            , table_name: str
            , schema: Dict[str, str]
            , unique_keys: List[str]
            , indexes: Optional[List[str]] = None
    ):
        """
        :param db_path: Путь к файлу БД (директория создастся автоматически).
        :param table_name: Имя таблицы.
        :param schema: Словарь {имя_колонки: SQL_тип_и_ограничения}.
        :param unique_keys: Список колонок для UNIQUE (используется в UPSERT).
        :param indexes: Список колонок для создания индексов.
        """
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.table_name = table_name if not pd.isna(table_name) or table_name == '' else 'NO_NAME_TABEL'
        self.schema = schema
        self.unique_keys = unique_keys

        # Подключение
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

        self._create_table()
        self._create_indexes(indexes or [])

    def _create_table(self):
        """Генерирует и выполняет CREATE TABLE на основе схемы."""
        cols_def = [f"{k} {v}" for k, v in self.schema.items()]
        if self.unique_keys:
            cols_def.append(f"UNIQUE({', '.join(self.unique_keys)})")

        query = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({', '.join(cols_def)})"
        self.cur.execute(query)
        self.conn.commit()

    def _create_indexes(self, indexes: List[str]):
        for col in indexes:
            idx_name = f"idx_{self.table_name}_{col}"
            self.cur.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {self.table_name}({col})")
        self.conn.commit()

    def upsert(self, data: Dict[str, Any]):
        """
        Универсальный UPSERT (INSERT or UPDATE).
        :param data: Словарь {колонка: значение}.
        """
        # Исключаем AUTOINCREMENT поля из вставки, если их нет в данных
        insert_cols = [k for k in self.schema.keys()
                       if 'AUTOINCREMENT' not in self.schema[k].upper() or k in data]

        # Фильтруем данные, оставляя только те, что есть в схеме
        filtered_data = {k: data[k] for k in insert_cols if k in data}

        col_names = ', '.join(filtered_data.keys())
        placeholders = ', '.join(['?'] * len(filtered_data))

        # Колонки для обновления (все, кроме тех, что в unique_keys)
        update_cols = [k for k in filtered_data.keys() if k not in self.unique_keys]
        update_set = ', '.join([f"{k}=excluded.{k}" for k in update_cols])

        query = f"""
            INSERT INTO {self.table_name} ({col_names}) VALUES ({placeholders})
            ON CONFLICT({', '.join(self.unique_keys)}) DO UPDATE SET {update_set}
        """
        self.cur.execute(query, tuple(filtered_data.values()))
        self.conn.commit()

    def get_all(self) -> List[Dict[str, Any]]:
        """Получить все записи в виде списка словарей."""
        self.cur.execute(f"SELECT * FROM {self.table_name}")
        return [dict(row) for row in self.cur.fetchall()]

    def get_by_field(self, field: str, value: Any) -> List[Dict[str, Any]]:
        """Поиск по одному полю."""
        self.cur.execute(f"SELECT * FROM {self.table_name} WHERE {field} = ?", (value,))
        return [dict(row) for row in self.cur.fetchall()]

    def execute_query(self, query: str, params: tuple = ()):
        """Для выполнения любых кастомных SQL-запросов."""
        self.cur.execute(query, params)
        self.conn.commit()
        return self.cur.fetchall()

    def close(self):
        self.conn.close()