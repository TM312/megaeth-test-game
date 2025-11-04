"""
Tests for configuration management
"""

import os
from unittest.mock import patch

from config import Config


class TestConfig:
    """Test suite for configuration management"""

    # region Default Values Tests

    def test_config_defaults(self):
        """Test config defaults when no environment variables are set"""
        # Clear any existing env vars for clean test
        with patch.dict(os.environ, {}, clear=True):
            # Force reload of config by reimporting
            import importlib
            import config

            importlib.reload(config)
            from config import Config

            assert Config.PRIVATE_KEY is None  # No env var set
            assert Config.RPC_URL == "https://carrot.megaeth.com/rpc"
            assert Config.DEBUG is False
            assert Config.LOG_LEVEL == "INFO"

    # endregion

    # region Environment Variable Loading Tests

    @patch.dict(
        os.environ,
        {
            "PRIVATE_KEY": "test_private_key_123",
            "RPC_URL": "https://custom.rpc.url",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG",
        },
        clear=True,
    )
    def test_config_with_env_vars(self):
        """Test config loads environment variables correctly"""
        # Force reload of config
        import importlib
        import config

        importlib.reload(config)
        from config import Config

        assert Config.PRIVATE_KEY == "test_private_key_123"
        assert Config.RPC_URL == "https://custom.rpc.url"
        assert Config.DEBUG is True
        assert Config.LOG_LEVEL == "DEBUG"

    @patch.dict(os.environ, {"DEBUG": "True"}, clear=True)  # Test case insensitivity
    def test_config_debug_case_insensitive(self):
        """Test DEBUG env var is case insensitive"""
        import importlib
        import config

        importlib.reload(config)
        from config import Config

        assert Config.DEBUG is True

    @patch.dict(os.environ, {"DEBUG": "false"}, clear=True)  # Test lowercase false
    def test_config_debug_false_values(self):
        """Test DEBUG env var handles false values correctly"""
        import importlib
        import config

        importlib.reload(config)
        from config import Config

        assert Config.DEBUG is False

    # endregion

    # region Validation Tests

    def test_validate_config_no_private_key(self):
        """Test config validation warns about missing private key"""
        warnings = Config.validate_config()
        assert len(warnings) >= 1
        assert any(
            "PRIVATE_KEY" in w and "blockchain features will not work" in w
            for w in warnings
        )

    @patch.dict(os.environ, {"PRIVATE_KEY": "some_key"}, clear=True)
    def test_validate_config_with_private_key(self):
        """Test config validation passes with private key present"""
        import importlib
        import config

        importlib.reload(config)
        from config import Config

        warnings = Config.validate_config()
        # Should not warn about missing private key
        assert not any("PRIVATE_KEY" in w for w in warnings)

    # endregion

    # region Warning Display Tests

    def test_print_warnings_no_warnings(self):
        """Test print_warnings handles empty warning list"""
        with patch("builtins.print") as mock_print:
            Config.print_warnings()
            # Should still print something due to missing PRIVATE_KEY
            mock_print.assert_called()

    # endregion
