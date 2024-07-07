from typing import Tuple

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

    def get_wallet_token_transfer_history(
            self,
            params: TokenTransfersQueryParameters,
        ) -> Tuple[TransactionHistory, Address_Record]:
        transfers = None
        if params.cached_first:
            transfers = self.__database_handler.get_token_transfers_by_address(
                params.address,
        )
        if transfers is not None:
            return transfers
        tnxs, cursor = self.__moralis_handler.query_wallet_token_transfers(
            params,
        )
        d = params.to_dict()
        transfers = self.__database_handler.create_wallet_token_transfers(
            params.chain, 
            tnxs,
        )
        d[ck.TRANSACTIONS] = transfers
        d[ck.CURSOR] = cursor
        d[ck.CHAIN] = params.chain
        history = TransactionHistory.from_dict(d)
        record = self.__database_handler.create_wallet_record(history)
        return history, record