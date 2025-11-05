"""
Test configuration and fixtures
"""

import pytest
from unittest.mock import Mock
from snake.game import SnakeGame  # noqa: F401

# Lazy import for blockchain client to handle missing dependencies
try:
    from blockchain import BlockchainClient

    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    BlockchainClient = None


# region Blockchain Fixtures


@pytest.fixture
def mock_blockchain_client():
    """Mock blockchain client for testing - connected and functional"""
    if not BLOCKCHAIN_AVAILABLE:
        pytest.skip("Blockchain dependencies not available")
    client = Mock(spec=BlockchainClient)
    client.is_connected.return_value = True
    client.send_key_transaction.return_value = (True, b"mock_tx_hash")
    return client


@pytest.fixture
def mock_blockchain_client_disconnected():
    """Mock blockchain client - disconnected"""
    if not BLOCKCHAIN_AVAILABLE:
        pytest.skip("Blockchain dependencies not available")
    client = Mock(spec=BlockchainClient)
    client.is_connected.return_value = False
    client.send_key_transaction.return_value = (False, None)
    return client


@pytest.fixture
def mock_blockchain_client_failing():
    """Mock blockchain client - connected but transaction sending fails"""
    if not BLOCKCHAIN_AVAILABLE:
        pytest.skip("Blockchain dependencies not available")
    client = Mock(spec=BlockchainClient)
    client.is_connected.return_value = True
    client.send_key_transaction.return_value = (False, None)
    return client


# endregion

# region Game Fixtures


@pytest.fixture
def snake_game():
    """Basic snake game instance with default settings"""
    return SnakeGame(width=10, height=8)


@pytest.fixture
def snake_game_small():
    """Small snake game instance for testing edge cases"""
    return SnakeGame(width=5, height=5)


@pytest.fixture
def snake_game_with_blockchain(mock_blockchain_client):
    """Snake game with connected blockchain client"""
    return SnakeGame(width=10, height=8, blockchain_client=mock_blockchain_client)


@pytest.fixture
def snake_game_blockchain_disabled(mock_blockchain_client_disconnected):
    """Snake game with disconnected blockchain client"""
    return SnakeGame(
        width=10, height=8, blockchain_client=mock_blockchain_client_disconnected
    )


# endregion

# region Game State Fixtures


@pytest.fixture
def snake_game_at_wall():
    """Snake game with snake positioned at left wall"""
    game = SnakeGame(width=5, height=5)
    game.snake = [(0, 2)]  # At left edge
    game.direction = (-1, 0)  # Moving left
    return game


@pytest.fixture
def snake_game_with_food():
    """Snake game with food positioned for easy consumption"""
    game = SnakeGame(width=5, height=5)
    game.snake = [(2, 2)]
    game.food = (2, 1)  # Food directly above snake
    game.direction = (0, -1)  # Moving toward food
    return game


# endregion
