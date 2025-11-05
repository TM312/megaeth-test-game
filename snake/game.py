"""
Core Snake game logic and state management
"""

from typing import List, Tuple, Optional

from .constants import GRID_WIDTH, GRID_HEIGHT, DIRECTION_UP
from .food_manager import FoodManager
from .game_renderer import GameRenderer
from .input_handler import InputHandler


class SnakeGame:
    """Core game logic and state management"""

    def __init__(
        self,
        width: int = GRID_WIDTH,
        height: int = GRID_HEIGHT,
        blockchain_client=None,
    ):
        self.width = width
        self.height = height

        # Initialize game components
        self.food_manager = FoodManager(width, height)
        self.input_handler = InputHandler(blockchain_client)
        self.renderer = GameRenderer(width, height)

        # Initialize game state
        self.snake: List[Tuple[int, int]] = [(width // 2, height // 2)]
        self.direction = DIRECTION_UP
        self.food: Tuple[int, int] = self.food_manager.generate_food(self.snake)
        self.score = 0
        self.game_over = False
        self.blockchain_enabled = blockchain_client is not None

    def update(self):
        """Update game state for one frame"""
        if self.game_over:
            return

        self._move_snake()

    def _move_snake(self):
        """Move the snake and handle collisions"""
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Check collisions
        if self._check_wall_collision(new_head) or self._check_self_collision(new_head):
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        # Handle food consumption
        if new_head == self.food:
            self.score += 1
            self.food = self.food_manager.generate_food(self.snake)
        else:
            self.snake.pop()

    def _check_wall_collision(self, position: Tuple[int, int]) -> bool:
        """Check if position collides with walls"""
        x, y = position
        return x < 0 or x >= self.width or y < 0 or y >= self.height

    def _check_self_collision(self, position: Tuple[int, int]) -> bool:
        """Check if position collides with snake body"""
        return position in self.snake

    def process_input(self, key: int) -> bool:
        """
        Process user input and return True if direction changed.
        Returns False for invalid input or blocked direction changes.
        """
        new_direction = self.input_handler.process_input(key, self.direction)
        if new_direction is not None:
            self.direction = new_direction
            return True
        return False

    def draw(self, stdscr):
        """Render the game using the renderer component"""
        self.renderer.draw_game(stdscr, self)

    def reset(self):
        """Reset game state for restart"""
        self.snake = [(self.width // 2, self.height // 2)]
        self.direction = DIRECTION_UP
        self.food = self.food_manager.generate_food(self.snake)
        self.score = 0
        self.game_over = False
