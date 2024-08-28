import os
import pandas as pd
from utils.custom_keys import CustomKeys as ck

os.environ[ck.PREFIX_PATH] = 'airdrop_analysis'
os.environ[ck.DATABASE_URL] = \
    os.environ[ck.DATABASE_URL].replace('./', f'{os.environ[ck.PREFIX_PATH]}/')

from data_handler.graph_builder import GraphBuilder
from data_handler.networkx_builder import NetworkXBuilder
from data_handler.models.base_models.query_parameters import \
    GraphQueryParameters
from data_handler.models.graph_models.graph import Graph
from utils.path_provider import PathProvider
from airdrop_analyzer import AirdropAnalyzer


class GraphBuilderTest():

    def __init__(self):
        self.__path_provider = PathProvider()
        self.__builder = GraphBuilder(
            self.__path_provider.get_api_keys_path(),
            self.__path_provider.get_dex_addresses_path()
        )
        self.__nx_builder = NetworkXBuilder()
        self.__analyzer = AirdropAnalyzer()
        self.__claimers = pd.read_csv(
            self.__path_provider[ck.CLAIMERS_PATH],
            )

    def __report_most_productive_parent(self, graph: Graph):
        most_productive_parent = graph.get_most_productive_parent(-1)
        if most_productive_parent is not None:
            print('most_productive_parent:', most_productive_parent.id)
            children_count = len(most_productive_parent.outgoing_edges)
            print('children_count:', children_count)
        return

    def __show_graph(self, graph: Graph, with_partition: bool = False):
        graph.remove_indirect_nodes()
        self.__report_most_productive_parent(graph)
        file_path = self.__path_provider.get_graph_html_path('test_graph')
        g = self.__nx_builder.get_directed_nx_graph(graph)
        if with_partition:
            partition, _ = self.__nx_builder.get_louvain_partition(graph)
            g = self.__nx_builder.colorize_graph_by_partition(g, partition)
        self.__nx_builder.visualize_with_pyvis(g, file_path, show=True)
        return g

    def __test_building_graph_with_limit_one(self, n: int = 5):
        addresses = self.__claimers.iloc[:n][ck.WALLET_ADDRESS]
        contract_addresses = ['0x4ed4e862860bed51a9570b96d89af5e1b0efefed']
        param1 = GraphQueryParameters(
            center_addresses=addresses.to_list(),
            chain='base',
            contract_addresses=contract_addresses,
            from_date='2023-12-01T00:00:00Z',
            to_date='2024-06-01T00:00:00Z',
            parent_depth=3,
            child_depth=3,
            edge_limit=5,
            edge_order=ck.DESC,
            partition=True,
            )
        g = self.__builder.build_graph(param1)
        return self.__show_graph(g, with_partition=param1.partition)

    def __test_visualizing_distribution_graph(self):
        param = GraphQueryParameters(
            center_addresses=['0xa2a5c549a454a1631ff226e0cf8dc4af03a61a75'],
            chain='base',
            contract_addresses=['0x4ed4e862860bed51a9570b96d89af5e1b0efefed'],
            from_date='2023-12-01T00:00:00Z',
            to_date='2024-06-01T00:00:00Z',
            parent_depth=1,
            child_depth=1,
            edge_limit=-1,
            edge_order=ck.DESC,
            partition=False,
        )
        g = self.__builder.build_graph_from_distributor(param)
        return self.__show_graph(g, with_partition=param.partition)
    
    def __test_getting_communities(self):
        param = GraphQueryParameters(
            center_addresses=['0xa2a5c549a454a1631ff226e0cf8dc4af03a61a75'],
            chain='base',
            contract_addresses=['0x4ed4e862860bed51a9570b96d89af5e1b0efefed'],
            from_date='2023-12-01T00:00:00Z',
            to_date='2024-06-01T00:00:00Z',
            parent_depth=1,
            child_depth=1,
            edge_limit=-1,
            edge_order=ck.DESC,
            partition=True,
        )
        communities = self.__analyzer.get_communities(param)
        return communities

    def run_tests(self):
        # self.__test_building_graph_with_limit_one()
        # self.__test_visualizing_distribution_graph()
        self.__test_getting_communities()
        return

