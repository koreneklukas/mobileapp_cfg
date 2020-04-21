import pandas as pd
import os
from openpyxl import load_workbook
from datetime import datetime


class CreateJSON:
    def __init__(self, excel):
        self.excel = excel

    def _read_xlsx(self):
        df = pd.ExcelFile(self.excel)
        df_list = []
        sheets = []
        for sheet in df.sheet_names:
            if "4json" in sheet:
                sheets.append(sheet)
                df_new = pd.read_excel(self.excel, sheet_name=sheet)
                df_list.append(df_new)
        return df_list, sheets

    def _get_sheet_tree(self):
        tree = {}
        df_list, sheets = self._read_xlsx()
        for i in range(len(sheets)):
            keys = []
            for k in df_list[i].keys():
                keys.append(k)
            tree.update({sheets[i]: keys})
        return tree

    def get_items(self):
        tree = self._get_sheet_tree()
        json_list = {}
        for keys in tree.keys():
            js_lst = []
            jsonify = {}
            df = pd.read_excel(self.excel, sheet_name=keys)
            c = 0
            while c < len(df[tree[keys][0]]):
                js_gather = {}
                for i in range(len(tree[keys])):
                    value = df[tree[keys][i]][c]
                    item = tree[keys][i]
                    if not isinstance(value, str) and item == 'validTo':
                        js_gather.update({item: str(value.strftime("%Y-%m-%dT21:59:59Z"))})
                    elif not isinstance(value, str) and item == 'visibleFrom':
                        js_gather.update({item: str(value.strftime("%Y-%m-%dT00:00:01Z"))})
                    elif not isinstance(value, str) and item == 'visibleTo':
                        js_gather.update({item: str(value.strftime("%Y-%m-%dT23:59:59Z"))})
                    else:
                        js_gather.update({item: str(value)})
                js_lst.append(js_gather)
                c += 1
            jsonify.update({"OfferJSON": js_lst})
            json_list.update({keys: jsonify})
        return json_list

    def create_json_file(self):
        json_tree = self.get_items()
        return json_tree

    def create_dirs(self, version, dest):
        parent_dir = "tmp"
        directory = "{}\\OfferSettings\\{}".format(dest, version)
        path = os.path.join(parent_dir, directory)
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            path = os.path.join(parent_dir, directory)
        return path

#xjson = CreateJSON(self.excel)

#if __name__ == '__main__':
 #   xjson.create_dirs(2.222222,'CZ')
