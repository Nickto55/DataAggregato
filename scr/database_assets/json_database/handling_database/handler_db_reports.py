import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scr.database_assets.json_database._receiver_db import ReceiverDataBase


class DataBaseProgramData:
    def __init__(self, name_dict=None, name_database=None, name_repozitory='reports', config_programm=None):
        name_database = name_database if not pd.isna(name_database) else 'database_reports.json'
        self.name_dict = name_dict if not pd.isna(name_dict) else 'pivot fusion'

        self.data_base = ReceiverDataBase(
            name_file_database=name_database
            , additional_directories=name_repozitory
            , data_structur={self.name_dict: {}}
            , config_programm=config_programm
        )

    def get_all_database_dict(self) -> dict[str, dict]:
        self.data_base.load()
        return self.data_base.data.get(self.name_dict, '')

    def set_value_in_key(self, key, data: dict):
        """
        Функция для установки контного значения по ключу
        :param key: ключ
        :param data: значение
        """
        if key in self.data_base.data.get(self.name_dict, '').keys():
            self.data_base.data[self.name_dict][key] = data
            self.data_base.save()
            self.data_base.load()

    def set_database(self, data: dict):
        self.data_base.data[self.name_dict] = data
        self.data_base.save()
        self.data_base.load()

    def get_program_data(self, repository_name) -> dict:
        """
        :param repository_name:Получение конкретного значения из базы данных
        :return: dict
        """
        self.data_base.load()
        return self.data_base.data[self.name_dict].get(repository_name, '')

    def set_program_db(self, name_repo: str, **kwargs: str) -> None:
        repo_dict = self.data_base.data.setdefault(self.name_dict, {})

        current_data = repo_dict.get(name_repo, {})

        filtered_kwargs = {k: v for k, v in kwargs.items() if v != ''}

        updated_data = {
            'name repo': name_repo
            , **current_data
            , **filtered_kwargs
        }

        repo_dict[name_repo] = updated_data
        self.data_base.save()
        self.data_base.load()


if __name__ == "__main__":
    app = DataBaseProgramData()
