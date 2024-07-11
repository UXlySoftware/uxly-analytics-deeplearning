import json
import moralis

from data_handler.models.base_models.query_parameters \
    import TransactionsQueryParameters
from data_handler.models.base_models.query_parameters \
    import StatsQueryParameters
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
            params: TransactionsQueryParameters,
            query: callable,
        ):
        page = query(
            api_key=self.__api_key, 
            params=params.to_dict(),
        )
        return page[ck.RESULT], page[ck.CURSOR]
    
    def __query_wallet_transactions(
            self, 
            params: TransactionsQueryParameters,
            query: callable,
            event: str,
        ):
        address = params.address
        transactions = []
        try:
            while params.cursor is not None:
                tnxs, cursor = self.__query_wallet_transactions_page(
                    params, query,
            )
                transactions.extend(tnxs)
                params.cursor = cursor
                cnt = len(transactions)
                s = f'Queryied {cnt} {event}s for {address}.'
                if params.limit < 300:
                    return transactions, params.cursor
                if params.cursor is not None:
                    s += f' Querying next page...'
                else:
                    s += ' Done.' + ' ' * 25
                print(s, end='\r')
        except Exception as e:
            if 'Reason: Internal Server Error' in str(e):
                print(f'Internal Server Error querying {event}s for {address}')
            else:
                print(e)
        return transactions, params.cursor
    
    
    def query_wallet_transactions(
            self, 
            params: TransactionsQueryParameters,
        ):
        return self.__query_wallet_transactions(
            params, 
            moralis.evm_api.transaction.get_wallet_transactions,
            'transaction',
        )
    
    def query_wallet_token_transfers(
            self, 
            params: TransactionsQueryParameters,
        ):
        return self.__query_wallet_transactions(
            params, 
            moralis.evm_api.token.get_wallet_token_transfers,
            'token transfer',
        )
    
    def query_wallet_stats(
            self, 
            params: StatsQueryParameters,
            ):
        try:
            return moralis.evm_api.wallets.get_wallet_stats(
                api_key=self.__api_key, 
                params=params.to_dict(),
            )
        except Exception as e:
            print(e)
            print(f'Error getting stats for {params.address}')
            return {}