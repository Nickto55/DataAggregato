import os

import pandas as pd

from scr.handling.pivot_fusion.pivot_fusion import PivotFusionLogic
from scr.handling.constructing_resulting_table.constructing_resulting_table import ConstructorResultLogic


class AggregatoMainLogic:
    def __init__(self):
        self.path_to_file = ''

    def start_pivot_fusion_program(self):
        pivot_fusion = PivotFusionLogic()
        pivot_fusion.main(path_to_out_file=self.path_to_file)

    def start_construction_result(self):
        construction_result = ConstructorResultLogic(path_to_pivot_fusion_tabel=self.path_to_file)
        construction_result.main()

    def main(self, path_to_file=None, run_pivot_fusion: bool = False, run_construction_result: bool = False):
        if pd.isna(path_to_file) or path_to_file == '': path_to_file = os.path.join(os.getcwd(), 'Aggregato result.xlsx')
        self.path_to_file = path_to_file

        if run_pivot_fusion: self.start_pivot_fusion_program()
        if run_construction_result: self.start_construction_result()

        return path_to_file


if __name__ == '__main__':
    app = AggregatoMainLogic()
    app.main(
        path_to_file=''
        , run_pivot_fusion=True
        , run_construction_result=True
    )
