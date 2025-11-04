# Snake Game Makefile

.PHONY: help install run test wallet clean

# Default target
help: ## Show this help message
	@echo "🐍 Snake Game - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

# Running the game
run: ## Run the Snake game
	@echo "🎮 Starting Snake game..."
	python3 main.py

# Testing
test: ## Run all tests
	@echo "🧪 Running tests..."
	pytest

# Wallet generation
wallet: ## Generate a new MegaETH testnet wallet
	@echo "🔑 Generating new wallet..."
	python3 scripts/generate_wallet.py

# Cleanup
clean: ## Clean up generated files
	@echo "🧹 Cleaning up..."
	rm -rf __pycache__/
	rm -rf snake/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf scripts/__pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .mypy_cache/
