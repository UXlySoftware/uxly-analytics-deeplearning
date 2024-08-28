import json
import moralis
import os
from requests_html import HTMLSession
from datetime import datetime

from data_handler.models.base_models.transaction_time import TransactionTime
from data_handler.models.base_models.query_parameters \
    import TransactionsQueryParameters , TokenTransfersQueryParameters
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
        transaction_time = TransactionTime(0)
        transactions = []
        try:
            start_time = datetime.now()
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
            end_time = datetime.now()
            difference = (end_time - start_time).total_seconds()
            transaction_time.last_transaction_count = cnt
            if cnt != 0:
                TransactionTime.average_time.append(difference / cnt)
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
    
    def __change_contract_addresses_to_url_string(
        self,
        contract_addresses: list[str]
        ):
        url_string = f"tkn={contract_addresses[0]}"
        for address in contract_addresses:
            url_string += f"%2c{address}"
        return url_string
    
    def __create_scan_url(
        self,
        params: TokenTransfersQueryParameters
        ):
        try:
            primary_url = os.getenv(f"{params.chain.upper()}_URL")
            url = primary_url
            url += self.__change_contract_addresses_to_url_string(params.contract_addresses)
            url += "&txntype=2"
            url += f"&fadd={params.address}"
            url += "&qt=2"
            url += f"&tadd={params.address}"
            url += f"&age={params.from_date}~{params.to_date}"
            return url
        except Exception:
            return ""
    
    def query_total_token_transfer_count(
        self,
        params: TokenTransfersQueryParameters
        ):
        try:
            url = self.__create_scan_url(params)
            session = HTMLSession()
            request = session.get(url)
            count = request.html.search("A total of {} transactions found")[0]
        except Exception:
            count = 0
        return count