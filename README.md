# Terminal Snake Game with MegaETH Testnet Integration

A terminal Snake game that sends each key press as a transaction to the MegaETH testnet.

## Quick Start

```bash
make install  # Install dependencies
make wallet   # Generate MegaETH testnet wallet
make run      # Start the game
```

## Setup Details

1. **Generate Wallet**: Creates an Ethereum wallet and saves the private key to `.env`
2. **Get Testnet Funds**: Visit https://testnet.megaeth.com/ and request ETH using your wallet address
3. **Optional Config**: Edit `.env` for custom RPC URL or debug settings

## Make Commands

```bash
make help     # Show all commands
make install  # Install dependencies
make run      # Start game
make test     # Run tests
make wallet   # Generate wallet
make clean    # Clean up files
```

## Controls

- **Arrow Keys**: Move snake (sends transaction per keypress)
- **Q**: Quit game
- **R**: Restart after game over

## Game Rules

- Control snake with arrow keys
- Eat `*` to grow and score points
- Avoid walls and self-collision
- Each valid keypress creates a MegaETH testnet transaction

## Requirements

- Python 3.8+
- curses (Unix systems)
- web3.py, python-dotenv

## Project Structure

```
snake/
├── snake/                 # Game package
│   ├── __init__.py       # Package exports
│   ├── constants.py      # Game constants and configuration
│   ├── data_structures.py # Position and DirectionInfo classes
│   ├── food_manager.py   # Food generation logic
│   ├── game_renderer.py  # Rendering and UI system
│   ├── input_handler.py  # Input processing and blockchain
│   ├── game.py          # Core SnakeGame class
│   └── transaction_tracker.py # Transaction recording
├── main.py               # Application entry point
├── tests/                # Test suite
└── scripts/              # Utility scripts
```

## Features

- Terminal-based Snake game
- Score tracking and game over detection
- **MegaETH Testnet Integration**: Each keypress sends a transaction
- Asynchronous transactions (non-blocking)
- Connection status display
- Works offline (transactions only sent when connected)

## Blockchain

- **Network**: MegaETH Testnet (https://carrot.megaeth.com/rpc)
- **Transactions**: Self-transfers with key event data
- **Gas**: 21,000 | **Value**: 0 ETH

API Docs: https://megaeth-testnet.blockscout.com/api-docs
