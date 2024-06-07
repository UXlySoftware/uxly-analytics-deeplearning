import json
import moralis

from data_handler.models.base_models.moralis_query_parameters \
    import MoralisTransactionsQueryParameters
from data_handler.models.base_models.moralis_query_parameters \
    import MoralisStatsQueryParameters
from utils.custom_keys import CustomKeys as ck


class MoralisQueryHandler(object):
    def __init__(self, api_keys_path):
        self.__api_key =  self.__read_api_key(api_keys_path)

    def __read_api_key(self, api_keys_path):
        with open(api_keys_path, 'r') as file:
            self.__api_key = json.loads(file.read())
        return self.__api_key[ck.MORALIS]
    
    def __query_wallet_transactions_page(
            self, 
            params: MoralisTransactionsQueryParameters,
        ):
        page = moralis.evm_api.transaction.get_wallet_transactions(
            api_key=self.__api_key, 
            params=params.to_dict(),
        )
        return page[ck.RESULT], page[ck.CURSOR]
    
    def query_wallet_transactions(
            self, 
            params: MoralisTransactionsQueryParameters,
        ):
        address = params.get_address()
        transactions = []
        try:
            while params.get_cursor() is not None:
                tnxs, cursor = self.__query_wallet_transactions_page(params)
                transactions.extend(tnxs)
                params.update_cursor(cursor)
                cnt = len(transactions)
                s = f'Queryied {cnt} transactions for {address}.'
                s += f' Querying next page...'
                print(s, end='\r')
        except Exception as e:
            if 'Reason: Internal Server Error' in str(e):
                print(f'Internal Server Error querying tnxs for {address}')
            else:
                print(e)
        return transactions, params.get_cursor()
    
    def get_wallet_stats(
            self, 
            params: MoralisStatsQueryParameters,
            ):
        try:
            return moralis.evm_api.wallets.get_wallet_stats(
                api_key=self.__api_key, 
                params=params.to_dict(),
            )
        except Exception as e:
            print(e)
            print(f'Error getting stats for {params.get_address()}')
            return {}