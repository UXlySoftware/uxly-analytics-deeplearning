import pyodbc
from datetime import datetime
import json
import os

from utils.path_provider import PathProvider
from data_handler.models.odbc_models.address_record import Address_Record
from data_handler.models.odbc_models.token_transfer import Token_Transfer
from data_handler.models.odbc_models.graph_record import Graph_Record
from data_handler.models.base_models.transaction_history import TransactionHistory
from utils.custom_keys import CustomKeys as ck

class ODBCQueryHandler:
    def __init__(self):
        self.connection_string = os.getenv(ck.ODBC_CONNECTION_STRING)
        self.__path_provider = PathProvider()

    def get_connection(self):
        return pyodbc.connect(self.connection_string)

    def create_wallet_token_transfers(self, chain: str, transfers: list):
        transfer_models = [
            Token_Transfer.create_from_dict(chain, t) for t in transfers
        ]
        self.insert_token_transfers(transfer_models)
        return transfer_models

    def insert_token_transfers(self, transfers):
        conn = self.get_connection()
        cursor = conn.cursor()
        for transfer in transfers:
            cursor.execute("""
                INSERT INTO token_transfer (from_address, to_address, value, 
                block_timestamp, block_hash, transaction_hash, token_name, 
                contract_address, chain)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transfer.from_address, transfer.to_address, transfer.value, transfer.block_timestamp,
                transfer.block_hash, transfer.transaction_hash, transfer.token_name, 
                transfer.contract_address, transfer.chain
            ))
        conn.commit()
        cursor.close()
        conn.close()

    def get_token_transfers_by_address(self, address: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM token_transfer WHERE from_address = ? OR to_address = ?
        """, (address, address))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [Token_Transfer(*(row[1:])) for row in rows]

    def get_wallet_token_transfers_from_address(self, address: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM token_transfer WHERE from_address = ?
        """, (address,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [Token_Transfer(*(row[1:])) for row in rows]

    def get_wallet_token_transfers_to_address(self, address: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM token_transfer WHERE to_address = ?
        """, (address,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [Token_Transfer(*(row[1:])) for row in rows]

    def create_wallet_record(self, history: TransactionHistory):
        address = self.get_address_record(history.address)
        if address is not None:
            return address
        address_record = Address_Record.create_from_history(history)
        self.insert_address_record(address_record)
        return address_record
        
    
    def insert_address_record(self, address_record: Address_Record):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO address_record (address, from_date, 
            to_date, balance, total_transaction_count, 
            incoming_transaction_count, 
            outgoing_transaction_count, 
            first_incoming_transaction_date, 
            first_incoming_transaction_source, 
            last_outgoing_transaction_date, 
            last_outgoing_transaction_destination, 
            chain, contract_address, last_cursor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            address_record.address, address_record.from_date, 
            address_record.to_date, address_record.balance, 
            address_record.total_transaction_count, 
            address_record.incoming_transaction_count, 
            address_record.outgoing_transaction_count, 
            address_record.first_incoming_transaction_date, 
            address_record.first_incoming_transaction_source, 
            address_record.last_outgoing_transaction_date, 
            address_record.last_outgoing_transaction_destination, 
            address_record.chain, address_record.contract_address, 
            address_record.last_cursor
        ))
        conn.commit()
        cursor.close()
        conn.close()

    def get_address_record(self, address: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT * FROM address_record WHERE address = ?
        """, (address,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return Address_Record(*(row[1:])) if row else None

    def update_address_record(self, address, data: dict[str, any]):
        conn = self.get_connection()
        cursor = conn.cursor()
        for key,value in data.items():
            cursor.execute("""
                UPDATE address_record SET ? = ? WHERE address = ?
            """, (key, value, address))
        conn.commit()
        cursor.close()
        conn.close()

    def create_graph_record(self, user_id : str, graph: dict):
        time_now = datetime.now()
        graph_path = self.__path_provider.get_graph_json_path(user_id,time_now)
        with open(graph_path,"w") as file:
            graph_string = json.dumps(graph)
            file.write(graph_string)
        graph_record = Graph_Record.create_from(user_id,graph_path,time_now)
        self.insert_graph_record(graph_record)
        return graph_record
    
    def insert_graph_record(self, graph_record : Graph_Record):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cached_graph_record (user_id, time_stamp, graph_path)
            VALUES (?, ?, ?)
        """, (
            graph_record.user_id, graph_record.time_stamp, graph_record.graph_path
        ))
        conn.commit()
        cursor.close()
        conn.close()

    def get_graph_records(self, node_id: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM cached_graph_record WHERE user_id = ?
        """, (node_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [Graph_Record(*(row[1:])) for row in rows]