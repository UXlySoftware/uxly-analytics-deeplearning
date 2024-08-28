from pydantic import BaseModel
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from data_handler.models.graph_models.node import Node


class Edge(BaseModel):
    source: 'Node'
    destination: 'Node'
    edge_type: str
    edge_value: float
    edge_timestamp: datetime

    def __init__(
            self,
            source: 'Node',
            destination: 'Node',
            edge_type: str,
            edge_value: float,
            edge_timestamp: str,
        ):
        super().__init__(
            source=source,
            destination=destination,
            edge_type=edge_type,
            edge_value=edge_value,
            edge_timestamp=edge_timestamp,
        )
        source.add_outgoing_edge(self)
        destination.add_incoming_edge(self)

    @property
    def id(self):
        return f'{self.source.id} -> {self.destination.id}'

    def to_dict(self):
        return self.model_dump()