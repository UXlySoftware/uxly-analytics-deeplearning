from dotenv import load_dotenv
load_dotenv()

# from tests.query_tests.chain_query_controller_test import ChainQueryControllerTest
from tests.query_tests.graph_builder_test import GraphBuilderTest
from tests.query_tests.chain_query_controller_test import ChainQueryControllerTest


def main():
    test = ChainQueryControllerTest()
    test.run_tests()
    # test = GraphBuilderTest()
    # test.run_tests()

if __name__ == '__main__':
    main()