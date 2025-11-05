"""
Game rendering system for the Snake game
"""

import curses
import logging
from typing import List, Tuple

from .constants import (
    BORDER_OFFSET,
    SCORE_PANEL_OFFSET,
    STATUS_PANEL_Y,
    COLOR_SNAKE_HEAD,
    COLOR_SNAKE_BODY,
    COLOR_FOOD,
    COLOR_BORDER,
    COLOR_SCORE,
    COLOR_GAME_OVER,
)

logger = logging.getLogger(__name__)


class GameRenderer:
    """Handles all game rendering and UI display"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def init_colors(self, stdscr):
        """Initialize color pairs if terminal supports colors"""
        try:
            if curses.has_colors():
                curses.start_color()

                # Define color pairs
                curses.init_pair(
                    COLOR_SNAKE_HEAD, curses.COLOR_YELLOW, curses.COLOR_BLACK
                )
                curses.init_pair(
                    COLOR_SNAKE_BODY, curses.COLOR_GREEN, curses.COLOR_BLACK
                )
                curses.init_pair(COLOR_FOOD, curses.COLOR_RED, curses.COLOR_BLACK)
                curses.init_pair(COLOR_BORDER, curses.COLOR_WHITE, curses.COLOR_BLACK)
                curses.init_pair(COLOR_SCORE, curses.COLOR_CYAN, curses.COLOR_BLACK)
                curses.init_pair(COLOR_GAME_OVER, curses.COLOR_RED, curses.COLOR_WHITE)
                curses.init_pair(
                    COLOR_BACKGROUND, curses.COLOR_BLACK, curses.COLOR_BLACK
                )

                # Set background color
                stdscr.bkgd(" ", curses.color_pair(COLOR_BACKGROUND))
        except Exception:
            # Colors not supported or curses not initialized - continue without colors
            pass

    def _safe_addch_colored(
        self, stdscr, y: int, x: int, char, color_pair: int
    ) -> bool:
        """Safely add a colored character at position"""
        try:
            max_y, max_x = stdscr.getmaxyx()
            if 0 <= y < max_y and 0 <= x < max_x:
                # Try colored version first, fallback to monochrome
                try:
                    if curses.has_colors():
                        stdscr.addch(y, x, char, curses.color_pair(color_pair))
                    else:
                        stdscr.addch(y, x, char)
                except Exception:
                    # Fallback to monochrome if color fails
                    stdscr.addch(y, x, char)
                return True
            return False
        except Exception:
            return False

    def _safe_addstr_colored(
        self, stdscr, y: int, x: int, text: str, color_pair: int
    ) -> bool:
        """Safely add a colored string at position"""
        try:
            max_y, max_x = stdscr.getmaxyx()
            if 0 <= y < max_y and 0 <= x < max_x:
                # Truncate text if it would exceed right boundary
                available_space = max_x - x
                if len(text) > available_space:
                    text = text[: available_space - 1]
                # Try colored version first, fallback to monochrome
                try:
                    if curses.has_colors():
                        stdscr.addstr(y, x, text, curses.color_pair(color_pair))
                    else:
                        stdscr.addstr(y, x, text)
                except Exception:
                    # Fallback to monochrome if color fails
                    stdscr.addstr(y, x, text)
                return True
            return False
        except Exception:
            return False

    def draw_game(self, stdscr, game_state):
        """Draw the complete game state"""
        try:
            stdscr.clear()
            self._draw_borders(stdscr)
            self._draw_snake(stdscr, game_state.snake)
            self._draw_food(stdscr, game_state.food)
            self._draw_score(stdscr, game_state.score)
            self._draw_blockchain_status(stdscr, game_state.blockchain_enabled)
            self._draw_game_over(stdscr, game_state.game_over, self.height)
            stdscr.refresh()
        except Exception as e:
            logger.error(f"Render error: {e}", exc_info=True)
            # Handle curses errors gracefully
            try:
                stdscr.clear()
                error_msg = f"Render error: {str(e)[:40]}"
                self._safe_addstr(stdscr, 0, 0, error_msg)
                stdscr.refresh()
            except Exception as err:
                logger.error(f"Failed to display error message: {err}", exc_info=True)
                pass  # Silently fail if we can't even display error

    def _safe_addch(self, stdscr, y: int, x: int, char) -> bool:
        """Safely add a character at position, checking bounds first"""
        try:
            max_y, max_x = stdscr.getmaxyx()
            if 0 <= y < max_y and 0 <= x < max_x:
                stdscr.addch(y, x, char)
                return True
            else:
                pass  # Out of bounds - silently skip
                return False
        except Exception as e:
            logger.warning(f"_safe_addch failed: {e}")
            return False

    def _safe_addstr(self, stdscr, y: int, x: int, text: str) -> bool:
        """Safely add a string at position, checking bounds first"""
        try:
            max_y, max_x = stdscr.getmaxyx()
            if 0 <= y < max_y and 0 <= x < max_x:
                # Truncate text if it would exceed right boundary
                available_space = max_x - x
                if len(text) > available_space:
                    text = text[: available_space - 1]
                stdscr.addstr(y, x, text)
                return True
            else:
                pass  # Out of bounds - silently skip
                return False
        except Exception as e:
            logger.warning(f"_safe_addstr failed: {e}")
            return False

    def _draw_borders(self, stdscr):
        """Draw game borders"""
        try:
            max_y, max_x = stdscr.getmaxyx()

            # Horizontal borders - use double lines for better appearance
            for x in range(min(self.width + 2, max_x)):
                self._safe_addch_colored(stdscr, 0, x, "═", COLOR_BORDER)
                if self.height + 1 < max_y:
                    self._safe_addch_colored(
                        stdscr, self.height + 1, x, "═", COLOR_BORDER
                    )

            # Vertical borders
            for y in range(min(self.height + 2, max_y)):
                self._safe_addch_colored(stdscr, y, 0, "║", COLOR_BORDER)
                if self.width + 1 < max_x:
                    self._safe_addch_colored(
                        stdscr, y, self.width + 1, "║", COLOR_BORDER
                    )

            # Corner pieces
            if self.width + 1 < max_x and self.height + 1 < max_y:
                self._safe_addch_colored(stdscr, 0, 0, "╔", COLOR_BORDER)
                self._safe_addch_colored(stdscr, 0, self.width + 1, "╗", COLOR_BORDER)
                self._safe_addch_colored(stdscr, self.height + 1, 0, "╚", COLOR_BORDER)
                self._safe_addch_colored(
                    stdscr, self.height + 1, self.width + 1, "╝", COLOR_BORDER
                )
        except Exception as e:
            logger.error(f"Error drawing borders: {e}", exc_info=True)

    def _draw_snake(self, stdscr, snake: List[Tuple[int, int]]):
        """Draw the snake body"""
        try:
            if not snake:
                return

            # Draw snake body (all segments except head)
            for x, y in snake[1:]:
                self._safe_addch_colored(
                    stdscr, y + BORDER_OFFSET, x + BORDER_OFFSET, "█", COLOR_SNAKE_BODY
                )

            # Draw snake head (first segment)
            if snake:
                head_x, head_y = snake[0]
                self._safe_addch_colored(
                    stdscr,
                    head_y + BORDER_OFFSET,
                    head_x + BORDER_OFFSET,
                    "●",
                    COLOR_SNAKE_HEAD,
                )
        except Exception as e:
            logger.error(f"Error drawing snake: {e}", exc_info=True)

    def _draw_food(self, stdscr, food: Tuple[int, int]):
        """Draw the food"""
        try:
            food_x, food_y = food
            self._safe_addch_colored(
                stdscr, food_y + BORDER_OFFSET, food_x + BORDER_OFFSET, "🍎", COLOR_FOOD
            )
        except Exception as e:
            logger.error(f"Error drawing food: {e}", exc_info=True)

    def _draw_score(self, stdscr, score: int):
        """Draw the score"""
        try:
            score_text = f"Score: {score}"
            self._safe_addstr_colored(
                stdscr, 0, self.width + SCORE_PANEL_OFFSET, score_text, COLOR_SCORE
            )
        except Exception as e:
            logger.error(f"Error drawing score: {e}", exc_info=True)

    def _draw_blockchain_status(self, stdscr, blockchain_enabled: bool):
        """Draw blockchain connection status"""
        try:
            status = "🌐 Connected" if blockchain_enabled else "📴 Offline"
            self._safe_addstr_colored(
                stdscr,
                STATUS_PANEL_Y,
                self.width + SCORE_PANEL_OFFSET,
                status,
                COLOR_SCORE,
            )
        except Exception as e:
            logger.error(f"Error drawing blockchain status: {e}", exc_info=True)

    def _draw_game_over(self, stdscr, game_over: bool, height: int):
        """Draw game over message if applicable"""
        try:
            if not game_over:
                return

            # Create a more visually appealing game over screen
            messages = [
                "╔══════════════════════════════════════════════╗",
                "║                 GAME OVER!                   ║",
                "║                                              ║",
                "║        Press 'R' to Restart                  ║",
                "║        Press 'Q' to Quit                     ║",
                "╚══════════════════════════════════════════════╝",
            ]

            start_y = max(0, (height // 2) - 3)
            for i, msg in enumerate(messages):
                y_pos = start_y + i
                x_pos = max(0, (self.width - len(msg)) // 2 + BORDER_OFFSET)
                self._safe_addstr_colored(stdscr, y_pos, x_pos, msg, COLOR_GAME_OVER)

        except Exception as e:
            logger.error(f"Error drawing game over: {e}", exc_info=True)
