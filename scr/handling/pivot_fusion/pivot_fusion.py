import os
import time

import pandas as pd

from scr.excel_assets.enters.excel_enter import ExcelInserter

from scr.handling.pivot_fusion.handling_pivot.handler_directory_report import ReportHandler

from scr.config_assets.handling_config.handler_program_config import ConfigMainProgram
from scr.config_assets.handling_config.handler_aggregato_config import ConfigAggregato


# noinspection PyArgumentList
class PivotFusionLogic:
    def __init__(self, log_callback=None):
        self.config_program = ConfigMainProgram()
        self.config_aggregato = ConfigAggregato()

        self.log = log_callback if log_callback else print

        self.list_name_dse = self.config_aggregato.get_all_config_program().get('name dse', '')

        try:
            if pd.isna(self.list_name_dse) or self.list_name_dse == '':
                raise
            self.list_name_dse = self.list_name_dse.split('|::|')
        except Exception as warn_:
            self.log(f'pivot_fusion: Не удалось загрузить наименование листов рц', level='warn')
            self.log(warn_, level='warn')
            self.list_name_dse = ['Фрезерные ЧПУ', 'Прутковые автоматы', 'Токарные ЧПУ', 'Автоматы ЧПУ']

    def main(self, path_to_out_file=None):
        if pd.isna(path_to_out_file) or path_to_out_file == '': path_to_out_file = os.path.join(os.getcwd(),
                                                                                                'Aggregato result.xlsx')

        link_to_directory_reports = self.config_aggregato.get_all_config_program().get('link to directory reports', '')
        if link_to_directory_reports is None or link_to_directory_reports == '': return None
        reading_data = self.report_handler(link_to_directory_reports)
        result_data, result_data_cut_out = self.data_filtering(reading_data)

        writer = ExcelInserter(path_to_out_file)
        writer.insert_data({0: result_data}, 'Сводная таблица')
        writer.insert_data({0: result_data_cut_out}, 'cut out')
        return path_to_out_file

    def data_filtering(self, input_data: dict):
        result_data = {}
        result_update_data = {}
        result_cut_out = {}

        for name_directori_report, data_directori_report in input_data.items():
            for name_work_central, data_work_central in data_directori_report.items():
                for c_row, data_row in data_work_central.items():
                    value_date = data_row.get('Дата', None)

                    if pd.isna(value_date) or value_date == 'NaT': continue

                    name_key_dse = 'Наименование'
                    headers_input = data_row.keys()
                    for name_key_dse in self.list_name_dse:
                        if name_key_dse in headers_input: break
                    if 'Наименование' in headers_input and 'Наименование.1' in headers_input:
                        for name_key_dse in self.list_name_dse:
                            if not name_key_dse in headers_input:
                                name_key_dse = 'Наименование'
                            else:
                                break

                    dse = data_row.get(name_key_dse, '')
                    if pd.isna(dse) or dse == '':
                        dse = data_row.get('Наименование', '')

                    try:
                        date_dse = data_row.get('Дата', '').strftime('%Y.%m.%d')
                    except:

                        date_dse = str(data_row.get('Дата', ''))[:10]

                    result_row = {
                        'РЦ': name_work_central
                        , 'Инф для Нач.бюро': data_row.get('Инф для Нач.бюро', '')
                        , 'Изделие': data_row.get('Изделие', '')
                        , 'ДСЕ': dse
                        , 'Наименование': data_row.get('Наименование', '')
                        , 'нов./ кор./ акт.': data_row.get('нов./ кор./ акт.', '')
                        , 'УП': data_row.get('УП', '')
                        , 'Дата': date_dse
                        , 'Ф. И. О.': data_row.get('Ф. И. О.', '')
                        , 'Получение задания': data_row.get('Получение задания', '')
                        , 'Комментарий': data_row.get('Комментарий', '')
                        , 'Отчет': name_directori_report
                    }

                    result_update_row = result_row.copy()
                    try:
                        del result_update_row['Отчет']
                    except:
                        self.log('pivot_fusion. GHjdklsfjsdkz')

                    if result_update_row in result_update_data.values():
                        result_cut_out[len(result_cut_out)] = result_row
                        continue

                    result_data[len(result_data)] = result_row
                    result_update_data[len(result_data)] = result_update_row

        return result_data, result_cut_out


    def report_handler(self, link_to_directory_reports):
        result_data = {}
        for NAME_DIRECTORY_REPORT in os.listdir(link_to_directory_reports):

            data_directory = ReportHandler(log_callback=self.log).get_data_from_report_directory(
                os.path.join(link_to_directory_reports, NAME_DIRECTORY_REPORT)
            )
            if data_directory is None: continue
            result_data[NAME_DIRECTORY_REPORT] = data_directory

        return result_data


if __name__ == '__main__':
    def seconds_to_minutes_seconds(seconds):
        """
        Преобразует секунды в минуты и секунды.
        """
        seconds = float(f"{seconds:.2f}")
        minutes = 0
        hour = 0

        if seconds >= 60:
            minutes = seconds // 60
        seconds = seconds - minutes * 60

        if minutes >= 60:
            hour = minutes // 60
        minutes = minutes - hour * 60

        return f'{hour} ч., {minutes} мин, {seconds} сек'


    time_start = time.time()

    app = PivotFusionLogic()
    app.main()

    time_stop = time.time()
    print(seconds_to_minutes_seconds(time_stop - time_start))
