"""
Tests for SnakeGame
"""

import curses
from unittest.mock import Mock, patch

from snake.game import SnakeGame
from snake.game_renderer import GameRenderer


# Test constants
DEFAULT_WIDTH = 20
DEFAULT_HEIGHT = 15
SMALL_WIDTH = 5
SMALL_HEIGHT = 5
CENTER_X = SMALL_WIDTH // 2
CENTER_Y = SMALL_HEIGHT // 2


class TestSnakeGame:
    """Test suite for SnakeGame"""

    # region Initialization Tests

    def test_init_default_values(self):
        """Test game initialization with default values"""
        game = SnakeGame()

        assert game.width == DEFAULT_WIDTH
        assert game.height == DEFAULT_HEIGHT
        assert game.snake == [(DEFAULT_WIDTH // 2, DEFAULT_HEIGHT // 2)]
        assert game.direction == (0, -1)  # Moving up
        assert game.score == 0
        assert game.game_over is False
        assert game.blockchain_enabled is False

    def test_init_custom_values(self):
        """Test game initialization with custom values"""
        mock_client = Mock()
        game = SnakeGame(width=10, height=8, blockchain_client=mock_client)

        assert game.width == 10
        assert game.height == 8
        assert game.snake == [(5, 4)]  # Center of 10x8 grid
        assert game.blockchain_enabled is True

    def test_init_blockchain_enabled(self):
        """Test blockchain enabled when client is connected"""
        mock_client = Mock()
        mock_client.is_connected.return_value = True

        game = SnakeGame(blockchain_client=mock_client)

        assert game.blockchain_enabled is True

    def test_init_blockchain_enabled_with_client(self):
        """Test blockchain enabled when any client is provided"""
        mock_client = Mock()
        mock_client.is_connected.return_value = False

        game = SnakeGame(blockchain_client=mock_client)

        # With the new architecture, blockchain is enabled if any client is provided
        # The client's connection status is checked at runtime, not during initialization
        assert game.blockchain_enabled is True

    # endregion

    # region Food Generation Tests

    def test_generate_food_creates_valid_position(self):
        """Test food generation creates position within bounds and not on snake"""
        game = SnakeGame(width=SMALL_WIDTH, height=SMALL_HEIGHT)
        game.snake = [(0, 0), (1, 0)]  # Snake occupies some positions

        food = game.food_manager.generate_food(game.snake)

        # Food should not be on snake
        assert food not in game.snake
        # Food should be within bounds
        assert 0 <= food[0] < game.width
        assert 0 <= food[1] < game.height

    @patch("random.randint")
    def test_generate_food_avoids_snake_positions(self, mock_randint):
        """Test food generation avoids all snake positions"""
        game = SnakeGame(width=3, height=3)
        game.snake = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)]  # Most positions occupied

        # Mock random to return snake positions first, then valid position
        mock_randint.side_effect = [0, 0, 1, 0, 2, 1]  # snake positions, then valid

        food = game.food_manager.generate_food(game.snake)

        assert food == (2, 1)
        assert food not in game.snake

    # endregion

    # region Movement Tests

    def test_update_normal_movement(self):
        """Test normal snake movement in current direction"""
        game = SnakeGame(width=SMALL_WIDTH, height=SMALL_HEIGHT)
        game.snake = [
            (CENTER_X, CENTER_Y),
            (CENTER_X, CENTER_Y + 1),
        ]  # Snake at center, moving up
        game.direction = (0, -1)
        # Set food to a position that won't be eaten
        game.food = (0, 0)

        game.update()

        assert game.snake == [
            (CENTER_X, CENTER_Y - 1),
            (CENTER_X, CENTER_Y),
        ]  # Moved up
        assert game.game_over is False

    def test_update_wall_collision_left(self):
        """Test wall collision on left edge"""
        game = SnakeGame(width=SMALL_WIDTH, height=SMALL_HEIGHT)
        game.snake = [(0, CENTER_Y)]  # At left edge
        game.direction = (-1, 0)  # Moving left

        game.update()

        assert game.game_over is True

    def test_update_wall_collision_right(self):
        """Test wall collision on right edge"""
        game = SnakeGame(width=SMALL_WIDTH, height=SMALL_HEIGHT)
        game.snake = [(SMALL_WIDTH - 1, CENTER_Y)]  # At right edge
        game.direction = (1, 0)  # Moving right

        game.update()

        assert game.game_over is True

    def test_update_wall_collision_top(self):
        """Test wall collision on top edge"""
        game = SnakeGame(width=SMALL_WIDTH, height=SMALL_HEIGHT)
        game.snake = [(CENTER_X, 0)]  # At top edge
        game.direction = (0, -1)  # Moving up

        game.update()

        assert game.game_over is True

    def test_update_wall_collision_bottom(self):
        """Test wall collision on bottom edge"""
        game = SnakeGame(width=SMALL_WIDTH, height=SMALL_HEIGHT)
        game.snake = [(CENTER_X, SMALL_HEIGHT - 1)]  # At bottom edge
        game.direction = (0, 1)  # Moving down

        game.update()

        assert game.game_over is True

    def test_update_self_collision(self):
        """Test self collision"""
        game = SnakeGame(width=SMALL_WIDTH, height=SMALL_HEIGHT)
        game.snake = [
            (CENTER_X, CENTER_Y),
            (CENTER_X, CENTER_Y + 1),
            (CENTER_X + 1, CENTER_Y + 1),
            (CENTER_X + 1, CENTER_Y),
        ]  # Snake in a loop
        game.direction = (0, 1)  # Moving into self

        game.update()

        assert game.game_over is True

    def test_update_eat_food_increases_score_and_length(self):
        """Test eating food increases score and snake length"""
        game = SnakeGame(width=SMALL_WIDTH, height=SMALL_HEIGHT)
        game.snake = [(CENTER_X, CENTER_Y)]
        game.food = (CENTER_X, CENTER_Y - 1)  # Food directly above
        game.direction = (0, -1)  # Moving up to food
        initial_score = game.score

        game.update()

        assert game.snake == [
            (CENTER_X, CENTER_Y - 1),
            (CENTER_X, CENTER_Y),
        ]  # Snake grew
        assert game.score == initial_score + 1
        assert game.food != (CENTER_X, CENTER_Y - 1)  # Food was consumed

    # endregion

    # region Direction Change Tests

    def test_process_input_up(self):
        """Test changing direction to up"""
        game = SnakeGame()
        game.direction = (1, 0)  # Currently moving right

        assert game.process_input(curses.KEY_UP) is True

        assert game.direction == (0, -1)

    def test_process_input_down(self):
        """Test changing direction to down"""
        game = SnakeGame()
        game.direction = (1, 0)  # Currently moving right

        assert game.process_input(curses.KEY_DOWN) is True

        assert game.direction == (0, 1)

    def test_process_input_left(self):
        """Test changing direction to left"""
        game = SnakeGame()
        game.direction = (0, 1)  # Currently moving down

        assert game.process_input(curses.KEY_LEFT) is True

        assert game.direction == (-1, 0)

    def test_process_input_right(self):
        """Test changing direction to right"""
        game = SnakeGame()
        game.direction = (0, 1)  # Currently moving down

        assert game.process_input(curses.KEY_RIGHT) is True

        assert game.direction == (1, 0)

    def test_process_input_reverse_blocked(self):
        """Test that reverse direction changes are blocked"""
        game = SnakeGame()
        game.direction = (0, -1)  # Moving up

        # Try to go down (reverse) - should be blocked
        assert game.process_input(curses.KEY_DOWN) is False

        assert game.direction == (0, -1)  # Direction unchanged

    def test_process_input_invalid_key(self):
        """Test invalid key doesn't change direction"""
        game = SnakeGame()
        original_direction = game.direction

        result = game.process_input(999)  # Invalid key

        assert result is False
        assert game.direction == original_direction

    @patch("threading.Thread")
    def test_process_input_with_blockchain_sends_transaction(self, mock_thread):
        """Test blockchain transaction on direction change"""
        mock_client = Mock()
        mock_client.is_connected.return_value = True

        game = SnakeGame(blockchain_client=mock_client)
        # Change from default direction (up) to left - valid direction change
        assert game.process_input(curses.KEY_LEFT) is True

        mock_thread.assert_called_once()
        # Verify the thread target calls the blockchain method
        call_kwargs = mock_thread.call_args[1]
        call_kwargs["target"]()  # Execute the target function
        mock_client.send_key_transaction.assert_called_once_with(
            curses.KEY_LEFT, "left"
        )

    def test_process_input_no_blockchain(self):
        """Test direction change without blockchain client"""
        game = SnakeGame()

        assert game.process_input(curses.KEY_UP) is True

        assert game.direction == (0, -1)

    def test_process_input_blockchain_enabled_attempts_transaction(self):
        """Test that blockchain transactions are attempted when enabled, regardless of connection status"""
        mock_client = Mock()
        mock_client.is_connected.return_value = False  # Client reports as disconnected

        game = SnakeGame(blockchain_client=mock_client)

        # Direction change should still work and attempt blockchain transaction
        assert game.process_input(curses.KEY_LEFT) is True
        assert game.direction == (-1, 0)

        # Transaction should still be attempted (connection status is checked by BlockchainClient)
        mock_client.send_key_transaction.assert_called_once_with(
            curses.KEY_LEFT, "left"
        )

    # endregion


# ============================================================================
# Comprehensive Edge Case Tests
# ============================================================================


class TestComprehensiveEdgeCases:
    """Comprehensive edge case tests covering various scenarios"""

    def test_game_initialization_various_sizes(self):
        """Test that game initializes correctly for various grid sizes"""
        test_cases = [
            (5, 5, (2, 2)),  # 5x5 grid, center at (2,2)
            (10, 8, (5, 4)),  # 10x8 grid, center at (5,4)
            (21, 13, (10, 6)),  # Odd dimensions
            (50, 30, (25, 15)),  # Large grid
        ]

        for width, height, expected_center in test_cases:
            game = SnakeGame(width=width, height=height)

            # Snake should start at center
            assert game.snake[0] == expected_center

            # Game should not be over initially
            assert not game.game_over

            # Dimensions should be set correctly
            assert game.width == width
            assert game.height == height

    def test_food_generation_comprehensive(self):
        """Test food generation in various scenarios"""
        # Test with almost full snake
        game = SnakeGame(width=5, height=5)
        # Place snake in most positions, leaving only corners
        game.snake = [
            (1, 1),
            (1, 2),
            (1, 3),
            (2, 1),
            (2, 2),
            (2, 3),
            (3, 1),
            (3, 2),
            (3, 3),
        ]

        food = game.food_manager.generate_food(game.snake)

        # Food should NOT be on the snake
        assert food not in game.snake
        # Food should be within grid bounds
        assert 0 <= food[0] < 5
        assert 0 <= food[1] < 5

        # Test food generation with empty snake (should still work)
        game2 = SnakeGame(width=3, height=3)
        game2.snake = []
        food2 = game2.food_manager.generate_food(game2.snake)
        assert 0 <= food2[0] < 3
        assert 0 <= food2[1] < 3

    def test_collision_detection_wall_comprehensive(self):
        """Test wall collision detection comprehensively"""
        game = SnakeGame(width=10, height=8)

        # Test wall collisions - only out-of-bounds positions
        wall_positions = [
            (-1, 4),  # Left wall
            (10, 4),  # Right wall
            (5, -1),  # Top wall
            (5, 8),  # Bottom wall
        ]

        for pos in wall_positions:
            assert game._check_wall_collision(
                pos
            ), f"Position {pos} should be wall collision"

        # Test valid positions (inside bounds)
        valid_positions = [(0, 0), (9, 7), (1, 1), (5, 4), (8, 6)]
        for pos in valid_positions:
            assert not game._check_wall_collision(
                pos
            ), f"Position {pos} should not be wall collision"

    def test_self_collision_scenarios(self):
        """Test various self collision scenarios"""
        game = SnakeGame(width=10, height=10)

        # Test single segment - it exists in snake list
        game.snake = [(5, 5)]
        assert game._check_self_collision((5, 5))  # Head IS in snake

        # Test collision with body segments
        game.snake = [(5, 5), (5, 6), (5, 7), (6, 7), (7, 7)]
        # These positions are in the snake, so should collide
        assert game._check_self_collision((5, 5))  # Head
        assert game._check_self_collision((5, 6))  # Body segment
        assert game._check_self_collision((5, 7))  # Body segment
        assert game._check_self_collision((6, 7))  # Body segment
        # This position is not in snake
        assert not game._check_self_collision((4, 5))

        # Test collision with various body configurations
        test_snakes = [
            [(0, 0), (1, 0), (1, 1)],  # L-shape
            [(2, 2), (2, 3), (3, 3), (3, 2)],  # Square
            [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)],  # Straight line
        ]

        for snake_config in test_snakes:
            game.snake = snake_config
            head = snake_config[0]
            body = snake_config[1:]

            # All snake segments should be detected as collisions
            for segment in snake_config:
                assert game._check_self_collision(
                    segment
                ), f"Segment {segment} should collide"

            # Random positions should not collide
            assert not game._check_self_collision((-1, -1))
            assert not game._check_self_collision((99, 99))


# ============================================================================
# Renderer Tests
# ============================================================================


class MockStdscr:
    """Mock curses window for testing"""

    def __init__(self, max_y=24, max_x=80):
        self.max_y = max_y
        self.max_x = max_x
        self.chars_added = []
        self.strs_added = []
        self.cleared = False
        self.refreshed = False

    def clear(self):
        self.cleared = True

    def addch(self, y, x, ch, *args):
        """Will raise error if out of bounds like real curses"""
        if y < 0 or y >= self.max_y or x < 0 or x >= self.max_x:
            raise curses.error("addch() out of bounds")
        self.chars_added.append((y, x, ch))

    def addstr(self, y, x, s, *args):
        """Will raise error if out of bounds like real curses"""
        if y < 0 or y >= self.max_y or x < 0 or x >= self.max_x:
            raise curses.error("addstr() out of bounds")
        self.strs_added.append((y, x, s))

    def refresh(self):
        self.refreshed = True

    def getmaxyx(self):
        return (self.max_y, self.max_x)


class TestGameRenderer:
    """Test suite for GameRenderer"""

    def test_renderer_initialization(self):
        """Test renderer initializes with correct dimensions"""

        renderer = GameRenderer(width=20, height=15)

        assert renderer.width == 20
        assert renderer.height == 15

    def test_safe_addch_within_bounds(self):
        """Test _safe_addch succeeds when within bounds"""

        renderer = GameRenderer(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=25, max_x=80)

        result = renderer._safe_addch(mock_stdscr, 5, 10, "X")

        assert result is True
        assert (5, 10, "X") in mock_stdscr.chars_added

    def test_safe_addch_out_of_bounds(self):
        """Test _safe_addch fails gracefully when out of bounds"""

        renderer = GameRenderer(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=25, max_x=80)

        result = renderer._safe_addch(mock_stdscr, 30, 10, "X")

        assert result is False
        assert len(mock_stdscr.chars_added) == 0

    def test_safe_addch_negative_coordinates(self):
        """Test _safe_addch fails gracefully with negative coordinates"""

        renderer = GameRenderer(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=25, max_x=80)

        result = renderer._safe_addch(mock_stdscr, -1, 10, "X")

        assert result is False
        assert len(mock_stdscr.chars_added) == 0

    def test_safe_addstr_within_bounds(self):
        """Test _safe_addstr succeeds when within bounds"""

        renderer = GameRenderer(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=25, max_x=80)

        result = renderer._safe_addstr(mock_stdscr, 2, 10, "Score: 42")

        assert result is True
        assert (2, 10, "Score: 42") in mock_stdscr.strs_added

    def test_safe_addstr_out_of_bounds(self):
        """Test _safe_addstr fails gracefully when out of bounds"""

        renderer = GameRenderer(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=25, max_x=80)

        result = renderer._safe_addstr(mock_stdscr, 30, 10, "Score: 42")

        assert result is False
        assert len(mock_stdscr.strs_added) == 0

    def test_safe_addstr_truncates_overflow(self):
        """Test _safe_addstr truncates text that would overflow"""

        renderer = GameRenderer(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=25, max_x=20)  # Only 20 columns

        # Text would overflow at position 15 with 20 char text
        result = renderer._safe_addstr(mock_stdscr, 0, 15, "This is very long text")

        assert result is True
        # Should truncate to fit in remaining space (20 - 15 - 1 = 4 chars)
        assert len(mock_stdscr.strs_added) == 1

    def test_draw_game_with_small_terminal(self):
        """Test game renders correctly with small terminal"""

        renderer = GameRenderer(width=20, height=15)
        game = SnakeGame(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=20, max_x=40)

        # Don't call init_colors for testing - use monochrome mode
        renderer.draw_game(mock_stdscr, game)

        assert mock_stdscr.cleared
        assert mock_stdscr.refreshed
        assert len(mock_stdscr.chars_added) > 0  # Borders and snake

    def test_draw_game_with_large_terminal(self):
        """Test game renders correctly with large terminal"""

        renderer = GameRenderer(width=20, height=15)
        game = SnakeGame(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=100, max_x=200)

        # Don't call init_colors for testing - use monochrome mode
        renderer.draw_game(mock_stdscr, game)

        assert mock_stdscr.cleared
        assert mock_stdscr.refreshed
        assert len(mock_stdscr.chars_added) > 0

    def test_draw_borders_clips_to_terminal_width(self):
        """Test borders are clipped to terminal width"""

        renderer = GameRenderer(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=25, max_x=15)  # Narrower than game

        renderer._draw_borders(mock_stdscr)

        # Should not attempt to draw outside bounds
        for y, x, ch in mock_stdscr.chars_added:
            assert 0 <= x < 15, f"Character at x={x} is out of bounds"
            assert 0 <= y < 25, f"Character at y={y} is out of bounds"

    def test_draw_borders_clips_to_terminal_height(self):
        """Test borders are clipped to terminal height"""

        renderer = GameRenderer(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=10, max_x=80)  # Shorter than game

        renderer._draw_borders(mock_stdscr)

        # Should not attempt to draw outside bounds
        for y, x, ch in mock_stdscr.chars_added:
            assert 0 <= y < 10, f"Character at y={y} is out of bounds"
            assert 0 <= x < 80, f"Character at x={x} is out of bounds"

    def test_draw_score_handles_small_terminal(self):
        """Test score display doesn't fail on small terminal"""

        renderer = GameRenderer(width=20, height=15)
        game = SnakeGame(width=20, height=15)
        game.score = 999
        mock_stdscr = MockStdscr(max_y=10, max_x=30)  # Limited space

        # Should not raise exception
        renderer._draw_score(mock_stdscr, game.score)

    def test_draw_blockchain_status_handles_small_terminal(self):
        """Test blockchain status display doesn't fail on small terminal"""

        renderer = GameRenderer(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=10, max_x=30)

        # Should not raise exception
        renderer._draw_blockchain_status(mock_stdscr, True)
        renderer._draw_blockchain_status(mock_stdscr, False)

    def test_draw_game_over_handles_small_terminal(self):
        """Test game over message doesn't fail on small terminal"""

        renderer = GameRenderer(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=10, max_x=30)

        # Should not raise exception
        renderer._draw_game_over(mock_stdscr, True, 15)

    def test_draw_game_handles_renderer_exception(self):
        """Test draw_game handles exceptions gracefully"""

        renderer = GameRenderer(width=20, height=15)
        game = SnakeGame(width=20, height=15)

        class FailingStdscr(MockStdscr):
            def clear(self):
                self.cleared = True

            def refresh(self):
                raise Exception("Refresh failed")

        mock_stdscr = FailingStdscr()

        # Should not raise exception even when refresh fails
        renderer.draw_game(mock_stdscr, game)

    def test_full_game_render_loop(self):
        """Test a complete game render loop with various game states"""

        renderer = GameRenderer(width=20, height=15)
        game = SnakeGame(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=25, max_x=80)

        # Render multiple frames
        for i in range(5):
            game.update()
            # Don't call init_colors for testing - use monochrome mode
            renderer.draw_game(mock_stdscr, game)

        assert mock_stdscr.cleared
        assert mock_stdscr.refreshed
        assert len(mock_stdscr.chars_added) > 0

    def test_snake_rendering_with_various_lengths(self):
        """Test rendering snakes of various lengths"""

        renderer = GameRenderer(width=20, height=15)
        mock_stdscr = MockStdscr(max_y=25, max_x=80)

        # Test with growing snake - keep within game bounds
        for length in [1, 5, 10]:
            game = SnakeGame(width=20, height=15)
            # Create snake of specific length, positioned safely in center
            game.snake = [(10 - i, 7) for i in range(length)]

            mock_stdscr.chars_added.clear()
            renderer._draw_snake(mock_stdscr, game.snake)

            # All snake segments within bounds should be drawn
            drawn_count = sum(
                1 for y, x, ch in mock_stdscr.chars_added if ch in ["█", "●"]
            )
            # At least some segments should be drawn
            assert drawn_count > 0, f"No snake segments drawn for length {length}"
            # All drawn segments should have valid coordinates
            for y, x, ch in mock_stdscr.chars_added:
                if ch in ["█", "●"]:
                    assert 0 <= x < 80
                    assert 0 <= y < 25
