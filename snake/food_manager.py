"""
Food management system for the Snake game
"""

import random
from typing import List, Tuple


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
