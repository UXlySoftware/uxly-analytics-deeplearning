
class CustomKeys:
    # Paths
    PATHS_JSON_PATH = 'paths_json_path'
    PREFIX_PATH = 'prefix_path'
    DATABASE_URL = 'database_url'
    API_KEYS_PATH = 'api_keys_path'
    AWS_ACCESS_KEYS_PATH = 'aws_access_keys_path'
    CLAIMER_LISTS_JSON_PATH = 'claimer_lists_json_path'
    CLAIMERS_PATH = 'claimers_path'
    TABLES_FILE_PATH = 'tables_file_path'
    DEX_ADDRESSES_PATH = 'dex_addresses_path'
    GRAPH_JSONS_FOLDER_PATH = 'graph_jsons_folder_path'

    # API keys
    MORALIS = 'moralis'
    DYNAMODB = 'dynamodb'
    ACCESS_KEY_ID = 'Access key ID'
    SECRET_ACCESS_KEY = 'Secret access key'
    AWS_REGION = 'us-east-1'

    # Query parameters
    CHAIN = 'chain'
    ORDER = 'order'
    ADDRESS = 'address'
    WALLET_ADDRESS = 'wallet_address'
    CONTRACT_ADDRESSES = 'contract_addresses'
    FROM_DATE = 'from_date'
    TO_DATE = 'to_date'
    LIMIT = 'limit'
    CURSOR = 'cursor'
    RESULT = 'result'
    DESC = 'DESC'
    ASC = 'ASC'
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
    DATETIME_FORMAT_FOR_QUERIED_TRANSFERS = '%Y-%m-%dT%H:%M:%S.%fZ'
    GRAPH = 'graph'

    # Wallet stats
    NFTS = 'nfts'
    NFT_COUNT = 'nft_count'
    COLLECTIONS = 'collections'
    COLLECTION_COUNT = 'collection_count'
    TRANSACTIONS = 'transactions'
    TRANSACTION_COUNT = 'transaction_count'
    NFT_TRANSFERS = 'nft_transfers'
    NFT_TRANSFER_COUNT = 'nft_transfer_count'
    TOKEN_TRANSFERS = 'token_transfers'
    TOKEN_TRANSFER_COUNT = 'token_transfer_count'
    TOTAL = 'total'

    # Transaction
    HASH = 'hash'
    NONCE = 'nonce'
    TRANSACTION_INDEX = 'transaction_index'
    FROM_ADDRESS = 'from_address'
    FROM_ADDRESS_LABEL = 'from_address_label'
    TO_ADDRESS = 'to_address'
    TO_ADDRESS_LABEL = 'to_address_label'
    VALUE = 'value'
    GAS = 'gas'
    GAS_PRICE = 'gas_price'
    INPUT = 'input'
    REPCEIPT_CUMULATIVE_GAS_USED = 'receipt_cumulative_gas_used'
    REPCEIPT_GAS_USED = 'receipt_gas_used'
    REPCEIPT_CONTRACT_ADDRESS = 'receipt_contract_address'
    RECEIPT_ROOT = 'receipt_root'
    RECEIPT_STATUS = 'receipt_status'
    BLOCK_TIMESTAMP = 'block_timestamp'
    BLOCK_NUMBER = 'block_number'
    BLOCK_HASH = 'block_hash'
    TRANSFER_INDEX = 'transfer_index'
    TRANSACTION_FEE = 'transaction_fee'

    # Token transfer
    TOKEN_NAME = 'token_name'
    TOKEN_SYMBOL = 'token_symbol'
    TOKEN_LOGO = 'token_logo'
    TOKEN_DECIMALS = 'token_decimals'
    BLOCK_HASH = 'block_hash'
    TRANSACTION_HASH = 'transaction_hash'
    LOG_INDEX = 'log_index'
    POSSIBLE_SPAM = 'possible_spam'
    VALUE_DECIMAL = 'value_decimal'
    VERIFIED_CONTRACT = 'verified_contract'
    ASC = 'ASC'
    DESC = 'DESC'
    
    # Graph Record
    USER_ID = 'user_id'
    TIME_STAMP = 'time_stamp'
    GRAPH_PATH = 'graph_path'
    
    # Address Record
    BALANCE = 'balance'
    TOTAL_TRANSACTION_COUNT = 'total_transaction_count'
    INCOMING_TRANSACTION_COUNT = 'incoming_transaction_count'
    OUTGOING_TRANSACTION_COUNT = 'outgoing_transaction_count'
    FIRST_INCOMING_TRANSACTION_DATE = 'first_incoming_transaction_date'
    FIRST_INCOMING_TRANSACTION_SOURCE = 'first_incoming_transaction_source'
    LAST_OUTGOING_TRANSACTION_DATE = 'last_outgoing_transaction_date'
    LAST_OUTGOING_TRANSACTION_DESTINATION = 'last_outgoing_transaction_destination'
    CONTRACT_ADDRESS = 'contract_address'
    LAST_CURSOR = 'last_cursor'
    
    # Azure Database
    ODBC_CONNECTION_STRING = 'odbc_connection_string'

    # DynamoDB
    ITEM = 'Item'
    TABLE_NAME = 'TableName'
    AIRDROPS = 'airdrops'
    DEGEN = 'degen'
    STATS = 'stats'
    STATS_TABLE = 'stats_table'
    TRANSACTIONS_TABLE = 'transactions_table'

    # Airdrop tables
    AIRDROPS_DATABASE_PATH = 'airdrops_database_path'
    GRAPH_HTMLS_FOLDER_PATH = 'graph_htmls_folder_path'
    
    #Graph JSON Properties
    NODES = 'nodes'
    LINKS = 'links'
    PARAMETERS = 'parameters'