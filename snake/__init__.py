"""
Snake Game Package

A terminal-based Snake game with MegaETH blockchain integration.
"""

from .game import SnakeGame
from .constants import (
    GRID_WIDTH,
    GRID_HEIGHT,
    GAME_SPEED_MS,
    DIRECTION_UP,
    DIRECTION_DOWN,
    DIRECTION_LEFT,
    DIRECTION_RIGHT,
)
from .transaction_tracker import transaction_tracker

__version__ = "1.0.0"

__all__ = [
    "SnakeGame",
    "GRID_WIDTH",
    "GRID_HEIGHT",
    "GAME_SPEED_MS",
    "DIRECTION_UP",
    "DIRECTION_DOWN",
    "DIRECTION_LEFT",
    "DIRECTION_RIGHT",
    "transaction_tracker",
]
