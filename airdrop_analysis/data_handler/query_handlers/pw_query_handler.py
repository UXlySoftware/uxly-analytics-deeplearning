from datetime import datetime
import json
from peewee import DoesNotExist

from data_handler.models.table_models.base_model import db
from data_handler.models.table_models.address_record import Address_Record
from data_handler.models.table_models.token_transfer import Token_Transfer
from data_handler.models.table_models.graph_record import Graph_Record
from data_handler.models.base_models.transaction_history \
    import TransactionHistory
from utils.path_provider import PathProvider
from utils.custom_keys import CustomKeys as ck

class PWQueryHandler(object):
    def __init__(self):
        self.__path_provider = PathProvider()
        db.create_tables([Address_Record, Token_Transfer, Graph_Record], safe=True)

    def create_wallet_token_transfers(self, chain: str, transfers: list):
        transfer_models = []
        for t in transfers:
            transfer_models.append(Token_Transfer.create_from_dict(chain, t))
        return transfer_models

    def get_token_transfers_by_address(self, address: str):
        return Token_Transfer.select().where(
            (Token_Transfer.from_address==address) | \
                (Token_Transfer.to_address==address),
         )

    def get_wallet_token_transfers_from_address(self, address: str):
        return Token_Transfer.select().where(
            (Token_Transfer.from_address==address),
        )

    def get_wallet_token_transfers_to_address(self, address: str):
        return Token_Transfer.select().where(
            (Token_Transfer.to_address==address),
        )

    def create_wallet_record(self, history: TransactionHistory):
        address = self.get_address_record(history.address)
        if address is not None:
            return address
        return Address_Record.create_from(history)
    
    def get_address_record(self, address: str):
        try:
            return Address_Record.get(Address_Record.address==address)
        except DoesNotExist:
            return None
    
        
    def update_address_record(self, address, data: dict[str, any]):
        for key,value in data.items():
            address_record = Address_Record.update({key: value}) \
            .where(Address_Record.address == address)
            address_record.execute()
    def create_graph_record(self, user_id : str, graph: dict):
        time_now = datetime.now().strftime(ck.DATETIME_FORMAT_FOR_QUERIED_TRANSFERS)
        graph_path = self.__path_provider.get_graph_json_path(user_id,time_now)
        with open(graph_path,"w") as file:
            graph_string = json.dumps(graph)
            file.write(graph_string)
        return Graph_Record.create_from(user_id,graph_path,time_now)
    
    def get_graph_records(self,user_id : str):
        return Graph_Record.select().where(Graph_Record.user_id==user_id)
        