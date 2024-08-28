from typing import Optional
import json

from data_handler.query_handlers.chain_query_controller import ChainQueryController
from data_handler.claimer_list_provider import ClaimerListProvider
from data_handler.graph_builder import GraphBuilder
from data_handler.networkx_builder import NetworkXBuilder
from data_handler.models.base_models.query_parameters import \
    GraphQueryParameters, ClaimersGraphParameters
from data_handler.models.graph_models.graph import Graph
from graph_handler.graph_analyzer import GraphAnalyzer
from utils.path_provider import PathProvider
from utils.custom_keys import CustomKeys as ck


class AirdropAnalyzer:
    def __init__(self):
        self.__path_provider = PathProvider()
        self.__builder = GraphBuilder(
            self.__path_provider.get_api_keys_path(),
            self.__path_provider.get_dex_addresses_path()
        )
        self.__controller = ChainQueryController(
            self.__path_provider.get_api_keys_path()
        )
        self.__nx_builder = NetworkXBuilder()
        self.__analyzer = GraphAnalyzer()
        self.__list_provider = ClaimerListProvider()

    def get_graph_html(
            self,
            graph: Graph,
            with_partition: Optional[bool] = False,
            clean: Optional[bool] = True,
        ) -> str:
        if clean:
            graph.remove_indirect_nodes()
        file_path = self.__path_provider.get_graph_html_path('test_graph')
        if with_partition:
            partition, _ = self.__nx_builder.get_louvain_partition(graph)
            g = self.__nx_builder.get_directed_nx_graph(graph)
            g = self.__nx_builder.colorize_graph_by_partition(g, partition)
        else:
            g = self.__nx_builder.get_directed_nx_graph(graph)
        html = self.__nx_builder.visualize_with_pyvis(
            g,
            file_path, 
            show=False,
        )
        return html

    def get_claimers_graph(self, param: ClaimersGraphParameters) -> str:
        param = self.__list_provider.adjust_params_for_claimer_list(param)
        graph = self.__builder.build_graph(param)
        return self.get_graph_html(graph,with_partition=param.partition)

    def get_distribution_graph(self, param: GraphQueryParameters) -> str:
        graph = self.__builder.build_graph_from_distributor(param)
        return self.get_graph_html(graph,with_partition=param.partition)

    def get_distribution_graph_json(self, param: GraphQueryParameters):
        graph_json = self.__builder.build_graph_json(param)
        return graph_json
    
    def get_graph_records_from_user_id(self,user_id: str):
        return self.__controller.get_graph_records(user_id)
    
    def __get_communities_from_partition(self, partition: dict) -> dict:
        communities: dict[str, list] = {}
        for nodeID, communityID in partition.items():
            if communityID not in communities:
                communities[communityID] = []
            communities[communityID].append(nodeID)
        return communities
    
    def __control_chain_like_pattern(self, communities: dict, graph: Graph) -> dict:
        chains = {}
        visited = set()
        min_length = 8
        for node in graph.nodes.values():
            if node.label not in visited:
                for neighbor in graph.get_neighbors(node):
                    if (node.label, neighbor.label) not in visited:
                        chain = [node.label]
                        current_node = neighbor
                        previous_node = node
                        
                        while True:
                            visited.add((previous_node.label, current_node.label))
                            if self.__is_neighbor_in_same_community(previous_node, current_node, communities):
                                chain.append(current_node.label)
                                neighbors = list(graph.get_neighbors(current_node))
                                next_node = [n for n in neighbors if n != previous_node]
                                if len(next_node) == 0:
                                    break
                                previous_node = current_node
                                current_node = next_node[0]
                            else:
                                break
                            
                        if len(chain) >= min_length:
                            chains[node.label] = chain
        # print(chains)
        return chains
    
    def __control_star_like_pattern(self, communities: dict, graph: Graph) -> dict:
        threshold = 3
        poss_inc_star_nodes = []
        poss_out_star_nodes = []
        for node in graph.nodes.values():
            if len(node.outgoing_edges) >= threshold:
                poss_out_star_nodes.append(node)
            if len(node.incoming_edges) >= threshold:
                poss_inc_star_nodes.append(node)
        star_patterns = {}
        for node in poss_inc_star_nodes:
            neighbors = [neighbor.source for neighbor in node.incoming_edges]
            neighbors_same_com = self.__is_neighbors_in_same_community(node, neighbors, communities)
            if len(neighbors_same_com) > 0:
                star_patterns[node.label] = neighbors_same_com
        for node in poss_out_star_nodes:
            neighbors = [neighbor.destination for neighbor in node.incoming_edges]
            neighbors_same_com = self.__is_neighbors_in_same_community(node, neighbors, communities)
            if len(neighbors_same_com) > 0:
                try:
                    star_patterns[node.label].extend(neighbors_same_com)
                except Exception :
                    star_patterns[node.label] = neighbors_same_com
        # print(star_patterns)
        return star_patterns
    
    def __is_neighbors_in_same_community(self, node , neighbors, communities):
        neighbors_same_com = []
        for neighbor in neighbors:
            if self.__is_neighbor_in_same_community(node, neighbor, communities):
                if node.label != neighbor.label:
                    neighbors_same_com.append(neighbor.label)
        return neighbors_same_com
    
    def __is_neighbor_in_same_community(self, node, neighbor, communities):
        for community in communities.values():
            if node.label in community:
                if neighbor.label in community:
                    return True
                break
        return False
    
    def get_communities(self, param: GraphQueryParameters) -> dict:
        graph = self.__builder.build_graph_from_distributor(param)
        partition, _ = self.__nx_builder.get_louvain_partition(graph)
        communities = self.__get_communities_from_partition(partition)
        self.__control_chain_like_pattern(communities, graph)
        self.__control_star_like_pattern(communities, graph)
        return communities

    def get_graph_summary(self, param: GraphQueryParameters) -> dict:
        graph = self.__builder.build_graph_from_distributor(param)
        analysis = self.__analyzer.analyze(graph)
        if param.partition:
            partition, _ = self.__nx_builder.get_louvain_partition(graph)
            communities = self.__get_communities_from_partition(partition)
            analysis['communities'] = len(communities)
        return analysis