"""
Game rendering system for the Snake game (Pygame implementation)
"""

import logging
from typing import List, Tuple

import pygame

from .constants import (
    CELL_SIZE,
    WINDOW_PADDING,
    BORDER_THICKNESS,
    COLOR_SNAKE_HEAD,
    COLOR_SNAKE_BODY,
    COLOR_FOOD,
    COLOR_BORDER,
    COLOR_SCORE,
    COLOR_GAME_OVER_TEXT,
    COLOR_GAME_OVER_BG,
    COLOR_BACKGROUND,
)

logger = logging.getLogger(__name__)


class GameRenderer:
    """Handles all game rendering and UI display using Pygame"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.cell_size = CELL_SIZE
        self.padding = WINDOW_PADDING
        self.border_thickness = BORDER_THICKNESS

        self.screen = None
        self.font_small = None
        self.font_large = None

    # ---------------------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------------------
    def init_window(self):
        """Initialize Pygame display and fonts; return window surface."""
        pygame.init()
        pygame.font.init()

        playfield_w = self.width * self.cell_size
        playfield_h = self.height * self.cell_size

        # Reserve top area for score/status (approx 40px)
        hud_height = 40

        window_w = self.padding * 2 + playfield_w + self.border_thickness * 2
        window_h = (
            self.padding * 2 + hud_height + playfield_h + self.border_thickness * 2
        )

        self.screen = pygame.display.set_mode((window_w, window_h))
        pygame.display.set_caption("Snake (Pygame)")

        # Use default fonts for portability
        self.font_small = pygame.font.SysFont(None, 22)
        self.font_large = pygame.font.SysFont(None, 36)

        return self.screen

    # ---------------------------------------------------------------------
    # Drawing helpers
    # ---------------------------------------------------------------------
    def _playfield_origin(self) -> Tuple[int, int]:
        """Top-left (x,y) pixel position of the playfield (inside border)."""
        hud_height = 40
        x0 = self.padding + self.border_thickness
        y0 = self.padding + hud_height + self.border_thickness
        return x0, y0

    def _playfield_rect(self) -> pygame.Rect:
        x0, y0 = self._playfield_origin()
        return pygame.Rect(
            x0 - self.border_thickness,
            y0 - self.border_thickness,
            self.width * self.cell_size + self.border_thickness * 2,
            self.height * self.cell_size + self.border_thickness * 2,
        )

    def _cell_to_px(self, cell: Tuple[int, int]) -> pygame.Rect:
        x0, y0 = self._playfield_origin()
        cx, cy = cell
        return pygame.Rect(
            x0 + cx * self.cell_size,
            y0 + cy * self.cell_size,
            self.cell_size,
            self.cell_size,
        )

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def draw_game(self, game_state) -> None:
        """Draw the complete game state to the window."""
        if self.screen is None:
            raise RuntimeError(
                "Renderer window not initialized. Call init_window() first."
            )

        # Background
        self.screen.fill(COLOR_BACKGROUND)

        # Border
        pygame.draw.rect(
            self.screen,
            COLOR_BORDER,
            self._playfield_rect(),
            width=self.border_thickness,
        )

        # Snake
        self._draw_snake(game_state.snake)

        # Food
        self._draw_food(game_state.food)

        # HUD (score and blockchain status)
        self._draw_hud(game_state.score, game_state.blockchain_enabled)

        # Game Over overlay
        if game_state.game_over:
            self._draw_game_over_overlay()

        pygame.display.flip()

    # ------------------------------------------------------------------
    def _draw_snake(self, snake: List[Tuple[int, int]]):
        """Draw the snake (body segments then head)."""
        if not snake:
            return

        # Body segments (skip head at index 0)
        for segment in snake[1:]:
            pygame.draw.rect(
                self.screen,
                COLOR_SNAKE_BODY,
                self._cell_to_px(segment),
            )

        # Head (first segment)
        pygame.draw.rect(
            self.screen,
            COLOR_SNAKE_HEAD,
            self._cell_to_px(snake[0]),
        )

    def _draw_food(self, food: Tuple[int, int]):
        fx, fy = food
        rect = self._cell_to_px((fx, fy))
        pygame.draw.rect(self.screen, COLOR_FOOD, rect)

    def _draw_hud(self, score: int, blockchain_enabled: bool):
        hud_text = f"Score: {score}    " + (
            "Connected" if blockchain_enabled else "Offline"
        )
        text_surf = self.font_small.render(hud_text, True, COLOR_SCORE)
        # Position at top-left inside padding
        self.screen.blit(text_surf, (self.padding, self.padding))

    def _draw_game_over_overlay(self):
        # Centered panel
        panel_w = int(self.width * self.cell_size * 0.9)
        panel_h = 140
        x0, y0 = self._playfield_origin()
        cx = x0 + (self.width * self.cell_size - panel_w) // 2
        cy = y0 + (self.height * self.cell_size - panel_h) // 2
        panel_rect = pygame.Rect(cx, cy, panel_w, panel_h)

        pygame.draw.rect(self.screen, COLOR_GAME_OVER_BG, panel_rect)
        pygame.draw.rect(self.screen, COLOR_GAME_OVER_TEXT, panel_rect, width=3)

        title = self.font_large.render("GAME OVER!", True, COLOR_GAME_OVER_TEXT)
        line1 = self.font_small.render(
            "Press 'R' to Restart", True, COLOR_GAME_OVER_TEXT
        )
        line2 = self.font_small.render("Press 'Q' to Quit", True, COLOR_GAME_OVER_TEXT)

        # Center text within panel
        self.screen.blit(
            title, (panel_rect.centerx - title.get_width() // 2, panel_rect.y + 18)
        )
        self.screen.blit(
            line1, (panel_rect.centerx - line1.get_width() // 2, panel_rect.y + 60)
        )
        self.screen.blit(
            line2, (panel_rect.centerx - line2.get_width() // 2, panel_rect.y + 90)
        )
