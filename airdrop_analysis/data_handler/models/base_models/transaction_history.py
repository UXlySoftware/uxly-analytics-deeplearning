from pydantic import BaseModel
from typing import Optional, List

from data_handler.models.odbc_models.token_transfer import Token_Transfer
from utils.custom_keys import CustomKeys as ck


class TransactionHistory(BaseModel):
    address: str
    chain: str
    transactions: List[Token_Transfer]
    from_date: str
    to_date: str
    contract_addresses: List[str]
    last_cursor: Optional[str] = '0'
    __received_transactions = None
    __sent_transactions = None
    __sender_addresses = None
    __receiver_addresses = None

    @staticmethod
    def from_dict(d: dict):
        if ck.FROM_DATE not in d:
            d[ck.FROM_DATE] = ''
        if ck.TO_DATE not in d:
            d[ck.TO_DATE] = ''
        if ck.CONTRACT_ADDRESSES not in d:
            d[ck.CONTRACT_ADDRESSES] = []
        return TransactionHistory(
            address=d[ck.ADDRESS],
            chain=d[ck.CHAIN],
            transactions=d[ck.TRANSACTIONS],
            from_date=d[ck.FROM_DATE],
            to_date=d[ck.TO_DATE],
            contract_addresses=d[ck.CONTRACT_ADDRESSES],
            last_cursor=d[ck.CURSOR],
        )

    def get_transaction_count(self) -> int:
        return len(self.transactions)

    def get_received_transactions(self) -> List[Token_Transfer]:
        if self.__received_transactions is None:
            self.__received_transactions = \
            [tx for tx in self.transactions if tx.to_address == self.address]
            self.__received_transactions = sorted(
                self.__received_transactions, 
                key=lambda tx: tx.block_timestamp,
            )
        return self.__received_transactions
    
    def get_sent_transactions(self) -> List[Token_Transfer]:
        if self.__sent_transactions is None:
            self.__sent_transactions = \
            [tx for tx in self.transactions if tx.from_address == self.address]
            self.__sent_transactions = sorted(
                self.__sent_transactions, 
                key=lambda tx: tx.block_timestamp,
            )
        return self.__sent_transactions
    
    def get_sender_addresses(self) -> List[str]:
        if self.__sender_addresses is None:
            sent_transactions = self.get_received_transactions()
            seen_addresses = set()
            self.__sender_addresses = []
            for tx in sent_transactions:
                if tx.from_address not in seen_addresses:
                    self.__sender_addresses.append(tx.from_address)
                    seen_addresses.add(tx.from_address)
        return self.__sender_addresses
    
    def get_receiver_addresses(self) -> List[str]:
        if self.__receiver_addresses is None:
            received_transactions = self.get_sent_transactions()
            seen_addresses = set()
            self.__receiver_addresses = []
            for tx in received_transactions:
                if tx.to_address not in seen_addresses:
                    self.__receiver_addresses.append(tx.to_address)
                    seen_addresses.add(tx.to_address)
        return self.__receiver_addresses

    class Config:
        arbitrary_types_allowed = True