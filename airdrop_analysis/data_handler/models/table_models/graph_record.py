from peewee import CharField, DateTimeField, IntegerField, FloatField
import json

from data_handler.models.table_models.base_model import BaseModel
from utils.custom_keys import CustomKeys as ck

class Graph_Record(BaseModel):
    user_id = CharField()
    time_stamp = DateTimeField()
    graph_path = CharField()
    
    def create_from(user_id : str , graph_path : str , time_stamp : str):
        return Graph_Record.create(
            user_id = user_id,
            time_stamp = time_stamp,
            graph_path = graph_path
        )
    
    def to_dict(data):
        return {
            "user_id": data.user_id,
            "time_stamp": str(data.time_stamp),
            "graph": data.graph_path
        }