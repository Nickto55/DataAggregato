import os

from scr.excel_assets.readers.excel_reader import ExcelReader as _ExcelReader

class InitialDataCNC:
    def __init__(self, path_to_pivot_fusion_tabel: str):
        self.path_to_pivot_fusion_tabel = os.path.normpath(path_to_pivot_fusion_tabel)
        self.data_pivot_fusion_tabel = {}

    def main(self):
        reader = _ExcelReader(
            file_path=self.path_to_pivot_fusion_tabel
            , sheet_name='Сводная таблица'
        )
        self.data_pivot_fusion_tabel = reader.get_dict_all_data()



if __name__=='__main__':
    app = InitialDataCNC(
        path_to_pivot_fusion_tabel=r"C:\Users\yakovlev_nd\Desktop\Tests\DataAggregato\Aggregato result.xlsx"
    )
    app.main()