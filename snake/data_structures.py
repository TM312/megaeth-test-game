"""
Data structures for the Snake game
"""

from typing import Tuple, NamedTuple


class Position(NamedTuple):
    """Represents a position on the game grid"""

    x: int
    y: int


class DirectionInfo(NamedTuple):
    """Represents direction vector and name"""

    vector: Tuple[int, int]
    name: str
