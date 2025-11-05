"""
Integration tests for Snake game components
"""

import pytest
from unittest.mock import Mock, patch
import curses
from snake.game import SnakeGame

# Lazy import for blockchain client
try:
    from blockchain import BlockchainClient

    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    BlockchainClient = None


class TestIntegration:
    """Integration tests for component interactions"""

    @pytest.mark.skipif(
        not BLOCKCHAIN_AVAILABLE, reason="Blockchain dependencies not available"
    )
    @patch.dict("os.environ", {"PRIVATE_KEY": "test_key"}, clear=True)
    @patch("blockchain.Web3")
    def test_game_with_blockchain_integration(
        self, mock_web3_class, mock_blockchain_client
    ):
        """Test full game lifecycle with blockchain integration"""
        # Setup mock blockchain
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = True
        mock_account = Mock()
        mock_account.address = "0x123"
        mock_w3.eth.account.from_key.return_value = mock_account
        mock_web3_class.HTTPProvider.return_value = Mock()
        mock_web3_class.return_value = mock_w3

        # Create game with blockchain
        game = SnakeGame(
            width=5, height=5, blockchain_client=BlockchainClient(auto_connect=False)
        )

        # Verify blockchain is enabled
        assert game.blockchain_enabled is True

        # Test direction change triggers blockchain transaction
        with patch("threading.Thread") as mock_thread:
            game.process_input(curses.KEY_UP)

            # Verify thread was created for async transaction
            mock_thread.assert_called_once()
            thread_kwargs = mock_thread.call_args[1]

            # Execute the transaction function
            thread_kwargs["target"]()

            # Verify blockchain transaction was attempted
            # Note: In real scenario, this would call the actual blockchain client

    def test_game_state_transitions(self):
        """Test game state transitions through a complete game"""
        game = SnakeGame(width=5, height=5)

        # Initial state
        assert not game.game_over
        assert game.score == 0
        assert len(game.snake) == 1

        # Move snake until wall collision
        game.direction = (-1, 0)  # Move left toward wall
        game.update()
        game.update()
        game.update()  # Hit left wall

        assert game.game_over

    def test_food_eating_mechanics(self):
        """Test the complete food eating cycle"""
        game = SnakeGame(width=5, height=5)

        # Position food next to snake
        game.food = (game.snake[0][0] + 1, game.snake[0][1])
        game.direction = (1, 0)  # Move toward food

        initial_length = len(game.snake)
        initial_score = game.score

        game.update()

        # Snake should grow and score should increase
        assert len(game.snake) == initial_length + 1
        assert game.score == initial_score + 1

        # Food should be regenerated (different position)
        assert game.food != (game.snake[0][0] + 1, game.snake[0][1])

    @patch("threading.Thread")
    def test_blockchain_transaction_flow(self, mock_thread, mock_blockchain_client):
        """Test the complete blockchain transaction flow"""
        game = SnakeGame(blockchain_client=mock_blockchain_client)

        # Change direction
        game.process_input(curses.KEY_RIGHT)

        # Verify thread was created
        assert mock_thread.called

        # Get the thread target function
        thread_kwargs = mock_thread.call_args[1]
        target_func = thread_kwargs["target"]

        # Execute the transaction
        target_func()

        # Verify blockchain client was called with correct parameters
        mock_blockchain_client.send_key_transaction.assert_called_once_with(
            curses.KEY_RIGHT, "right"
        )

    def test_game_restart_functionality(self):
        """Test game can be restarted after game over"""
        game = SnakeGame(width=5, height=5)

        # Cause game over
        game.direction = (-1, 0)
        for _ in range(3):  # Move left until wall
            game.update()

        assert game.game_over

        # Create new game (simulating restart)
        new_game = SnakeGame(width=5, height=5)

        # New game should be in initial state
        assert not new_game.game_over
        assert new_game.score == 0
        assert len(new_game.snake) == 1

    def test_edge_case_small_grid(self):
        """Test game behavior on very small grid"""
        game = SnakeGame(width=3, height=3)

        # Snake starts at center
        assert game.snake == [(1, 1)]

        # Move in any direction should eventually cause game over
        game.direction = (1, 0)  # Right
        game.update()  # Position (2, 1)
        assert not game.game_over

        game.update()  # Hit right wall
        assert game.game_over

    def test_direction_change_prevents_immediate_reverse(self):
        """Test that direction changes prevent immediate self-collision"""
        game = SnakeGame(width=5, height=5)
        game.snake = [(2, 2), (2, 3), (2, 4)]  # Snake moving up

        # Try to reverse direction (should be blocked)
        game.process_input(curses.KEY_DOWN)
        assert game.direction == (0, -1)  # Still moving up

        # Move should be safe
        game.update()
        assert not game.game_over
        assert game.snake[0] == (2, 1)  # Moved up safely

    @pytest.mark.skipif(
        not BLOCKCHAIN_AVAILABLE, reason="Blockchain dependencies not available"
    )
    @patch("blockchain.Web3")
    def test_blockchain_connection_failure_graceful_degradation(self, mock_web3_class):
        """Test game works when blockchain connection fails"""
        # Mock failed connection
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = False
        mock_web3_class.HTTPProvider.return_value = Mock()
        mock_web3_class.return_value = mock_w3

        # Create game - blockchain is enabled even with failed connection
        game = SnakeGame(blockchain_client=BlockchainClient(auto_connect=False))

        # Game should still work - blockchain is enabled but transactions may fail
        assert game.blockchain_enabled is True

        # Direction changes should work (transactions may fail but don't break game)
        game.process_input(curses.KEY_UP)
        assert game.direction == (0, -1)
