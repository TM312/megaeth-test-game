#!/usr/bin/env python3
"""
Simple test to verify terminal size validation works
"""

import curses
from unittest.mock import Mock, patch

# Import the main function and dependencies
from main import main
from snake.constants import GRID_WIDTH, GRID_HEIGHT


def test_small_terminal():
    """Test that the game exits gracefully with a small terminal"""

    # Create a mock stdscr with small dimensions
    mock_stdscr = Mock()
    mock_stdscr.getmaxyx.return_value = (10, 10)  # Too small
    mock_stdscr.clear = Mock()
    mock_stdscr.addstr = Mock()
    mock_stdscr.refresh = Mock()
    mock_stdscr.getch = Mock(return_value=ord("q"))

    # This should exit early due to small terminal
    try:
        main(mock_stdscr)
        print(
            "✓ Terminal size validation works - game exited gracefully for small terminal"
        )
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    # Verify the correct error message was displayed
    expected_msg_start = "Terminal too small! Need at least"
    calls = mock_stdscr.addstr.call_args_list
    if calls and expected_msg_start in calls[0][0][2]:
        print("✓ Correct error message displayed")
        return True
    else:
        print("✗ Error message not displayed correctly")
        return False


def test_large_enough_terminal():
    """Test that the game proceeds with adequate terminal size"""

    # Create a mock stdscr with adequate dimensions
    mock_stdscr = Mock()
    mock_stdscr.getmaxyx.return_value = (25, 25)  # Large enough
    mock_stdscr.clear = Mock()
    mock_stdscr.addstr = Mock()
    mock_stdscr.refresh = Mock()
    mock_stdscr.getch = Mock(return_value=ord("q"))
    mock_stdscr.nodelay = Mock()
    mock_stdscr.timeout = Mock()
    mock_stdscr.curs_set = Mock()

    # Mock the game initialization to avoid blockchain dependencies
    with patch("main._initialize_game") as mock_init_game, patch(
        "main._show_welcome_screen"
    ) as mock_welcome, patch("curses.wrapper") as mock_wrapper:

        mock_game = Mock()
        mock_game.game_over = True  # Make it exit immediately
        mock_init_game.return_value = mock_game

        try:
            main(mock_stdscr)
            print("✓ Terminal size validation allows adequate terminal size")
            return True
        except Exception as e:
            print(f"✗ Unexpected error with adequate terminal: {e}")
            return False


if __name__ == "__main__":
    print("Testing terminal size validation...")

    # Test 1: Small terminal should be rejected
    print("\n1. Testing small terminal rejection:")
    if test_small_terminal():
        print("✓ Small terminal test passed")
    else:
        print("✗ Small terminal test failed")

    # Test 2: Adequate terminal should proceed
    print("\n2. Testing adequate terminal acceptance:")
    if test_large_enough_terminal():
        print("✓ Adequate terminal test passed")
    else:
        print("✗ Adequate terminal test failed")

    print(
        f"\nMinimum required size: {GRID_WIDTH + 2}x{GRID_HEIGHT + 2} ({GRID_WIDTH}x{GRID_HEIGHT} game + 2x2 borders)"
    )
