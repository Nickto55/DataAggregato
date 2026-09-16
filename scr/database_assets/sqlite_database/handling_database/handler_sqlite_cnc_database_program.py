import os

from scr.database_assets.sqlite_database._receiver_sqlite_database import SQLiteManager


class ReceiverDataBaseCNC:
    def __init__(self, name_file_db=None):
        self.name_work_file = name_file_db if name_file_db else 'summary_table_of_milling_machines.db'

        self.CONFIG_DIR = r'\\volna.dmn\data\obmen\Служба Главного инженера\ОГТ\ЧПУ\Программы Python\database_program'
        self.file_path = os.path.join(self.CONFIG_DIR, self.name_work_file)

        self.table_name = 'cnc_data_machine'
        self.schema = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name_machine_directory": "TEXT NOT NULL",
            "dse_directory": "TEXT NOT NULL",
            "dse_name": "TEXT NOT NULL",
            "content": "TEXT DEFAULT ''",
            "link": "TEXT DEFAULT ''",
            "fm_file": "TEXT DEFAULT ''",
            "files_without_extension": "TEXT DEFAULT ''",
            "last_modified_date": "TEXT DEFAULT ''",
            "kb": "TEXT DEFAULT ''"
        }
        self.unique_keys = ["name_machine_directory", "dse_directory", "dse_name"]
        self.indexes = ["name_machine_directory", "dse_name"]

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
            machine = row['name_machine_directory']
            dse_dir = row['dse_directory']
            dse_name = row['dse_name']

            result.setdefault(machine, {}).setdefault(dse_dir, {})[dse_name] = {
                'dse_name': dse_name,
                'content': row['content'],
                'link': row['link'],
                'fm_file': row['fm_file'],
                'files_without_extension': row['files_without_extension'],
                'last_modified_date': row['last_modified_date'],
                'kb': row['kb']
            }
        return result

    def get_program_data(self, repository_name):
        """Быстрый поиск по имени DSE."""
        return self.db.get_by_field('dse_name', repository_name)

    def set_program_db(self, name_machine_directory, dse_directory, dse_name,
                       content='', link='', fm_file='', files_without_extension='',
                       last_modified_date='', kb=''):
        """
        Запись/обновление.
        Если поле пустое, но в БД уже есть старое значение - можно подтянуть его (опционально).
        """
        # Логика подтягивания старых значений, если новые пустые
        existing = self.db.get_by_field('dse_name', dse_name)
        if existing and len(existing) > 0:
            old = existing[0]
            if not content: content = old.get('content', '')
            if not link: link = old.get('link', '')
            if not fm_file: fm_file = old.get('fm_file', '')
            if not files_without_extension: files_without_extension = old.get('files_without_extension', '')
            if not last_modified_date: last_modified_date = old.get('last_modified_date', '')
            if not kb: kb = old.get('kb', '')

        data_to_save = {
            "name_machine_directory": name_machine_directory,
            "dse_directory": dse_directory,
            "dse_name": dse_name,
            "content": content,
            "link": link,
            "fm_file": fm_file,
            "files_without_extension": files_without_extension,
            "last_modified_date": last_modified_date,
            "kb": kb
        }

        self.db.upsert(data_to_save)

    def close(self):
        self.db.close()

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

if __name__ == "__main__":
    app = ReceiverDataBaseCNC('')

    # app.set_program_db(
    #     name_machine_directory='HAAS',
    #     dse_directory='БАШК',
    #     dse_name='БАШК.711112.003',
    #     content='',
    #     link=r'//Dc-hv-disp/UP/HAAS\БАШК\БАШК.711112.003',
    #     fm_file='X',
    #     files_without_extension='',
    #     last_modified_date='2016-04-07 14:29:57',
    #     kb='POPOVCHENKO S.S. )'
    # )
    for row_dse in app.get_program_data('БАШК.711112.003'):
        print(f'`{row_dse}`')