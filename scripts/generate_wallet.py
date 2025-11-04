#!/usr/bin/env python3
"""
Wallet Generation Script for Snake Game MegaETH Testnet

This script generates a new Ethereum wallet (private key and address)
that can be used with the Snake game for MegaETH testnet transactions.

Usage:
    python3 scripts/generate_wallet.py

Output:
    - Private Key: For use in .env file as PRIVATE_KEY
    - Wallet Address: For requesting testnet funds from MegaETH faucet
"""

import os
import sys
from eth_account import Account


def generate_wallet():
    """Generate a new Ethereum wallet"""
    # Generate a new account with random private key
    account = Account.create()

    return {"private_key": account.key.hex(), "address": account.address}


def print_wallet_info(wallet):
    """Print wallet information in a user-friendly format"""
    print("=" * 60)
    print("🎮 SNAKE GAME WALLET GENERATED")
    print("=" * 60)
    print()
    print("📋 WALLET ADDRESS (for MegaETH faucet):")
    print(f"   {wallet['address']}")
    print()
    print("🔑 PRIVATE KEY (for .env file):")
    print(f"   {wallet['private_key']}")
    print()
    print("⚠️  IMPORTANT SECURITY NOTES:")
    print("   • Keep your private key secure and never share it")
    print("   • This is for testnet use only - has no real value")
    print("   • Use the wallet address to request testnet ETH from:")
    print("     https://testnet.megaeth.com/")
    print()
    print("📄 To use with Snake game, create/update your .env file:")
    print("   PRIVATE_KEY={}".format(wallet["private_key"]))
    print()
    print("=" * 60)


def main():
    """Main script execution"""
    try:
        print("Generating new Ethereum wallet for Snake game...")
        print()

        wallet = generate_wallet()
        print_wallet_info(wallet)

        # Optional: Save to .env file if it doesn't exist
        env_file = ".env"
        if not os.path.exists(env_file):
            print(f"💡 Tip: Creating {env_file} file with your private key...")
            with open(env_file, "w") as f:
                f.write(f"PRIVATE_KEY={wallet['private_key']}\n")
                f.write("# MegaETH Testnet Configuration\n")
                f.write("# Wallet Address for faucet: {}\n".format(wallet["address"]))
            print(f"✅ Created {env_file} file!")
        else:
            print(
                "ℹ️  .env file already exists - manually add your PRIVATE_KEY if needed"
            )

    except Exception as e:
        print(f"❌ Error generating wallet: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
