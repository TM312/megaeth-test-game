"""
Blockchain client for MegaETH testnet integration
"""

from typing import Optional
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

try:
    from .config import Config
except ImportError:
    from config import Config


# Blockchain constants
DEFAULT_GAS_LIMIT = 21000


class BlockchainClient:
    """Client for interacting with MegaETH testnet"""

    def __init__(self):
        self.w3: Optional[Web3] = None
        self.account = None
        self.private_key = Config.PRIVATE_KEY
        self.rpc_url = Config.RPC_URL

        if self.private_key:
            self._connect()

    def _connect(self):
        """Connect to MegaETH testnet"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

            # Derive account from private key
            self.account = self.w3.eth.account.from_key(self.private_key)

            if not self.w3.is_connected():
                print("Warning: Could not connect to MegaETH testnet")
                self.w3 = None
            else:
                print(f"Connected to MegaETH testnet. Account: {self.account.address}")
        except Exception as e:
            print(f"Failed to connect to MegaETH testnet: {e}")
            self.w3 = None

    def send_key_transaction(self, key_code: int, direction: str = "") -> bool:
        """Send a transaction representing a key event"""
        if not self.w3 or not self.account:
            return False

        try:
            transaction = self._build_transaction(key_code, direction)
            signed_transaction = self._sign_transaction(transaction)
            tx_hash = self._send_transaction(signed_transaction)

            self._log_transaction(tx_hash)
            return True

        except Exception as e:
            self._handle_transaction_error(e)
            return False

    def _build_transaction(self, key_code: int, direction: str) -> dict:
        """Build transaction dictionary"""
        key_data = f"snake_key_{key_code}_{direction}".encode("utf-8")

        return {
            "from": self.account.address,
            "to": self.account.address,  # Send to self
            "value": 0,
            "gas": DEFAULT_GAS_LIMIT,
            "gasPrice": self.w3.eth.gas_price,
            "nonce": self.w3.eth.get_transaction_count(self.account.address),
            "data": key_data,
            "chainId": self.w3.eth.chain_id,
        }

    def _sign_transaction(self, transaction: dict):
        """Sign the transaction with private key"""
        return self.w3.eth.account.sign_transaction(transaction, self.private_key)

    def _send_transaction(self, signed_transaction):
        """Send the signed transaction to the network"""
        return self.w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    def _log_transaction(self, tx_hash):
        """Log transaction hash in debug mode"""
        if Config.DEBUG:
            print(f"Transaction sent: {tx_hash.hex()}")

    def _handle_transaction_error(self, error: Exception):
        """Handle transaction errors"""
        print(f"Transaction failed: {error}")

    def is_connected(self) -> bool:
        """Check if connected to testnet"""
        return self.w3 is not None and self.w3.is_connected()
