import os
import time

import pandas as pd

from datetime import datetime

from scr.excel_assets.readers.excel_reader import MultiSheetReader
from scr.config_assets.handling_config.handler_direcrory_report import ConfigDirectoryReport
from scr.config_assets.handling_config.handler_aggregato_config import ConfigAggregato

from scr.database_assets.json_database.handling_database.handler_db_reports import DataBaseProgramData


class ReportHandler:
    def __init__(self, log_callback=None):
        self.log = log_callback if log_callback else print

        self.config_aggregato = ConfigAggregato()
        self.config_directory_report = ConfigDirectoryReport()

        self.name_report_file = self.config_aggregato.get_all_config_program().get('name bam report tabel', '')
        self.list_name_work_central = self.config_aggregato.get_all_config_program().get('name work central', '')

        try:
            self.list_name_work_central = self.list_name_work_central.split('|::|')
        except:
            self.list_name_work_central = ['ФОЦ', 'ТОЦ', 'ПОЦ']
        try:
            self.name_report_file = self.name_report_file.split('|::|')
        except:
            self.name_report_file = ['Отчёт по УП БАМ.xlsm']

    def _data_get_report_tabel(self, path_to_directory):
        result_data = {}
        list_fiels_in_directory = os.listdir(path_to_directory)

        path_to_report_file = None
        if 'Отчёт по УП БАМ.xlsm' in list_fiels_in_directory:
            path_to_report_file = os.path.join(path_to_directory, self.name_report_file[0])
        else:
            for namefile in list_fiels_in_directory:
                if self.name_report_file[1] in namefile:
                    path_to_report_file = os.path.join(path_to_directory, namefile)
                    break
        if path_to_report_file is None:
            # noinspection PyInconsistentReturns
            return
        name_directory_report_database = self.config_aggregato.get_all_config_program().get(
            'name directory database save reports'
            , None
        )
        name_file_in_database = f'{os.path.basename(path_to_directory)}.json'

        try:
            name_directory_report = os.path.basename(path_to_directory)

            path_to_directory_database_save_reports = self.config_aggregato.get_all_config_program().get(
                'path to directory database save reports', None)

            for name_file_database in os.listdir(path_to_directory_database_save_reports):
                if name_directory_report in name_file_database:
                    name_file_in_database = name_file_database
                    break

            # noinspection PyUnboundLocalVariable
            self.log(f'handler_directory_report: Файл принят в обработку:', level='debug')
            self.log(f'  {path_to_report_file}', level='debug')
            time_modify_report = os.path.getmtime(path_to_report_file)
            data_config_reports = self.config_directory_report.get_all_config_program()

            if os.path.basename(path_to_directory) in data_config_reports.keys():
                data_config_report = data_config_reports.get(os.path.basename(path_to_directory), '')
                if time_modify_report == data_config_report.get('last time modification report', ''):
                    database_repors = DataBaseProgramData(
                        name_database=name_file_in_database
                        , name_dict='datas'
                        , name_repozitory=name_directory_report_database
                        , config_programm=self.config_aggregato
                    )
                    data_report = database_repors.get_all_database_dict()
                    return data_report
        except Exception as error_get_data:
            self.log(error_get_data)
            raise error_get_data

        reader = MultiSheetReader(file_path=path_to_report_file)
        data_report = reader.load_sheets()

        for work_central, data_work_central in data_report.items():
            if work_central in self.list_name_work_central:
                transformed_value_of_work_center = {}
                for column_name, column_data in data_work_central.items():
                    count_row_value = 0
                    for column_value in column_data:

                        if column_name == column_value: continue
                        if column_name == "Дата" and isinstance(column_value, datetime):
                            column_value = str(column_value)
                        if pd.isna(column_value): column_value = None

                        if not count_row_value in transformed_value_of_work_center.keys():
                            transformed_value_of_work_center[count_row_value] = {column_name: column_value}
                            count_row_value += 1
                            continue
                        data_row = transformed_value_of_work_center.get(count_row_value, None)
                        # noinspection PyUnresolvedReferences
                        data_row[column_name] = column_value
                        transformed_value_of_work_center[count_row_value] = data_row
                        count_row_value += 1

                result_data[work_central] = transformed_value_of_work_center
        path_directory_report_database = self.config_aggregato.get_all_config_program().get(
            'path to directory database save reports'
            , None
        )
        database_repors = DataBaseProgramData(
            name_database=name_file_in_database
            , name_dict='datas'
            , name_repozitory=name_directory_report_database
            , config_programm=self.config_aggregato
        )
        self.config_directory_report.add_config_progrm(
            key=os.path.basename(path_to_directory)
            , data={
                'last time modification report': os.path.getmtime(path_to_report_file)
                , 'time save report in database': time.time()
                , 'link to database save': os.path.join(path_directory_report_database, name_file_in_database)
            }
        )
        database_repors.set_database(data=result_data)
        return result_data

    def get_data_from_report_directory(self, path_to_directory):
        if os.path.isdir(path_to_directory):
            if self.name_report_file[0] in os.listdir(path_to_directory):
                return self._data_get_report_tabel(path_to_directory)
            for name_tabel_file in os.listdir(path_to_directory):
                if 'программы для станков с ЧПУ ' in name_tabel_file:
                    return self._data_get_report_tabel(path_to_directory)


        # noinspection PyArgumentList
        self.log(f'Не удалось обработать: {os.path.basename(path_to_directory):}', color_log='#575a5e', level='info')
        return None
