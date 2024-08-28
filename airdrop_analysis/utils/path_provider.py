import json
import os
from datetime import datetime

from  utils.custom_keys import CustomKeys as ck


class PathProvider(object):
    
    def __init__(self):
        self.__path_prefix = os.getenv(ck.PREFIX_PATH)
        self.__sep = os.path.sep
        self.__paths = self.__read_paths(os.getenv(ck.PATHS_JSON_PATH))
        if self.__path_prefix != '':
            for key in self.__paths:
                self.__paths[key] = self.__sep.join(
                    [self.__path_prefix, self.__paths[key]],
                ).replace('/', self.__sep)

    def __read_paths(self, paths_json_path: str):
        if self.__path_prefix != '':
            paths_json_path = self.__sep.join(
                [self.__path_prefix, paths_json_path],
            )
        print(self.__path_prefix)
        with open(paths_json_path, 'r') as file:
            self.__paths = json.loads(file.read())
        return self.__paths

    def __getitem__(self, key: str):
        if key not in self.__paths:
            raise Exception(f'Path {key} not found in paths.')
        return self.__paths[key]
    
    def get_api_keys_path(self):
        return self[ck.API_KEYS_PATH]
    
    def get_aws_access_key_path(self):
        return self[ck.AWS_ACCESS_KEYS_PATH]

    def get_claimers_path(self):
        return self[ck.CLAIMERS_PATH]

    def get_table_file_path(self):
        return self[ck.TABLES_FILE_PATH]
    
    def get_airdrop_table_path(self):
        return self[ck.AIRDROPS_DATABASE_PATH]
    
    def get_graph_html_path(self, graph_name: str):
        return self.__sep.join([
            self[ck.GRAPH_HTMLS_FOLDER_PATH].replace('/', self.__sep), 
            graph_name + '.html',
        ])
    
    def get_dex_addresses_path(self):
        return self[ck.DEX_ADDRESSES_PATH]
    
    def get_claimer_lists_json_path(self) -> str:
        return self[ck.CLAIMER_LISTS_JSON_PATH]

    def get_claimer_lists(self) -> dict:
        with open(self.get_claimer_lists_json_path(), 'r') as file:
            return json.loads(file.read())
        
    def get_graph_json_path(self,user_id : str,time_stamp_date : datetime):
        folder_path = self[ck.GRAPH_JSONS_FOLDER_PATH].replace('/', self.__sep)
        try:
            time_stamp = time_stamp_date.strftime(ck.DATETIME_FORMAT)
        except Exception:
            time_stamp = time_stamp_date.strftime(ck.DATETIME_FORMAT_FOR_QUERIED_TRANSFERS)
        arranged_time_stamp = time_stamp.replace(":" , "-")
        if not os.path.exists(f"{folder_path}{user_id}"):
            os.makedirs(f"{folder_path}{user_id}")
        return self.__sep.join(
            [
                f"{folder_path}{user_id}",
                arranged_time_stamp + ".json"
            ]
        )