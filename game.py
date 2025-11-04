"""
Snake game logic and components
"""

import curses
import random
import threading
from typing import List, Tuple, Optional, NamedTuple


# ============================================================================
# Data Structures
# ============================================================================


class Position(NamedTuple):
    """Represents a position on the game grid"""

    x: int
    y: int


class DirectionInfo(NamedTuple):
    """Represents direction vector and name"""

    vector: Tuple[int, int]
    name: str


# ============================================================================
# Constants
# ============================================================================

# Game grid dimensions
GRID_WIDTH = 20
GRID_HEIGHT = 15
GAME_SPEED_MS = 150

# UI constants
BORDER_OFFSET = 1
SCORE_PANEL_OFFSET = 4
STATUS_PANEL_Y = 1

# Direction constants for better readability
DIRECTION_UP = (0, -1)
DIRECTION_DOWN = (0, 1)
DIRECTION_LEFT = (-1, 0)
DIRECTION_RIGHT = (1, 0)

# Direction mappings
DIRECTION_KEYS = {
    curses.KEY_UP: DirectionInfo(DIRECTION_UP, "up"),
    curses.KEY_DOWN: DirectionInfo(DIRECTION_DOWN, "down"),
    curses.KEY_LEFT: DirectionInfo(DIRECTION_LEFT, "left"),
    curses.KEY_RIGHT: DirectionInfo(DIRECTION_RIGHT, "right"),
}

# Opposite directions for validation
OPPOSITE_DIRECTIONS = {
    DIRECTION_UP: DIRECTION_DOWN,
    DIRECTION_DOWN: DIRECTION_UP,
    DIRECTION_LEFT: DIRECTION_RIGHT,
    DIRECTION_RIGHT: DIRECTION_LEFT,
}


# ============================================================================
# Game Components
# ============================================================================


class FoodManager:
    """Manages food generation and positioning"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def generate_food(self, snake_positions: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Generate food at a random empty position"""
        while True:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if (x, y) not in snake_positions:
                return (x, y)


class GameRenderer:
    """Handles all game rendering and UI display"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def draw_game(self, stdscr, game_state: "SnakeGame"):
        """Draw the complete game state"""
        stdscr.clear()
        self._draw_borders(stdscr)
        self._draw_snake(stdscr, game_state.snake)
        self._draw_food(stdscr, game_state.food)
        self._draw_score(stdscr, game_state.score)
        self._draw_blockchain_status(stdscr, game_state.blockchain_enabled)
        self._draw_game_over(stdscr, game_state.game_over, self.height)
        stdscr.refresh()

    def _draw_borders(self, stdscr):
        """Draw game borders"""
        # Horizontal borders
        for x in range(self.width + 2):
            stdscr.addch(0, x, "#")
            stdscr.addch(self.height + 1, x, "#")

        # Vertical borders
        for y in range(self.height + 2):
            stdscr.addch(y, 0, "#")
            stdscr.addch(y, self.width + 1, "#")

    def _draw_snake(self, stdscr, snake: List[Tuple[int, int]]):
        """Draw the snake body"""
        for x, y in snake:
            stdscr.addch(y + BORDER_OFFSET, x + BORDER_OFFSET, "O")

    def _draw_food(self, stdscr, food: Tuple[int, int]):
        """Draw the food"""
        food_x, food_y = food
        stdscr.addch(food_y + BORDER_OFFSET, food_x + BORDER_OFFSET, "*")

    def _draw_score(self, stdscr, score: int):
        """Draw the score"""
        score_text = f"Score: {score}"
        stdscr.addstr(0, self.width + SCORE_PANEL_OFFSET, score_text)

    def _draw_blockchain_status(self, stdscr, blockchain_enabled: bool):
        """Draw blockchain connection status"""
        status = (
            "Blockchain: Connected" if blockchain_enabled else "Blockchain: Offline"
        )
        stdscr.addstr(STATUS_PANEL_Y, self.width + SCORE_PANEL_OFFSET, status)

    def _draw_game_over(self, stdscr, game_over: bool, height: int):
        """Draw game over message if applicable"""
        if not game_over:
            return

        message = "Game Over! Press 'r' to restart or 'q' to quit"
        stdscr.addstr(
            height // 2, (self.width - len(message)) // 2 + BORDER_OFFSET, message
        )


class InputHandler:
    """Handles user input processing and direction changes"""

    def __init__(self, blockchain_client=None):
        # Lazy import to avoid dependency issues during testing
        if blockchain_client is not None:
            try:
                from blockchain import BlockchainClient

                self.blockchain_client = blockchain_client
                self.blockchain_enabled = True
            except ImportError:
                # For testing: if blockchain module not available but client provided,
                # assume it's a mock and enable blockchain functionality
                self.blockchain_client = blockchain_client
                self.blockchain_enabled = True
        else:
            self.blockchain_client = None
            self.blockchain_enabled = False

    def process_input(
        self, key: int, current_direction: Tuple[int, int]
    ) -> Optional[Tuple[int, int]]:
        """
        Process user input and return new direction if valid.
        Returns None if input is invalid or direction change is blocked.
        """
        if key not in DIRECTION_KEYS:
            return None

        direction_info = DIRECTION_KEYS[key]

        # Prevent reversing into self
        if direction_info.vector == OPPOSITE_DIRECTIONS.get(current_direction):
            return None

        # Send blockchain transaction asynchronously
        self._send_blockchain_transaction(key, direction_info.name)

        return direction_info.vector

    def _send_blockchain_transaction(self, key: int, direction_name: str):
        """Send blockchain transaction for direction change"""
        if not self.blockchain_enabled or not self.blockchain_client:
            return

        def send_tx():
            self.blockchain_client.send_key_transaction(key, direction_name)

        thread = threading.Thread(target=send_tx, daemon=True)
        thread.start()


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
