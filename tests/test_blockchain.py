"""
Tests for BlockchainClient
"""

import os
from unittest.mock import Mock, patch

import pytest

# Lazy import for blockchain client to handle missing dependencies
try:
    from blockchain import BlockchainClient
    from config import Config

    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    BlockchainClient = None
    Config = None


# Test constants
TEST_PRIVATE_KEY = "test_private_key_123"
TEST_ACCOUNT_ADDRESS = "0x123456789abcdef"
DEFAULT_GAS_PRICE = 20000000000
DEFAULT_GAS_LIMIT = 21000
DEFAULT_CHAIN_ID = 1


@pytest.mark.skipif(
    not BLOCKCHAIN_AVAILABLE, reason="Blockchain dependencies not available"
)
class TestBlockchainClient:
    """Test suite for BlockchainClient"""

    # region Initialization Tests

    @patch("config.load_dotenv")
    def test_init_with_private_key_calls_connect(self, mock_load_dotenv):
        """Test initialization with private key triggers connection attempt"""
        with patch.object(Config, "PRIVATE_KEY", TEST_PRIVATE_KEY):
            with patch.object(BlockchainClient, "_connect") as mock_connect:
                client = BlockchainClient()

                assert client.private_key == TEST_PRIVATE_KEY
                mock_connect.assert_called_once()

    @patch("config.load_dotenv")
    def test_init_without_private_key_skips_connect(self, mock_load_dotenv):
        """Test initialization without private key skips connection"""
        with patch.object(Config, "PRIVATE_KEY", None):
            with patch.object(BlockchainClient, "_connect") as mock_connect:
                client = BlockchainClient()

                assert client.private_key is None
                mock_connect.assert_not_called()

    # endregion

    # region Connection Tests

    @patch("blockchain.Web3")
    @patch("blockchain.ExtraDataToPOAMiddleware")
    def test_connect_success_sets_web3_and_account(
        self, mock_middleware, mock_web3_class
    ):
        """Test successful connection sets web3 and account instances"""
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = True
        mock_account = Mock()
        mock_account.address = TEST_ACCOUNT_ADDRESS
        mock_w3.eth.account.from_key.return_value = mock_account
        mock_web3_class.HTTPProvider.return_value = Mock()
        mock_web3_class.return_value = mock_w3

        client = BlockchainClient()
        client.private_key = TEST_PRIVATE_KEY
        client._connect()

        assert client.w3 == mock_w3
        assert client.account == mock_account

    @patch("blockchain.Web3")
    @patch("blockchain.ExtraDataToPOAMiddleware")
    def test_connect_success_injects_middleware(self, mock_middleware, mock_web3_class):
        """Test successful connection injects POA middleware"""
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = True
        mock_account = Mock()
        mock_w3.eth.account.from_key.return_value = mock_account
        mock_web3_class.HTTPProvider.return_value = Mock()
        mock_web3_class.return_value = mock_w3

        client = BlockchainClient()
        client.private_key = TEST_PRIVATE_KEY
        client._connect()

        mock_w3.middleware_onion.inject.assert_called_once_with(
            mock_middleware, layer=0
        )

    @patch("blockchain.Web3")
    @patch("blockchain.ExtraDataToPOAMiddleware")
    def test_connect_failure_sets_web3_to_none(self, mock_middleware, mock_web3_class):
        """Test connection failure sets web3 to None"""
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = False
        mock_web3_class.HTTPProvider.return_value = Mock()
        mock_web3_class.return_value = mock_w3

        client = BlockchainClient()
        client.private_key = TEST_PRIVATE_KEY
        client._connect()

        assert client.w3 is None

    # endregion

    # region Connection Status Tests

    def test_is_connected_returns_true_when_web3_connected(self):
        """Test is_connected returns True when web3 reports connection"""
        client = BlockchainClient()
        client.w3 = Mock()
        client.w3.is_connected.return_value = True

        result = client.is_connected()

        assert result is True

    def test_is_connected_returns_false_when_no_web3(self):
        """Test is_connected returns False when no web3 instance"""
        client = BlockchainClient()
        client.w3 = None

        result = client.is_connected()

        assert result is False

    def test_is_connected_returns_false_when_web3_not_connected(self):
        """Test is_connected returns False when web3 reports disconnection"""
        client = BlockchainClient()
        client.w3 = Mock()
        client.w3.is_connected.return_value = False

        result = client.is_connected()

        assert result is False

    # endregion

    def test_send_key_transaction_no_web3(self):
        """Test send_key_transaction returns False when no web3"""
        client = BlockchainClient()
        client.w3 = None

        result = client.send_key_transaction(65, "up")
        assert result is False

    def test_send_key_transaction_no_account(self):
        """Test send_key_transaction returns False when no account"""
        client = BlockchainClient()
        client.w3 = Mock()
        client.account = None

        result = client.send_key_transaction(65, "up")
        assert result is False

    @patch("blockchain.Web3")
    def test_send_key_transaction_success_returns_true(self, mock_web3_class):
        """Test successful transaction sending returns True"""
        mock_w3 = Mock()
        mock_account = Mock()
        mock_account.address = TEST_ACCOUNT_ADDRESS
        mock_w3.eth.account.from_key.return_value = mock_account
        mock_w3.eth.gas_price = DEFAULT_GAS_PRICE
        mock_w3.eth.get_transaction_count.return_value = 1
        mock_w3.eth.chain_id = DEFAULT_CHAIN_ID
        mock_w3.eth.account.sign_transaction.return_value = Mock(
            rawTransaction=b"signed_tx"
        )
        mock_web3_class.HTTPProvider.return_value = Mock()
        mock_web3_class.return_value = mock_w3

        client = BlockchainClient()
        client.w3 = mock_w3
        client.account = mock_account

        result = client.send_key_transaction(65, "up")

        assert result is True

    @patch("blockchain.Web3")
    def test_send_key_transaction_success_creates_correct_transaction(
        self, mock_web3_class
    ):
        """Test transaction is created with correct parameters"""
        mock_w3 = Mock()
        mock_account = Mock()
        mock_account.address = TEST_ACCOUNT_ADDRESS
        mock_w3.eth.account.from_key.return_value = mock_account
        mock_w3.eth.gas_price = DEFAULT_GAS_PRICE
        mock_w3.eth.get_transaction_count.return_value = 1
        mock_w3.eth.chain_id = DEFAULT_CHAIN_ID
        mock_w3.eth.account.sign_transaction.return_value = Mock(
            rawTransaction=b"signed_tx"
        )
        mock_web3_class.HTTPProvider.return_value = Mock()
        mock_web3_class.return_value = mock_w3

        client = BlockchainClient()
        client.w3 = mock_w3
        client.account = mock_account

        client.send_key_transaction(65, "up")

        # Verify transaction structure
        call_args = mock_w3.eth.account.sign_transaction.call_args[0][0]
        assert call_args["from"] == TEST_ACCOUNT_ADDRESS
        assert call_args["to"] == TEST_ACCOUNT_ADDRESS
        assert call_args["value"] == 0
        assert call_args["gas"] == DEFAULT_GAS_LIMIT
        expected_data = f"snake_key_65_up".encode("utf-8")
        assert expected_data in call_args["data"]

    @patch("blockchain.Web3")
    def test_send_key_transaction_failure_returns_false(self, mock_web3_class):
        """Test transaction sending failure returns False"""
        mock_w3 = Mock()
        mock_account = Mock()
        mock_account.address = TEST_ACCOUNT_ADDRESS
        mock_w3.eth.account.from_key.return_value = mock_account
        mock_w3.eth.gas_price = DEFAULT_GAS_PRICE
        mock_w3.eth.get_transaction_count.return_value = 1
        mock_w3.eth.chain_id = DEFAULT_CHAIN_ID
        mock_w3.eth.account.sign_transaction.side_effect = Exception(
            "Transaction failed"
        )
        mock_web3_class.HTTPProvider.return_value = Mock()
        mock_web3_class.return_value = mock_w3

        client = BlockchainClient()
        client.w3 = mock_w3
        client.account = mock_account

        result = client.send_key_transaction(65, "up")

        assert result is False

    # endregion
