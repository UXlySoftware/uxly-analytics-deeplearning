import json
from typing import List, Dict
import pandas as pd

from data_handler.networkx_builder import NetworkXBuilder
from data_handler.query_handlers.chain_query_controller import \
    ChainQueryController
from data_handler.models.base_models.transaction_history \
    import TransactionHistory
from data_handler.models.base_models.query_parameters import \
    TokenTransfersQueryParameters, GraphQueryParameters
from data_handler.models.odbc_models.token_transfer import Token_Transfer
from data_handler.models.graph_models.node import Node
from data_handler.models.graph_models.edge import Edge
from data_handler.models.graph_models.graph import Graph
from utils.custom_keys import CustomKeys as ck

Edge.model_rebuild()
Node.model_rebuild()

class GraphBuilder():
    def __init__(self, api_keys_path: str, dex_addresses_path: str):
        self.__controller = ChainQueryController(api_keys_path)
        self.__get_dex_addresses_from_csv(dex_addresses_path)
        self.__graph = Graph()
        self.__current_query_params = None
        self.__current_hirerarchy_stack = []
        self.__nx_builder = NetworkXBuilder()

    def __get_dex_addresses_from_csv(self,dex_addresses_path):
        dex_info = pd.read_csv(dex_addresses_path)
        self.__dex_addresses = dex_info["addresses"].str.lower().to_list()
        return self.__dex_addresses
    
    def __get_transactions_query_params(
            self,
            address: str,
            params: GraphQueryParameters,
        ) -> TokenTransfersQueryParameters:
        return TokenTransfersQueryParameters(
            address=address,
            chain=params.chain,
            contract_addresses=params.contract_addresses,
            from_date=params.from_date,
            to_date=params.to_date,
            order=params.edge_order,
            limit=params.edge_limit if params.edge_limit > 0 else 100,
        )

    def __get_parent_addresses(self, sender_addresses: List[str]) -> List[str]:
        if self.__current_query_params.edge_limit > 0:
            return sender_addresses[:self.__current_query_params.edge_limit]
        else:
            return sender_addresses

    def __create_node(self, address: str, hirerarchy: int) -> Node:
        if address in self.__graph:
            return self.__graph.nodes[address]
        node = Node(id=address, hierarchy=hirerarchy)
        self.__graph.add_node(node)
        return node

    def __check_indirect_node(self) -> bool:
        if len(self.__current_hirerarchy_stack) < 3:
            return False
        return self.__current_hirerarchy_stack[-1] == \
            self.__current_hirerarchy_stack[-3]

    def __get_parent_by_address(
            self, 
            address: str,
            parent_hirerarchy: int,
        ) -> Node:
        if address in self.__graph:
            return self.__graph.nodes[address]
        elif self.__check_indirect_node() or \
            parent_hirerarchy <= -self.__current_query_params.parent_depth or \
                address.lower() in self.__dex_addresses:
            return self.__create_node(address, parent_hirerarchy)
        else:
            return self.__query_node(address, parent_hirerarchy)

    def __get_parent_nodes(
            self, 
            sender_addresses: List[str],
            hirerarchy: int,
        ) -> Dict[str, Node]:
        parents: Dict[str, Node] = {}
        for address in sender_addresses:
            parents[address] = self.__get_parent_by_address(
                address, 
                hirerarchy - 1,
            )
        return parents

    def __get_children_addresses(
            self, 
            receiver_addresses: List[str],
        ) -> List[str]:
        if self.__current_query_params.edge_limit > 0:
            return receiver_addresses[:self.__current_query_params.edge_limit]
        else:
            return receiver_addresses

    def __get_child_by_address(
            self, 
            address: str,
            child_hirerarchy: int,
        ) -> Node:
        if address in self.__graph:
            return self.__graph.nodes[address]
        elif self.__check_indirect_node() or \
            child_hirerarchy >= self.__current_query_params.child_depth or \
                address.lower() in self.__dex_addresses:
            return self.__create_node(address, child_hirerarchy)
        else:
            return self.__query_node(address, child_hirerarchy)

    def __get_children_nodes(
            self, 
            receiver_addresses: List[str],
            hirerarchy: int,
        ) -> Dict[str, Node]:
        children_nodes: Dict[str, Node] = {}
        for address in receiver_addresses:
            children_nodes[address] = self.__get_child_by_address(
                address, 
                hirerarchy + 1,
            )
        return children_nodes

    def __get_edge_from_transaction(
            self, 
            transaction: Token_Transfer,
            source: Node,
            destination: Node,
        ) -> List[Edge]:
            token_name = transaction.token_name
            value = transaction.value
            timestamp = transaction.block_timestamp
            return Edge(
                source=source,
                destination=destination,
                edge_type= token_name if token_name is not None else '',
                edge_value= value if value is not None else 0,
                edge_timestamp= timestamp if timestamp is not None else '',
            )

    def __get_incoming_edges(
            self, 
            destination: Node,
            parents: Dict[str, Node],
            received_transactions: List[Token_Transfer],
        ) -> List[Edge]:
        incoming_edges: List[Edge] = []
        for transaction in received_transactions:
            if transaction.from_address in parents:
                edge = self.__get_edge_from_transaction(
                    transaction,
                    parents[transaction.from_address],
                    destination,
                )
                incoming_edges.append(edge)
        return incoming_edges

    def __get_outgoing_edges(
            self,
            source: Node,
            children: Dict[str, Node],
            sent_transactions: List[Token_Transfer],
        ) -> List[Edge]:
        outgoing_edges: List[Edge] = []
        for transaction in sent_transactions:
            if transaction.to_address in children:
                edge = self.__get_edge_from_transaction(
                    transaction,
                    source,
                    children[transaction.to_address],
                )
                outgoing_edges.append(edge)
        return outgoing_edges

    def __get_node_from_transaction_history(
            self,
            history: TransactionHistory,
            hirerarchy: int,
        ) -> Node:
        self.__current_hirerarchy_stack.append(hirerarchy)
        node = self.__create_node(history.address, hirerarchy)
        sender_addresses = history.get_sender_addresses()
        parent_addresses = self.__get_parent_addresses(sender_addresses)
        parents = self.__get_parent_nodes(parent_addresses, hirerarchy)
        received_tnxs = history.get_received_transactions()
        incoming = self.__get_incoming_edges(node, parents, received_tnxs)
        node.add_incoming_edges(incoming)
        receiver_addresses = history.get_receiver_addresses()
        children_addresses = self.__get_children_addresses(receiver_addresses)
        childrens = self.__get_children_nodes(children_addresses, hirerarchy)
        sent_tnxs = history.get_sent_transactions()
        outgoing = self.__get_outgoing_edges(node, childrens, sent_tnxs)
        node.add_outgoing_edges(outgoing)
        self.__current_hirerarchy_stack.pop()
        return node

    def __query_node(
            self,
            address: str,
            hirerarchy: int,
        ) -> Node:
        if  address in self.__graph:
            return self.__graph.nodes[address]
        params = self.__get_transactions_query_params(
            address,
            self.__current_query_params,
        )
        hist, _ = self.__controller.get_wallet_token_transfer_history(params)
        return self.__get_node_from_transaction_history(hist, hirerarchy)

    def __query_nodes(
            self,
            addresses: List[str],
            hirerarchy: int,
        ) -> List[Node]:
        nodes: List[Node] = []
        for address in addresses:
            node = self.__query_node(address, hirerarchy)
            nodes.append(node)
        self.__graph.add_nodes(nodes)
        return nodes

    def build_graph(self, params: GraphQueryParameters) -> Graph:
        self.__current_query_params = params
        self.__graph = Graph()
        self.__query_nodes(params.center_addresses, 0)
        for dex_address in self.__dex_addresses:
            self.__graph.delete_node(dex_address)
        return self.__graph
    
    def build_graph_from_distributor(
            self, 
            params: GraphQueryParameters, 
        ) -> Graph:
        hist_p = self.__get_transactions_query_params(
            params.center_addresses[0],
            params,
        )
        hist, _ = self.__controller.get_wallet_token_transfer_history(hist_p)
        params.center_addresses = hist.get_receiver_addresses()
        g = self.build_graph(params)
        center = self.__get_node_from_transaction_history(hist, 0)
        g.add_node(center)
        for dex_address in self.__dex_addresses:
            g.delete_node(dex_address)
        result_dict = self.__get_result_dict(g,params)
        self.__save_graph(result_dict,params)
        return g
    
    def build_graph_json(self, params : GraphQueryParameters):
        graph = self.build_graph_from_distributor(params)
        result_dict = self.__get_result_dict(graph,params)
        return self.__dict_to_json(result_dict)
    
    def __save_graph(self, result_dict : dict, params: GraphQueryParameters):
        return self.__controller.save_graph_record(params.user_id,result_dict)
    
    def __get_result_dict(self, graph: Graph , params: GraphQueryParameters):
        communities = {}
        if params.partition:
            partition, _ = self.__nx_builder.get_louvain_partition(graph)
            communities = self.get_communities_from_partition(partition)
        result_dict = graph.get_graph_dict()
        result_dict[ck.PARAMETERS] = self.__dict_to_json(params.to_dict())
        return result_dict
    
    def __dict_to_json(self,data):
        dict_string = json.dumps(data)
        return json.loads(dict_string)
    
    def get_communities_from_partition(self, partition: dict) -> dict:
        communities: dict[str, list] = {}
        for nodeID, communityID in partition.items():
            if communityID not in communities:
                communities[communityID] = []
            communities[communityID].append(nodeID)
        return communities

    def get_communities(self, param: GraphQueryParameters) -> dict:
        graph = self.build_graph_from_distributor(param)
        partition, _ = self.__nx_builder.get_louvain_partition(graph)
        return self.get_communities_from_partition(partition)