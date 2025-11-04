"""
Configuration management for the Snake game
"""

import os
from dotenv import load_dotenv


# Load environment variables once at module import
load_dotenv()


class Config:
    """Centralized configuration for the application"""

    # Blockchain Configuration
    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    RPC_URL = os.getenv("RPC_URL", "https://carrot.megaeth.com/rpc")

    # Debug/Development
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate_config(cls) -> list[str]:
        """Validate configuration and return list of warnings/errors"""
        warnings = []

        if not cls.PRIVATE_KEY:
            warnings.append("No PRIVATE_KEY found - blockchain features will not work")

        return warnings

    @classmethod
    def print_warnings(cls):
        """Print configuration warnings if any exist"""
        warnings = cls.validate_config()
        if warnings:
            print("Configuration warnings:")
            for warning in warnings:
                print(f"  - {warning}")


# Print warnings on import (but don't execute complex logic)
Config.print_warnings()

# Export commonly used config values for easy importing
PRIVATE_KEY = Config.PRIVATE_KEY
RPC_URL = Config.RPC_URL
DEBUG = Config.DEBUG
