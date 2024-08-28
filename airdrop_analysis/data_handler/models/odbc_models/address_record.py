from utils.custom_keys import CustomKeys as ck
from data_handler.models.base_models.transaction_history import TransactionHistory


class Address_Record:
    def __init__(self, address, from_date, to_date, balance, total_transaction_count, incoming_transaction_count, outgoing_transaction_count, first_incoming_transaction_date, first_incoming_transaction_source, last_outgoing_transaction_date, last_outgoing_transaction_destination, chain, contract_address, last_cursor):
        self.address = address
        self.from_date = from_date
        self.to_date = to_date
        self.balance = balance
        self.total_transaction_count = total_transaction_count
        self.incoming_transaction_count = incoming_transaction_count
        self.outgoing_transaction_count = outgoing_transaction_count
        self.first_incoming_transaction_date = first_incoming_transaction_date
        self.first_incoming_transaction_source = first_incoming_transaction_source
        self.last_outgoing_transaction_date = last_outgoing_transaction_date
        self.last_outgoing_transaction_destination = last_outgoing_transaction_destination
        self.chain = chain
        self.contract_address = contract_address
        self.last_cursor = last_cursor
        
    @staticmethod
    def create_from_dict(data: dict):
        return Address_Record(
            address=data[ck.ADDRESS],
            from_date=data[ck.FROM_DATE],
            to_date=data[ck.TO_DATE],
            balance=data[ck.BALANCE],
            total_transaction_count=data[ck.TOTAL_TRANSACTION_COUNT],
            incoming_transaction_count=data[ck.INCOMING_TRANSACTION_COUNT],
            outgoing_transaction_count=data[ck.OUTGOING_TRANSACTION_COUNT],
            first_incoming_transaction_date=data[ck.FIRST_INCOMING_TRANSACTION_DATE],
            first_incoming_transaction_source=data[ck.FIRST_INCOMING_TRANSACTION_SOURCE],
            last_outgoing_transaction_date=data[ck.LAST_OUTGOING_TRANSACTION_DATE],
            last_outgoing_transaction_destination=data[ck.LAST_OUTGOING_TRANSACTION_DESTINATION],
            chain=data[ck.CHAIN],
            contract_address=data[ck.CONTRACT_ADDRESS],
            last_cursor=data[ck.LAST_CURSOR],
        )
    
    @staticmethod
    def create_from_history(history: TransactionHistory):
        ins = history.get_received_transactions()
        outs = history.get_sent_transactions()
        first_date, last_date = '', ''
        first_source, last_destination = '', ''
        if ins:
            first_date = ins[0].block_timestamp
            first_source = ins[0].from_address
        if outs:
            last_date = outs[-1].block_timestamp
            last_destination = outs[-1].to_address
        balance = sum([t.value for t in ins]) - sum([t.value for t in outs])
        contract_address = ''
        if history.contract_addresses:
            contract_address = history.contract_addresses[0]
        return Address_Record(
            address=history.address,
            from_date=history.from_date,
            to_date=history.to_date,
            balance=balance,
            total_transaction_count=history.get_transaction_count(),
            incoming_transaction_count=len(ins),
            outgoing_transaction_count=len(outs),
            first_incoming_transaction_date=first_date,
            first_incoming_transaction_source=first_source,
            last_outgoing_transaction_date=last_date,
            last_outgoing_transaction_destination=last_destination,
            chain=history.chain,
            contract_address=contract_address,
            last_cursor=history.last_cursor,
        )