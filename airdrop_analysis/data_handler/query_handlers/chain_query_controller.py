from typing import Tuple
from datetime import datetime
import json

from data_handler.models.table_models.graph_record import Graph_Record
from data_handler.query_handlers.moralis_query_handler \
    import MoralisQueryHandler
from data_handler.query_handlers.pw_query_handler import PWQueryHandler
from data_handler.models.base_models.query_parameters import *
from data_handler.models.table_models.address_record import Address_Record
from data_handler.models.base_models.transaction_history \
    import TransactionHistory
from utils.custom_keys import CustomKeys as ck


class ChainQueryController():
    def __init__(self, api_keys_path: str):
        self.__moralis_handler = MoralisQueryHandler(api_keys_path)
        self.__database_handler = PWQueryHandler()

    def get_address_record(self, address) -> Address_Record:
        return self.__database_handler.get_address_record(address)
    
    def save_graph_record(self,user_id : str, graph : dict):
        return self.__database_handler.create_graph_record(user_id,graph)
    
    def get_graph_records(self,user_id : str):
        graph_records = self.__database_handler.get_graph_records(user_id)
        record_list = []
        for graph in graph_records:
            record_dict = Graph_Record.to_dict(graph)
            record_dict[ck.GRAPH] = self.__read_graph_from_json(record_dict[ck.GRAPH])
            record_string = json.dumps(record_dict)
            record_json = json.loads(record_string)
            record_list.append(record_json)
        return record_list

    def __read_graph_from_json(self,graph_path : str):
        with open(graph_path,"r") as file:
            return json.loads(file.read())

    def __query_wallet_token_transfers(
            self,
            params: TokenTransfersQueryParameters,
        ) -> Tuple[list, str]:
        tnxs, cursor = self.__moralis_handler.query_wallet_token_transfers(
            params,
        )
        transfers = self.__database_handler.create_wallet_token_transfers(
            params.chain, 
            tnxs,
        )
        return transfers, cursor

    def compare_dates(self,date1_str: str,date2_str: str):
        try:
            date1 = datetime.strptime(date1_str,ck.DATETIME_FORMAT)
        except ValueError:
            date1 = datetime.strptime(date1_str,ck.DATETIME_FORMAT_FOR_QUERIED_TRANSFERS)
        try:
            date2 = datetime.strptime(date2_str,ck.DATETIME_FORMAT)
        except ValueError:
            date2 = datetime.strptime(date2_str,ck.DATETIME_FORMAT_FOR_QUERIED_TRANSFERS)
        return (date1-date2).total_seconds()

    def query_not_overlapped_transfers(
        self,
        params: TokenTransfersQueryParameters,
        record: Address_Record
        ):
        transfers = []
        cursor = '0'
        if self.compare_dates(params.from_date,record.from_date) < 0:
            new_params = params.model_copy()
            new_params.to_date = record.from_date
            new_transfers , _ = self.__query_wallet_token_transfers(new_params)
            transfers.extend(new_transfers)
            self.__database_handler.update_address_record(params.address,{ck.FROM_DATE: params.from_date})
        if self.compare_dates(params.to_date,record.to_date) > 0:
            new_params = params.model_copy()
            new_params.from_date = record.to_date
            new_transfers , cursor = self.__query_wallet_token_transfers(new_params)
            transfers.extend(new_transfers)
            self.__database_handler.update_address_record(params.address,{ck.TO_DATE: params.to_date})
        
        return transfers,cursor
    
    def get_wallet_token_transfer_history(
            self,
            params: TokenTransfersQueryParameters,
        ) -> Tuple[TransactionHistory, Address_Record]:
        transfers = None
        d = params.to_dict()
        cursor = '0'
        if params.cached_first:
            record = self.get_address_record(params.address)
            if record is not None:
                not_overlapped_transfers , cursor = self. \
                query_not_overlapped_transfers(params,record)
                transfers = not_overlapped_transfers
                if cursor == '0':
                    cursor = record.last_cursor
                transfers.extend(self.__database_handler.\
                    get_token_transfers_by_address(params.address))
                transfers.sort(
                    key=lambda transfer: 
                        datetime.strptime(transfer.block_timestamp,ck.DATETIME_FORMAT_FOR_QUERIED_TRANSFERS)
                        )
                if params.order == ck.DESC:
                    transfers.reverse()
        if transfers is None or len(transfers) == 0:
            transfers, cursor = self.__query_wallet_token_transfers(params)
        d[ck.TRANSACTIONS] = transfers
        d[ck.CURSOR] = cursor
        history = TransactionHistory.from_dict(d)
        record = self.__database_handler.create_wallet_record(history)
        return history, record