import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scr.config_assets._receiver_config import ReceiverConfig


class ConfigMainProgram:
    def __init__(self, log_callback=None):
        self.log = log_callback if log_callback else print

        self.data_base = ReceiverConfig()
        self.config_section_classification = 'program'

    def get_all_config_program(self):
        self.data_base.load()
        return self.data_base.data.get(self.config_section_classification, '')

    def set_config_progrm(self, key, data):
        if key in self.data_base.data.get(self.config_section_classification, '').keys():
            self.data_base.data[self.config_section_classification][key] = data
            self.data_base.save()
            self.data_base.load()

    def get_size_config(self):
        self.data_base.load()
        return self.data_base.data[self.config_section_classification].get('size', '')

    def set_size_config(self, key_name_file, path_to_file):

        data = self.data_base.data[self.config_section_classification].get('size', '')

        if key_name_file in data.keys():
            self.data_base.data[self.config_section_classification]["size"][key_name_file] = path_to_file
            self.data_base.save()
            self.data_base.load()
        else:
            self.log(
                f"Данного ключа('{key_name_file:<15}') нет в словаре 'size', возможные варианты {list(data.keys())}"
            )
            # CTkMessagebox(
            #     title="Не критическая ошибка",
            #     message=f"Ошибка при записи размера\nКлюча ('{key_name_file}') нет в словаре 'size'\nПуть к файлу не сохранен",
            #     icon="warning", option_1="Не сохранять путь"
            # )


if __name__ == "__main__":
    app = ConfigMainProgram()
