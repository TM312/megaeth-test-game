"""
Tests for configuration management
"""

import importlib
import os
import sys
from unittest.mock import patch

import pytest


@pytest.fixture
def clean_config_module():
    """Fixture to ensure clean config module state between tests"""
    # Remove config from sys.modules if it exists
    if "config" in sys.modules:
        del sys.modules["config"]
    yield
    # Cleanup after test
    if "config" in sys.modules:
        del sys.modules["config"]


@pytest.fixture
def clean_environment():
    """Fixture to provide clean environment variables"""
    original_env = os.environ.copy()
    os.environ.clear()
    yield
    os.environ.update(original_env)


def reload_config():
    """Helper function to reload config module and return Config class"""
    # Remove config from sys.modules if it exists
    if "config" in sys.modules:
        del sys.modules["config"]

    with patch("dotenv.load_dotenv"):
        import config

        importlib.reload(config)
        from config import Config

        return Config


class TestConfig:
    """Test suite for configuration management"""

    # region Default Values Tests

    def test_config_defaults(self, clean_environment):
        """Test config defaults when no environment variables are set"""
        config = reload_config()

        assert config.PRIVATE_KEY is None
        assert config.RPC_URL == "https://carrot.megaeth.com/rpc"
        assert config.DEBUG is False
        assert config.LOG_LEVEL == "INFO"

    # endregion

    # region Environment Variable Loading Tests

    def test_config_with_env_vars(self, clean_environment):
        """Test config loads environment variables correctly"""
        # Set environment variables
        os.environ.update(
            {
                "PRIVATE_KEY": "test_private_key_123",
                "RPC_URL": "https://custom.rpc.url",
                "DEBUG": "true",
                "LOG_LEVEL": "DEBUG",
            }
        )

        config = reload_config()

        assert config.PRIVATE_KEY == "test_private_key_123"
        assert config.RPC_URL == "https://custom.rpc.url"
        assert config.DEBUG is True
        assert config.LOG_LEVEL == "DEBUG"

    @pytest.mark.parametrize(
        "debug_value,expected",
        [
            ("True", True),  # Case insensitivity
            ("true", True),  # Lowercase
            ("TRUE", True),  # Uppercase
            ("false", False),  # Lowercase false
            ("False", False),  # Mixed case false
            ("FALSE", False),  # Uppercase false
            ("", False),  # Empty string
            ("anything_else", False),  # Non-boolean string
        ],
    )
    def test_config_debug_values(self, clean_environment, debug_value, expected):
        """Test DEBUG env var handles various values correctly"""
        os.environ["DEBUG"] = debug_value

        config = reload_config()

        assert config.DEBUG is expected

    # endregion

    # region Validation Tests

    def test_validate_config_no_private_key(self, clean_environment):
        """Test config validation warns about missing private key"""
        config = reload_config()

        warnings = config.validate_config()
        assert len(warnings) >= 1
        assert any(
            "PRIVATE_KEY" in w and "blockchain features will not work" in w
            for w in warnings
        )

    def test_validate_config_with_private_key(self, clean_environment):
        """Test config validation passes with private key present"""
        os.environ["PRIVATE_KEY"] = "some_key"

        config = reload_config()

        warnings = config.validate_config()
        # Should not warn about missing private key
        assert not any("PRIVATE_KEY" in w for w in warnings)

    # endregion

    # region Warning Display Tests

    def test_print_warnings_with_warnings(self, clean_environment):
        """Test print_warnings displays warnings when they exist"""
        config = reload_config()

        with patch("builtins.print") as mock_print:
            config.print_warnings()
            # Should print warnings due to missing PRIVATE_KEY
            mock_print.assert_called()

    def test_print_warnings_no_warnings(self, clean_environment):
        """Test print_warnings does nothing when no warnings exist"""
        os.environ["PRIVATE_KEY"] = "some_key"

        config = reload_config()

        with patch("builtins.print") as mock_print:
            config.print_warnings()
            # Should not print anything when no warnings
            mock_print.assert_not_called()

    # endregion
