# Scripts Directory

This directory contains utility scripts for the Snake game.

## generate_wallet.py

Generates a new Ethereum wallet for MegaETH testnet usage.

### Usage

```bash
python3 scripts/generate_wallet.py
```

### What it does

- Generates a new random Ethereum private key
- Derives the corresponding wallet address
- Displays both values in a user-friendly format
- Optionally creates a `.env` file with the private key

### Output

```
============================================================
🎮 SNAKE GAME WALLET GENERATED
============================================================

📋 WALLET ADDRESS (for MegaETH faucet):
   0x123456789abcdef...

🔑 PRIVATE KEY (for .env file):
   0xabcdef123456789...

⚠️  IMPORTANT SECURITY NOTES:
   • Keep your private key secure and never share it
   • This is for testnet use only - has no real value
   • Use the wallet address to request testnet ETH from:
     https://megaeth-testnet.blockscout.com/faucet

📄 To use with Snake game, create/update your .env file:
   PRIVATE_KEY=0xabcdef123456789...
```

### Security Notes

- Private keys are generated locally and never transmitted
- This is for testnet use only - generated wallets have no real value
- Keep private keys secure and never share them
- The script only creates the `.env` file if it doesn't already exist
