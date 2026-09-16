import os

import pandas as pd

from scr.excel_assets.enters.excel_enter import ExcelInserter

from scr.handling.constructing_resulting_table.handling_generator.handler_initial_data_collector import \
    InitialDataCollector
from scr.database_assets.sqlite_database.handling_database.handler_sqlite_cnc_database_program import ReceiverDataBaseCNC


class ConstructorResultLogic:
    def __init__(self, path_to_pivot_fusion_tabel: str, log_callback=None):
        self.log = log_callback if log_callback else print

        self.path_to_pivot_fusion_tabel = os.path.normpath(path_to_pivot_fusion_tabel)
        self.data_pivot_fusion_tabel = {}
        self.result_data = {}
        self.database_sqlite_cnc = ReceiverDataBaseCNC()

        self.work_central = {
            'ФОЦ': [
                'HAAS'
                , 'TGM0609'
                , 'VCenter'
                , 'Dahlih'
                , 'MCV'
                , 'beaver'
            ]
            , 'ПОЦ': [
                'GeFong GF-20MDII'
                , 'GeFong GNP-1724-D'
            ]
            , 'ТОЦ': [
                'ACCUWAY UT-200SY'
                , 'PUMA 3050LM'
                , 'VTurn - A20YCM'
                , 'SL20'
                , 'ACCUWAY UT-200'
                , 'CKA6180A'
                , 'PUMA 4050LM'
                , 'SL10'
            ]
        }

    def search_fio(self):
        for num_row, data_row in self.result_data.items():
            dse = data_row.get('ДСЕ', None)
            if dse is None: continue
            list_cnc_sqlite_database = self.database_sqlite_cnc.get_program_data(dse)

            raw_fio_list = []

            for database_row_data in list_cnc_sqlite_database:
                if database_row_data.get('name_machine_directory', '') in self.work_central.get(data_row.get('РЦ', ''),
                                                                                                ''):
                    fio = str(database_row_data.get('content', '')).lower().strip()
                    if fio and fio != 'не найден':
                        raw_fio_list.append(fio)

            string_fio = str(list(dict.fromkeys(raw_fio_list)))[1:-1].replace("'", "")

            fio_input = self.result_data[num_row].get('ФИО', '')
            if fio_input != '' and not pd.isna(fio_input):
                if string_fio != '':
                    string_fio = str(fio_input).lower() + ', ' + string_fio
                else:
                    string_fio = str(fio_input).lower() + string_fio
            self.result_data[num_row]['ФИО'] = string_fio

    def removal_of_duplicate_records(self):
        result_data = {}
        for num_row, data_row in self.result_data.items():
            work_central = data_row.get('РЦ', '')
            dse = data_row.get('ДСЕ', '')
            new_key_row = f'{work_central}|::|{dse}'
            if not new_key_row in result_data.keys():
                result_data[new_key_row] = data_row
            else:
                new_fio = data_row.get('ФИО', '')
                res_fio = result_data[new_key_row].get('ФИО', '')
                if new_fio != '' and res_fio != '': res_fio = res_fio + ', ' + new_fio
                elif new_fio != '' and res_fio == '': res_fio = new_fio
                elif new_fio == '' and res_fio != '': res_fio = res_fio

                res_report = data_row.get('Отчет', '') + ', ' + result_data[new_key_row].get('Отчет', '')

                res_fio = str(list(dict.fromkeys(res_fio.split(', '))))[1:-1].replace("'", "")
                res_report = str(list(dict.fromkeys(res_report.split(', '))))[1:-1].replace("'", "")


                data_result = {
                    'РЦ': work_central
                    , 'ДСЕ': dse
                    , 'ФИО': res_fio
                    , 'Отчет':res_report
                }

                result_data[new_key_row] = data_result
        self.result_data = result_data.copy()

    def main(self):
        self.result_data, self.data_pivot_fusion_tabel = InitialDataCollector(self.path_to_pivot_fusion_tabel, log_callback=self.log).main()
        self.search_fio()
        self.removal_of_duplicate_records()

        writer = ExcelInserter(file_path=self.path_to_pivot_fusion_tabel)
        writer.insert_data(data={'0': self.result_data}, sheet_name='cnc database')


if __name__ == '__main__':
    app = ConstructorResultLogic(r"C:\Users\yakovlev_nd\Desktop\Tests\DataAggregato\Aggregato result.xlsx")
    app.main()
