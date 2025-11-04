"""
Main entry point for the Snake game application
"""

import curses

try:
    from .blockchain import BlockchainClient
    from .game import SnakeGame, GAME_SPEED_MS
except ImportError:
    from blockchain import BlockchainClient
    from game import SnakeGame, GAME_SPEED_MS


def main(stdscr):
    """Main game loop"""
    try:
        _setup_curses(stdscr)
        game = _initialize_game()

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
        _handle_error(stdscr, e)


def _setup_curses(stdscr):
    """Setup curses configuration"""
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Non-blocking input
    stdscr.timeout(GAME_SPEED_MS)  # Game speed


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
