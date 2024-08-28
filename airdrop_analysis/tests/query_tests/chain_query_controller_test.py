import pandas as pd
import json

from data_handler.query_handlers.chain_query_controller \
    import ChainQueryController
from data_handler.query_handlers.chain_query_controller \
    import ChainQueryController
from data_handler.query_handlers.moralis_query_handler \
    import MoralisQueryHandler
from utils.path_provider import PathProvider
from utils.custom_keys import CustomKeys as ck
from data_handler.models.base_models.query_parameters import *
from data_handler.models.base_models.transaction_time import TransactionTime


class ChainQueryControllerTest():

    def __init__(self):
        self.__path_provider = PathProvider()
        self.__controller = ChainQueryController(
            self.__path_provider.get_api_keys_path(),
        )
        self.__moralis_handler = MoralisQueryHandler(
            self.__path_provider.get_api_keys_path()
        )
        self.__claimers = pd.read_csv(self.__path_provider[ck.CLAIMERS_PATH])
        with open(self.__path_provider.get_table_file_path(), 'r') as file:
            self.__tables = json.loads(file.read())
        print(self.__tables)

    def __test_query_wallet_token_transfers_with_contracts(self):
        address = self.__claimers.iloc[36][ck.WALLET_ADDRESS]
        prms1 = TokenTransfersQueryParameters(
            address=address, 
            chain='base',
            cached_first=False,
            from_date='2012-23-01T00:00:00Z',
            to_date='2024-06-01T00:00:00Z',
            )
        history, _ = self.__controller.get_wallet_token_transfer_history(prms1)
        print()
        print(history.get_transaction_count())
        prms2 = TokenTransfersQueryParameters(
            address=address, 
            chain='base',
            cached_first=False,
            from_date='2012-23-01T00:00:00Z',
            to_date='2024-06-01T00:00:00Z',
            contract_addresses=['0x9f07f8a82cb1af1466252e505b7b7ddee103bc91'],
            )
        history, _ = self.__controller.get_wallet_token_transfer_history(prms2)
        print()
        print(history.get_transaction_count())
        return

    def __test_query_wallet_token_transfers(self):
        contract_addresses=['0x4ed4e862860bed51a9570b96d89af5e1b0efefed']
        addresses = self.__claimers[ck.WALLET_ADDRESS].to_list()[150:200]
        for address in addresses:
            params = TokenTransfersQueryParameters(
                address=address, 
                chain='base',
                cached_first=True,
                from_date='2024-01-01T00:00:00Z',
                to_date='2024-07-15T00:00:00Z',
                contract_addresses=contract_addresses,
                )
            history, _ = self.__controller.get_wallet_token_transfer_history(
                params,
            )
        total_time = 0
        length = len(TransactionTime.average_time)
        for i in TransactionTime.average_time:
            total_time += i
        if length > 0:
            print(total_time/length)
            # print(history.get_transaction_count())

    def __test_query_total_token_transfer_count(self):
        contract_addresses=['0x4ed4e862860bed51a9570b96d89af5e1b0efefed']
        addresses = self.__claimers[ck.WALLET_ADDRESS].to_list()[:8]
        for address in addresses:
            params = TokenTransfersQueryParameters(
                address=address, 
                chain='base',
                cached_first=True,
                from_date='2022-01-01T00:00:00Z',
                to_date='2024-05-15T00:00:00Z',
                contract_addresses=contract_addresses,
                )
            count = self.__moralis_handler.query_total_token_transfer_count(params)
            print(count)
    
    def run_tests(self):
        # self.__test_query_wallet_token_transfers_with_contracts()
        self.__test_query_wallet_token_transfers()
        # self.__test_query_total_token_transfer_count()