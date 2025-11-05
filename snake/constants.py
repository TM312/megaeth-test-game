"""
Game constants and configuration values for the Pygame renderer
"""

import pygame

# ============================================================================
# Game Grid Dimensions
# ============================================================================

GRID_WIDTH = 20
GRID_HEIGHT = 15
GAME_SPEED_MS = 150  # milliseconds between updates

# ============================================================================
# Rendering Constants (Pygame)
# ============================================================================

# Size of one logical cell in pixels
CELL_SIZE = 24

# Window padding around the playfield (in pixels)
WINDOW_PADDING = 16

# Border thickness (in pixels)
BORDER_THICKNESS = 2

# ============================================================================
# Color Constants (RGB tuples)
# ============================================================================

COLOR_SNAKE_HEAD = (255, 215, 0)  # gold
COLOR_SNAKE_BODY = (40, 200, 40)  # green
COLOR_FOOD = (220, 20, 60)  # crimson
COLOR_BORDER = (200, 200, 200)  # light gray
COLOR_SCORE = (0, 200, 255)  # cyan-ish
COLOR_GAME_OVER_TEXT = (220, 50, 50)
COLOR_GAME_OVER_BG = (230, 230, 230)
COLOR_BACKGROUND = (0, 0, 0)  # black

# ============================================================================
# Direction Constants
# ============================================================================

DIRECTION_UP = (0, -1)
DIRECTION_DOWN = (0, 1)
DIRECTION_LEFT = (-1, 0)
DIRECTION_RIGHT = (1, 0)

# Direction mappings for key presses (Pygame key constants)
DIRECTION_KEYS = {
    pygame.K_UP: DIRECTION_UP,
    pygame.K_DOWN: DIRECTION_DOWN,
    pygame.K_LEFT: DIRECTION_LEFT,
    pygame.K_RIGHT: DIRECTION_RIGHT,
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
