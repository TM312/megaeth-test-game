"""
Main entry point for the Snake game application
"""

import curses
import logging

# Configure logging for main module
logger = logging.getLogger(__name__)

try:
    from .blockchain import BlockchainClient
    from .snake import SnakeGame, GAME_SPEED_MS
    from .snake.constants import GRID_WIDTH, GRID_HEIGHT
except ImportError:
    from blockchain import BlockchainClient
    from snake import SnakeGame, GAME_SPEED_MS
    from snake.constants import GRID_WIDTH, GRID_HEIGHT


def main(stdscr):
    """Main game loop"""
    try:
        _setup_curses(stdscr)

        # Check terminal size
        max_y, max_x = stdscr.getmaxyx()
        min_width = GRID_WIDTH + 2  # +2 for borders
        min_height = GRID_HEIGHT + 2  # +2 for borders

        if max_x < min_width or max_y < min_height:
            stdscr.clear()
            error_msg = (
                f"Terminal too small! Need at least {min_width}x{min_height}, "
                f"got {max_x}x{max_y}"
            )
            stdscr.addstr(0, 0, error_msg)
            stdscr.addstr(2, 0, "Press any key to exit...")
            stdscr.refresh()
            stdscr.getch()
            return

        game = _initialize_game()

        # Initialize colors for better visual design
        game.renderer.init_colors(stdscr)

        # Show welcome screen
        _show_welcome_screen(stdscr, game)

        # Initialize transaction tracking
        from snake.transaction_tracker import transaction_tracker

        transaction_tracker.start_session()

        while True:
            game.draw(stdscr)

            if game.game_over:
                _handle_game_over(stdscr, game)
                continue

            # Handle input and game logic
            key = stdscr.getch()
            if _should_quit(key):
                break

            game.process_input(key)
            game.update()

    except KeyboardInterrupt:
        pass  # Handle Ctrl+C gracefully
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
        _handle_error(stdscr, e)
    finally:
        # Display transaction summary
        from snake.transaction_tracker import transaction_tracker

        transaction_tracker.end_session()
        transaction_tracker.print_summary()


def _show_welcome_screen(stdscr, game):
    """Show welcome screen before starting the game"""
    try:
        # Clear screen
        stdscr.clear()

        # Get terminal dimensions
        max_y, max_x = stdscr.getmaxyx()

        # Welcome message
        welcome_lines = [
            "🐍 SNAKE GAME with MegaETH Blockchain Integration 🐍",
            "",
            "🎮 Controls:",
            "   ↑↓←→ Arrow keys to move",
            "   Q to quit",
            "",
            "🎯 Goal:",
            "   Eat the 🍎 to grow and score points",
            "   Avoid walls and yourself",
            "",
            "🌐 Blockchain:",
            "   Each move sends a transaction to MegaETH testnet",
            "",
            "🎨 Features:",
            "   Colorful graphics (if supported)",
            "   Transaction tracking and summary",
            "",
            "Press any key to start...",
        ]

        # Center the welcome message
        start_y = max(1, (max_y - len(welcome_lines)) // 2)

        for i, line in enumerate(welcome_lines):
            y_pos = start_y + i
            x_pos = max(0, (max_x - len(line)) // 2)
            if y_pos < max_y:
                game.renderer._safe_addstr_colored(
                    stdscr, y_pos, x_pos, line, 5
                )  # Cyan color

        stdscr.refresh()

        # Wait for any key press
        stdscr.nodelay(False)  # Blocking input for welcome screen
        stdscr.getch()
        stdscr.nodelay(True)  # Back to non-blocking

    except Exception as e:
        logger.error(f"Error showing welcome screen: {e}", exc_info=True)


def _setup_curses(stdscr):
    """Setup curses configuration"""
    try:
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True)  # Non-blocking input
        stdscr.timeout(GAME_SPEED_MS)  # Game speed
    except Exception as e:
        logger.error(f"Curses setup failed: {e}", exc_info=True)
        raise


def _initialize_game():
    """Initialize game with blockchain client"""
    blockchain_client = BlockchainClient()
    return SnakeGame(blockchain_client=blockchain_client)


def _handle_game_over(stdscr, game):
    """Handle game over state and restart logic"""
    key = stdscr.getch()
    if key == ord("r"):
        # Restart with new game
        game.reset()
    elif key == ord("q"):
        raise KeyboardInterrupt  # Exit game loop


def _should_quit(key: int) -> bool:
    """Check if quit key was pressed"""
    return key == ord("q")


def _handle_error(stdscr, error: Exception):
    """Handle unexpected errors gracefully"""
    try:
        stdscr.clear()
        error_msg = f"An error occurred: {error}"
        stdscr.addstr(0, 0, error_msg)
        stdscr.addstr(2, 0, "Press any key to exit...")
        stdscr.refresh()
        stdscr.getch()
    except Exception:
        print(f"Error: {error}")  # Fallback if curses fails


def run():
    """Run the game with curses wrapper"""
    curses.wrapper(main)


if __name__ == "__main__":
    run()
