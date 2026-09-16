import os
from scr.database_assets.sqlite_database._receiver_sqlite_database import SQLiteManager


class ReceiverDataBase:
    def __init__(self, name_file_db=None):
        self.name_work_file = name_file_db if name_file_db else 'summary_table_of_milling_machines.db'

        self.CONFIG_DIR = r'\\volna.dmn\data\obmen\Служба Главного инженера\ОГТ\ЧПУ\Программы Python\database_program'
        self.file_path = os.path.join(self.CONFIG_DIR, self.name_work_file)

        self.table_name = "program_data"
        self.schema = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "program": "TEXT NOT NULL",
            "len_database": "TEXT NOT NULL",
            "content": "TEXT DEFAULT ''",
        }
        self.unique_keys = ["program"]
        self.indexes = ["program", "id"]

        self.db = SQLiteManager(
            db_path=self.file_path,
            table_name=self.table_name,
            schema=self.schema,
            unique_keys=self.unique_keys,
            indexes=self.indexes
        )


    def get_all_db_program(self):
        """Возвращает данные в виде вложенного словаря (как в старом JSON)."""
        rows = self.db.get_all()
        result = {}
        for row in rows:
            machine = row['program']
            dse_dir = row['len_database']

            result.setdefault(machine, {}).setdefault(dse_dir, {})[program] = {
                'content': row['content'],

            }
        return result

    def get_program_data(self, program):
        """Быстрый поиск по имени DSE."""
        return self.db.get_by_field('program', program)

    def set_program_db(self, program, len_database,
                       content=''):
        """
        Запись/обновление.
        Если поле пустое, но в БД уже есть старое значение - можно подтянуть его (опционально).
        """
        existing = self.db.get_by_field('program', program)
        if existing and len(existing) > 0:
            old = existing[0]
            if not content: content = old.get('content', '')

        data_to_save = {
            "program": program,
            "len_database": len_database,
            "content": content
        }

        self.db.upsert(data_to_save)

    def close(self):
        self.db.close()

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

if __name__ == "__main__":
    app = ReceiverDataBase()

    app.set_program_db(
        program='Aggregato',
        len_database='321332',
        content='error',

    )
    print(app.get_program_data('Aggregato'))