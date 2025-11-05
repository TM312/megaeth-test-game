"""
Transaction tracking for Snake game blockchain interactions
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class TransactionRecord:
    """Record of a blockchain transaction"""

    timestamp: datetime
    key_code: int
    direction: str
    success: bool
    tx_hash: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class TransactionTracker:
    """Tracks all blockchain transactions during gameplay"""

    def __init__(self):
        self.transactions: List[TransactionRecord] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def start_session(self):
        """Start tracking a new game session"""
        self.transactions = []
        self.start_time = datetime.now()

    def end_session(self):
        """End the current game session"""
        self.end_time = datetime.now()

    def record_transaction(
        self,
        key_code: int,
        direction: str,
        success: bool,
        tx_hash: Optional[str] = None,
        error_message: Optional[str] = None,
    ):
        """Record a transaction attempt"""
        record = TransactionRecord(
            timestamp=datetime.now(),
            key_code=key_code,
            direction=direction,
            success=success,
            tx_hash=tx_hash,
            error_message=error_message,
        )
        self.transactions.append(record)

    def get_successful_transactions(self) -> List[TransactionRecord]:
        """Get all successful transactions"""
        return [tx for tx in self.transactions if tx.success]

    def get_failed_transactions(self) -> List[TransactionRecord]:
        """Get all failed transactions"""
        return [tx for tx in self.transactions if not tx.success]

    def get_transaction_summary(self) -> Dict:
        """Get summary statistics of transactions"""
        total = len(self.transactions)
        successful = len(self.get_successful_transactions())
        failed = len(self.get_failed_transactions())

        return {
            "total_transactions": total,
            "successful_transactions": successful,
            "failed_transactions": failed,
            "success_rate": f"{(successful / total * 100):.1f}%" if total > 0 else "0%",
            "session_duration": (
                str(self.end_time - self.start_time)
                if self.end_time and self.start_time
                else None
            ),
        }

    def print_summary(self):
        """Print transaction summary to console"""
        if not self.transactions:
            print("\n🚫 No blockchain transactions recorded (offline mode)")
            return

        summary = self.get_transaction_summary()

        print("\n" + "=" * 60)
        print("🎮 SNAKE GAME BLOCKCHAIN SUMMARY")
        print("=" * 60)
        print(f"📊 Total Transactions: {summary['total_transactions']}")
        print(f"✅ Successful: {summary['successful_transactions']}")
        print(f"❌ Failed: {summary['failed_transactions']}")
        print(f"📈 Success Rate: {summary['success_rate']}")

        if summary["session_duration"]:
            print(f"⏱️  Game Duration: {summary['session_duration']}")

        if self.transactions:
            print(f"\n📋 Transaction Details:")
            for i, tx in enumerate(self.transactions[:10], 1):  # Show first 10
                status = "✅" if tx.success else "❌"
                direction = tx.direction.upper()
                time_str = tx.timestamp.strftime("%H:%M:%S")
                print(f"  {i}. {time_str} - {direction} ({tx.key_code}) {status}")
                if tx.tx_hash:
                    print(f"     Hash: {tx.tx_hash}")

            if len(self.transactions) > 10:
                print(f"     ... and {len(self.transactions) - 10} more transactions")

        print("=" * 60)

    def export_to_json(self, filename: str = "snake_transactions.json"):
        """Export transactions to JSON file"""
        data = {
            "session_start": self.start_time.isoformat() if self.start_time else None,
            "session_end": self.end_time.isoformat() if self.end_time else None,
            "summary": self.get_transaction_summary(),
            "transactions": [tx.to_dict() for tx in self.transactions],
        }

        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

        print(f"📄 Transactions exported to {filename}")


# Global instance for the game
transaction_tracker = TransactionTracker()
