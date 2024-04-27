from eth_account import Account
from eth_account.messages import encode_defunct, SignableMessage, encode_structured_data
from web3 import Web3


class Web3Utils:
    def __init__(self, http_provider: str = 'https://eth.llamarpc.com', mnemonic: str = None, key: str = None):
        self.w3 = None
        Account.enable_unaudited_hdwallet_features()
        if mnemonic:
            self.mnemonic = mnemonic
            self.acct = Account.from_mnemonic(mnemonic)
        elif key:
            self.mnemonic = ""
            self.acct = Account.from_key(key)

        self.new_provider(http_provider)

    def new_provider(self, http_provider: str):
        self.w3 = Web3(Web3.HTTPProvider(http_provider))

    def create_wallet(self):
        self.acct, self.mnemonic = Account.create_with_mnemonic()
        return self.acct, self.mnemonic

    def sign(self, encoded_msg: SignableMessage):
        return self.w3.eth.account.sign_message(encoded_msg, self.acct.key)

    def get_signed_code(self, msg) -> str:
        return self.sign(encode_defunct(text=msg)).signature.hex()

    def get_signed_code_struct(self, msg) -> str:
        return self.sign(encode_structured_data(msg)).signature.hex()

    def wait_transaction(self, transaction_hash, timeout=120):
        return self.w3.eth.wait_for_transaction_receipt(transaction_hash, timeout=timeout)

    def balance_of_erc20(self, address, contract_address):
        abi = '[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]'

        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(contract_address), abi=abi)
        return contract.functions.balanceOf(address).call()

    def balance_of_erc721(self, address, contract_address):
        abi = '[{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"balance","type":"uint256"}],"stateMutability":"view","type":"function"}]'

        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(contract_address), abi=abi)
        return contract.functions.balanceOf(address).call()

    def allowance(self, spender: str, contract: str, abi: str):
        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(contract), abi=abi)
        return self.w3.from_wei(contract.functions.allowance(self.w3.to_checksum_address(self.acct.address), self.w3.to_checksum_address(spender)).call(), 'ether')
