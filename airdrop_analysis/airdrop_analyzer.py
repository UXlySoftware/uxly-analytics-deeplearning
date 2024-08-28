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
    
    def get_communities(self, param: GraphQueryParameters) -> dict:
        graph = self.__builder.build_graph_from_distributor(param)
        partition, _ = self.__nx_builder.get_louvain_partition(graph)
        return self.__get_communities_from_partition(partition)

    def get_graph_summary(self, param: GraphQueryParameters) -> dict:
        graph = self.__builder.build_graph_from_distributor(param)
        analysis = self.__analyzer.analyze(graph)
        if param.partition:
            partition, _ = self.__nx_builder.get_louvain_partition(graph)
            communities = self.__get_communities_from_partition(partition)
            analysis['communities'] = len(communities)
        return analysis