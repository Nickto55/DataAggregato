import os

from scr.excel_assets.readers.excel_reader import ExcelReader as _ExcelReader

class InitialDataCollector:
    def __init__(self, path_to_pivot_fusion_tabel:str, log_callback=None):
        self.log = log_callback if log_callback else print
        self.path_to_pivot_fusion_tabel = os.path.normpath(path_to_pivot_fusion_tabel)
        self.data_pivot_fusion_tabel = {}

    def main(self):
        reader = _ExcelReader(
            file_path=self.path_to_pivot_fusion_tabel
            , sheet_name='Сводная таблица'
        )
        self.data_pivot_fusion_tabel = reader.get_dict_all_data()

        result_data = self._data_converter()
        return result_data, self.data_pivot_fusion_tabel

    def _data_converter(self):
        result_data = {}
        for row_num,row_data in self.data_pivot_fusion_tabel.items():

            result_data[len(result_data)] = {
                'РЦ': row_data.get('РЦ','')
                ,'ДСЕ':row_data.get('ДСЕ','')
                , 'ФИО':row_data.get('Ф. И. О.','')
                , 'Отчет':row_data.get('Отчет','')
            }
        return result_data




if __name__=='__main__':
    app = InitialDataCollector(r"C:\Users\yakovlev_nd\Desktop\Tests\DataAggregato\Aggregato result.xlsx")
    app.main()