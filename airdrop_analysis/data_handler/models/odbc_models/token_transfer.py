from utils.custom_keys import CustomKeys as ck

class Token_Transfer:
    def __init__(self, from_address, to_address, value, block_timestamp, block_hash, transaction_hash, token_name, contract_address, chain):
        self.from_address = from_address
        self.to_address = to_address
        self.value = value
        self.block_timestamp = block_timestamp
        self.block_hash = block_hash
        self.transaction_hash = transaction_hash
        self.token_name = token_name
        self.contract_address = contract_address
        self.chain = chain

    @staticmethod
    def create_from_dict(chain: str, response: dict):
        return Token_Transfer(
            from_address=response[ck.FROM_ADDRESS],
            to_address=response[ck.TO_ADDRESS],
            value=float(response[ck.VALUE]) / 10**18,
            block_timestamp=response[ck.BLOCK_TIMESTAMP],
            block_hash=response[ck.BLOCK_HASH],
            transaction_hash=response[ck.TRANSACTION_HASH],
            token_name=response[ck.TOKEN_NAME],
            contract_address=response[ck.ADDRESS],
            chain=chain,
        )