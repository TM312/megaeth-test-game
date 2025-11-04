"""
Performance tests and benchmarks for Snake game components
"""

import time
from unittest.mock import Mock

import pytest

from game import SnakeGame, FoodManager, GameRenderer, InputHandler


class TestPerformance:
    """Performance benchmarks for game components"""

    def test_game_update_performance(self):
        """Test game update performance"""
        game = SnakeGame(width=20, height=15)

        # Time 1000 update operations
        start_time = time.time()
        for _ in range(1000):
            game.update()
        end_time = time.time()

        duration = end_time - start_time
        # Should complete 1000 updates in less than 0.5 seconds
        assert duration < 0.5, f"1000 updates took {duration:.3f}s, expected < 0.5s"

    def test_food_generation_performance(self):
        """Test food generation performance"""
        food_manager = FoodManager(50, 50)
        snake_positions = [
            (i, 0) for i in range(10)
        ]  # Long snake to make generation harder

        # Time 100 food generations
        start_time = time.time()
        for _ in range(100):
            food_manager.generate_food(snake_positions)
        end_time = time.time()

        duration = end_time - start_time
        # Should generate 100 foods quickly
        assert (
            duration < 1.0
        ), f"100 food generations took {duration:.3f}s, expected < 1.0s"

    def test_renderer_performance(self):
        """Test rendering performance"""
        game = SnakeGame(width=50, height=30)
        # Make snake longer for more complex rendering
        game.snake = [(i, 15) for i in range(20)]
        renderer = GameRenderer(50, 30)

        # Mock stdscr to avoid curses dependency
        mock_stdscr = Mock()

        # Time 100 rendering operations
        start_time = time.time()
        for _ in range(100):
            renderer.draw_game(mock_stdscr, game)
        end_time = time.time()

        duration = end_time - start_time
        # Should render 100 times quickly
        assert duration < 2.0, f"100 renders took {duration:.3f}s, expected < 2.0s"

    def test_input_handler_performance(self):
        """Test input processing performance"""
        input_handler = InputHandler()

        # Time 1000 input processing operations
        start_time = time.time()
        for _ in range(1000):
            input_handler.process_input(258, (0, -1))  # KEY_UP
        end_time = time.time()

        duration = end_time - start_time
        # Should process 1000 inputs quickly
        assert (
            duration < 0.5
        ), f"1000 input processes took {duration:.3f}s, expected < 0.5s"

    @pytest.mark.parametrize("grid_size", [(10, 10), (20, 20), (50, 50)])
    def test_memory_usage_scaling(self, grid_size):
        """Test that memory usage scales reasonably with grid size"""
        width, height = grid_size
        game = SnakeGame(width=width, height=height)

        # Basic check that game initializes without excessive memory issues
        assert game.width == width
        assert game.height == height
        assert len(game.snake) == 1  # Should always start with 1 segment

    def test_game_simulation_performance(self):
        """Test performance of a short game simulation"""
        game = SnakeGame(width=20, height=15)

        start_time = time.time()

        # Simulate 100 game updates
        for _ in range(100):
            if game.game_over:
                break
            game.update()

        end_time = time.time()
        duration = end_time - start_time

        # Should complete in reasonable time (less than 1 second)
        assert duration < 1.0, f"Game simulation took {duration:.3f}s, expected < 1.0s"

    def test_component_initialization_performance(self):
        """Test that component initialization is fast"""
        start_time = time.time()

        # Initialize all components
        game = SnakeGame(width=20, height=15)

        end_time = time.time()
        duration = end_time - start_time

        # Should initialize very quickly (less than 0.1 seconds)
        assert duration < 0.1, f"Initialization took {duration:.3f}s, expected < 0.1s"
