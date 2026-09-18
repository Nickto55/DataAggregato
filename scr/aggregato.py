import os

import pandas as pd

from scr.handling.pivot_fusion.pivot_fusion import PivotFusionLogic
from scr.handling.constructing_resulting_table.constructing_resulting_table import ConstructorResultLogic


#555 noinspection PyArgumentList
class AggregatoMainLogic:
    def __init__(self,log_callback=None):
        self.path_to_file = ''
        self.log = log_callback if log_callback else print

    def start_pivot_fusion_program(self):
        pivot_fusion = PivotFusionLogic(log_callback=self.log)
        pivot_fusion.main(path_to_out_file=self.path_to_file)

    def start_construction_result(self):
        construction_result = ConstructorResultLogic(path_to_pivot_fusion_tabel=self.path_to_file, log_callback=self.log)
        construction_result.main()

    def main(self, path_to_file=None, run_pivot_fusion: bool = False, run_construction_result: bool = False):
        if pd.isna(path_to_file) or path_to_file == '': path_to_file = os.path.join(os.getcwd(), 'Aggregato result.xlsx')
        self.log('Начинаем загрузку данных...', color_log='green', level='special')
        self.path_to_file = path_to_file

        if run_pivot_fusion:
            self.log('Запуск программы для сбора ежемесячных отчетов', color_log='#a96b21', level='special')
            self.start_pivot_fusion_program()
        if run_construction_result:
            self.log('Запуск программы для сверки ФИО', color_log='#a96b21', level='special')
            self.start_construction_result()


        return path_to_file


if __name__ == '__main__':
    app = AggregatoMainLogic()
    app.main(
        path_to_file=''
        , run_pivot_fusion=True
        , run_construction_result=True
    )
