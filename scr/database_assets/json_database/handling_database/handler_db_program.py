import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scr.database_assets.json_database._receiver_db import ReceiverDataBase


class DataBaseProgramData:
    def __init__(self):
        self.data_base = ReceiverDataBase()
        self.name_dict = 'program data'

    def get_all_db_program(self):
        self.data_base.load()
        return self.data_base.data.get(self.name_dict, '')

    def set_db_progrm(self, key, data):
        if key in self.data_base.data.get(self.name_dict, '').keys():
            self.data_base.data[self.name_dict][key] = data
            self.data_base.save()
            self.data_base.load()

    def get_program_data(self, repository_name):
        self.data_base.load()
        return self.data_base.data[self.name_dict].get(repository_name, '')

    def set_program_db(
            self
            , name_repo
            , url_git=''
            , comment=''
            , last_version=''
            , program_name=''
            , target=''
            , date_relise=''
    ):
        if name_repo in self.data_base.data[self.name_dict].keys():

            bd_url = self.data_base.data[self.name_dict][name_repo].get('url git', '')
            bd_version = self.data_base.data[self.name_dict][name_repo].get('last version', '')
            bd_comment = self.data_base.data[self.name_dict][name_repo].get('comment', '')
            bd_name = self.data_base.data[self.name_dict][name_repo].get('name', '')
            bd_target = self.data_base.data[self.name_dict][name_repo].get('target', '')
            bd_date_relise = self.data_base.data[self.name_dict][name_repo].get('date relise', '')

            if url_git == '' and bd_url != '': url_git = bd_url
            if last_version == '' and bd_version != '': last_version = bd_version
            if comment == '' and bd_comment != '': comment = bd_comment
            if program_name == '' and bd_name != '': program_name = bd_name
            if target == '' and bd_target != '': target = bd_target
            if date_relise == '' and bd_date_relise != '': date_relise = bd_date_relise

        data_program = {
            f'{name_repo}': {
                'name': program_name
                , 'url git': url_git
                , 'comment': comment
                , 'last version': last_version
                , 'name repo': name_repo
                , 'target': target
                , 'date relise': date_relise
            }
        }

        self.data_base.data[self.name_dict].update(data_program)
        self.data_base.save()
        self.data_base.load()


if __name__ == "__main__":
    app = DataBaseProgramData()
