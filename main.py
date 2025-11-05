"""
Main entry point for the Snake game application (Pygame version)
"""

import logging
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame

# Configure logging for main module
logger = logging.getLogger(__name__)

try:
    from .blockchain import BlockchainClient
    from .snake import SnakeGame, GAME_SPEED_MS
except ImportError:
    from blockchain import BlockchainClient
    from snake import SnakeGame, GAME_SPEED_MS


def main():
    """Main game loop using Pygame"""
    try:
        # Initialize game and renderer
        game = _initialize_game()

        # Initialize Pygame window via renderer
        screen = game.renderer.init_window()

        # Initialize transaction tracking
        from snake.transaction_tracker import transaction_tracker

        transaction_tracker.start_session()

        clock = pygame.time.Clock()
        last_update = pygame.time.get_ticks()
        running = True

        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_r and game.game_over:
                        game.reset()
                    else:
                        game.process_input(event.key)

            # Timed game updates
            now = pygame.time.get_ticks()
            if not game.game_over and (now - last_update) >= GAME_SPEED_MS:
                game.update()
                last_update = now

            # Render
            game.renderer.draw_game(game)
            clock.tick(60)

    except KeyboardInterrupt:
        pass  # Graceful exit on Ctrl+C
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
    finally:
        # Display transaction summary
        from snake.transaction_tracker import transaction_tracker

        transaction_tracker.end_session()
        transaction_tracker.print_summary()
        try:
            pygame.quit()
        except Exception:
            pass


def _initialize_game():
    """Initialize game with blockchain client"""
    blockchain_client = BlockchainClient()
    return SnakeGame(blockchain_client=blockchain_client)


def _handle_error(error: Exception):
    """Handle unexpected errors gracefully (console fallback)"""
    print(f"Error: {error}")


def run():
    """Run the game"""
    main()


if __name__ == "__main__":
    run()
