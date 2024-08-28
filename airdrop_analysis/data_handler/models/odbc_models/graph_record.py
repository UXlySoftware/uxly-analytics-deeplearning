from utils.custom_keys import CustomKeys as ck

class Graph_Record:
    def __init__(self, user_id, time_stamp, graph_path):
        self.user_id = user_id
        self.time_stamp = time_stamp
        self.graph_path = graph_path

    @staticmethod
    def create_from_dict(data: dict):
        return Graph_Record(
            user_id=data[ck.USER_ID],
            time_stamp=data[ck.TIME_STAMP],
            graph_path=data[ck.GRAPH_PATH],
        )
    
    @staticmethod
    def create_from(user_id : str , graph_path : str , time_stamp : str):
        return Graph_Record(
            user_id = user_id,
            time_stamp = time_stamp,
            graph_path = graph_path
        )
    
    def to_dict(self):
        return {
            ck.USER_ID: self.user_id,
            ck.TIME_STAMP: str(self.time_stamp),
            ck.GRAPH_PATH: self.graph_path
        }