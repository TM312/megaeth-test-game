"""
Input handling system for the Snake game
"""

import curses
import threading
from typing import Optional, Tuple

from .constants import DIRECTION_KEYS, OPPOSITE_DIRECTIONS


class InputHandler:
    """Handles user input processing and direction changes"""

    def __init__(self, blockchain_client=None):
        # Lazy import to avoid dependency issues during testing
        if blockchain_client is not None:
            try:
                from blockchain import BlockchainClient

                self.blockchain_client = blockchain_client
                self.blockchain_enabled = True
            except ImportError:
                # For testing: if blockchain module not available but client provided,
                # assume it's a mock and enable blockchain functionality
                self.blockchain_client = blockchain_client
                self.blockchain_enabled = True
        else:
            self.blockchain_client = None
            self.blockchain_enabled = False

    def process_input(
        self, key: int, current_direction: Tuple[int, int]
    ) -> Optional[Tuple[int, int]]:
        """
        Process user input and return new direction if valid.
        Returns None if input is invalid or direction change is blocked.
        """
        if key not in DIRECTION_KEYS:
            return None

        new_direction = DIRECTION_KEYS[key]

        # Prevent reversing into self
        if new_direction == OPPOSITE_DIRECTIONS.get(current_direction):
            return None

        # Send blockchain transaction asynchronously
        self._send_blockchain_transaction(key, self._get_direction_name(new_direction))

        return new_direction

    def _get_direction_name(self, direction: Tuple[int, int]) -> str:
        """Get the name of a direction vector"""
        from .constants import DIRECTION_NAMES

        return DIRECTION_NAMES.get(direction, "unknown")

    def _send_blockchain_transaction(self, key: int, direction_name: str):
        """Send blockchain transaction for direction change"""
        if not self.blockchain_enabled or not self.blockchain_client:
            return

        def send_tx():
            try:
                success, tx_hash = self.blockchain_client.send_key_transaction(
                    key, direction_name
                )
                # Record transaction in tracker
                from .transaction_tracker import transaction_tracker

                transaction_tracker.record_transaction(
                    key_code=key,
                    direction=direction_name,
                    success=success,
                    tx_hash=tx_hash.hex() if tx_hash else None,
                    error_message=None if success else "Transaction failed",
                )
            except Exception as e:
                # Record failed transaction
                from .transaction_tracker import transaction_tracker

                transaction_tracker.record_transaction(
                    key_code=key,
                    direction=direction_name,
                    success=False,
                    error_message=str(e),
                )

        thread = threading.Thread(target=send_tx, daemon=True)
        thread.start()
