import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scr.config_assets._receiver_config import ReceiverConfig


class ConfigDirectoryReport:
    def __init__(self):
        self.data_base = ReceiverConfig()
        self.config_section_classification = 'directory report'

    def get_all_config_program(self) -> dict[str, dict]:
        self.data_base.load()
        return self.data_base.data.get(self.config_section_classification, '')

    def set_config_progrm(self, key:str, data:dict):
        if key in self.data_base.data.get(self.config_section_classification, '').keys():
            self.data_base.data[self.config_section_classification][key] = data
            self.data_base.save()
            self.data_base.load()

    def add_config_progrm(self, key:str, data:dict):
        if key in self.data_base.data.get(self.config_section_classification, '').keys():
            self.data_base.data[self.config_section_classification][key] = data
        else:
            self.data_base.data[self.config_section_classification].update({key:data})
        self.data_base.save()
        self.data_base.load()


if __name__ == "__main__":
    app = ConfigDirectoryReport()
    app.add_config_progrm(key='dsajk', data={'version':'0213','jdasl':'sajdio'})
