from pydantic import BaseModel
from typing import Dict, List, Union

from data_handler.models.base_models.query_parameters import GraphQueryParameters
from data_handler.models.graph_models.node import Node
from data_handler.models.graph_models.edge import Edge
from utils.custom_keys import CustomKeys as ck


class Graph(BaseModel):
    __nodes: Dict[str, Node] = {}
    __edges: Dict[str, Edge] = {}

    @property
    def nodes(self):
        return self.__nodes
    
    @property
    def edges(self):
        return self.__edges

    def add_edge(self, edge: Edge) -> bool:
        if edge.id in self.__edges:
            return False
        self.__edges[edge.id] = edge
        if edge.destination.id not in self.__nodes:
            self.add_node(edge.source)
        if edge.destination.id not in self.__nodes:
            self.add_node(edge.destination)
        return True

    def add_edges(self, edges: List[Edge]):
        for edge in edges:
            self.add_edge(edge)

    def add_node(self, node: Node) -> bool:
        if node.id not in self.__nodes:
            self.__nodes[node.id] = node
        self.add_edges(node.incoming_edges)
        self.add_edges(node.outgoing_edges)
        for edge in self.edges.values():
            if edge.source == node:
                self.__nodes[node.id].add_outgoing_edge(edge)
            elif edge.destination == node:
                self.__nodes[node.id].add_incoming_edge(edge)
        return True
    
    def add_nodes(self, nodes: List[Node]):
        for node in nodes:
            self.add_node(node)

    def delete_edge(self, edge: Union[Edge, str]) -> bool:
        if isinstance(edge, str):
            edge_id = edge
        else:
            edge_id = edge.id
        if edge_id not in self.__edges:
            return False
        edge = self.__edges.pop(edge_id)
        edge.source.delete_edge(edge)
        if len(edge.source.edges) == 0:
            self.delete_node(edge.source)
        edge.destination.delete_edge(edge)
        if len(edge.destination.edges) == 0:
            self.delete_node(edge.destination)
        return True

    def delete_node(self, node: Union[Node, str]) -> bool:
        if isinstance(node, str):
            node_id = node
        else:
            node_id = node.id
        if node_id not in self.__nodes:
            return False
        node = self.__nodes.pop(node_id)
        for edge in node.incoming_edges + node.outgoing_edges:
            self.delete_edge(edge)
        return True

    def clear_children_from_rootless_parents(self):
        nodes_to_delete = []
        for node in self.__nodes.values():
            if node.hierarchy > 0 and not node.incoming_edges:
                nodes_to_delete.append(node)
        for node in nodes_to_delete:
            self.delete_node(node)
        return

    def clear_parents_from_leaf_children(self):
        nodes_to_delete = []
        for node in self.__nodes.values():
            if node.hierarchy < 0 and not node.outgoing_edges:
                nodes_to_delete.append(node)
        for node in nodes_to_delete:
            self.delete_node(node)
        return

    def remove_indirect_nodes(self):
        self.clear_children_from_rootless_parents()
        self.clear_parents_from_leaf_children()

    def get_most_productive_parent(self, hirerarchy: int) -> Node:
        most_productive = None
        for node in self.__nodes.values():
            if node.hierarchy == hirerarchy:
                if most_productive is None or \
                    len(node.outgoing_edges) > \
                        len(most_productive.outgoing_edges):
                    most_productive = node
        return most_productive

    def get_graph_dict(self, communities : dict = {}):
        graph_dict = {}
        graph_dict[ck.NODES] = []
        graph_dict[ck.LINKS] = []
        for node in self.__nodes.values():
            hierarchy = node.hierarchy
            label = node.label
            for key,community in communities.items():
                if label in community:
                    hierarchy = key
                    break
            node_dict = {"id" : node.id , "hierarchy" : hierarchy}
            graph_dict[ck.NODES].append(node_dict)
        for edge in self.__edges.values():
            edge_dict = {"source" : edge.source.id , "target" : edge.destination.id}
            graph_dict[ck.LINKS].append(edge_dict)
        return graph_dict

    def __contains__(self, node: Union[Node, str]) -> bool:
        if isinstance(node, str):
            return node in self.__nodes
        else:
            return node.id in self.__nodes       
