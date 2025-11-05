"""
Game constants and configuration values
"""

import curses

# ============================================================================
# Game Grid Dimensions
# ============================================================================

GRID_WIDTH = 20
GRID_HEIGHT = 15
GAME_SPEED_MS = 150

# ============================================================================
# UI Constants
# ============================================================================

BORDER_OFFSET = 1
SCORE_PANEL_OFFSET = 4
STATUS_PANEL_Y = 1

# ============================================================================
# Color Constants
# ============================================================================

COLOR_SNAKE_HEAD = 1
COLOR_SNAKE_BODY = 2
COLOR_FOOD = 3
COLOR_BORDER = 4
COLOR_SCORE = 5
COLOR_GAME_OVER = 6
COLOR_BACKGROUND = 7

# ============================================================================
# Direction Constants
# ============================================================================

DIRECTION_UP = (0, -1)
DIRECTION_DOWN = (0, 1)
DIRECTION_LEFT = (-1, 0)
DIRECTION_RIGHT = (1, 0)

# Direction mappings for key presses
DIRECTION_KEYS = {
    curses.KEY_UP: DIRECTION_UP,
    curses.KEY_DOWN: DIRECTION_DOWN,
    curses.KEY_LEFT: DIRECTION_LEFT,
    curses.KEY_RIGHT: DIRECTION_RIGHT,
}

# Opposite directions for validation (prevent immediate reversal)
OPPOSITE_DIRECTIONS = {
    DIRECTION_UP: DIRECTION_DOWN,
    DIRECTION_DOWN: DIRECTION_UP,
    DIRECTION_LEFT: DIRECTION_RIGHT,
    DIRECTION_RIGHT: DIRECTION_LEFT,
}

# Direction names for display/logging
DIRECTION_NAMES = {
    DIRECTION_UP: "up",
    DIRECTION_DOWN: "down",
    DIRECTION_LEFT: "left",
    DIRECTION_RIGHT: "right",
}
