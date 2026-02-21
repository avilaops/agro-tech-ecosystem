"""Unit tests for configuration."""

import pytest
import os
from unittest.mock import patch

from precision_intelligence.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_defaults(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.precision_api_url == "http://localhost:5000"
        assert config.intelligence_api_url == "http://localhost:6000"
        assert config.timeout_seconds == 5
        assert config.retry_attempts == 3
        assert config.retry_backoff_multiplier == 1.0
        assert config.retry_backoff_min == 2.0
        assert config.retry_backoff_max == 10.0
        assert config.validate_schemas is True
        assert config.contracts_path == "contracts"
        assert config.log_level == "INFO"
        assert config.log_format == "json"

    def test_env_vars_override(self):
        """Test that environment variables override defaults."""
        env_vars = {
            "PRECISION_INTELLIGENCE_PRECISION_API_URL": "http://custom:5000",
            "PRECISION_INTELLIGENCE_INTELLIGENCE_API_URL": "http://custom:6000",
            "PRECISION_INTELLIGENCE_TIMEOUT_SECONDS": "30",
            "PRECISION_INTELLIGENCE_RETRY_ATTEMPTS": "5",
            "PRECISION_INTELLIGENCE_RETRY_BACKOFF_MULTIPLIER": "2.0",
            "PRECISION_INTELLIGENCE_RETRY_BACKOFF_MIN": "1.0",
            "PRECISION_INTELLIGENCE_RETRY_BACKOFF_MAX": "30.0",
            "PRECISION_INTELLIGENCE_VALIDATE_SCHEMAS": "false",
            "PRECISION_INTELLIGENCE_CONTRACTS_PATH": "custom/contracts",
            "PRECISION_INTELLIGENCE_LOG_LEVEL": "DEBUG",
            "PRECISION_INTELLIGENCE_LOG_FORMAT": "text",
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            
            assert config.precision_api_url == "http://custom:5000"
            assert config.intelligence_api_url == "http://custom:6000"
            assert config.timeout_seconds == 30
            assert config.retry_attempts == 5
            assert config.retry_backoff_multiplier == 2.0
            assert config.retry_backoff_min == 1.0
            assert config.retry_backoff_max == 30.0
            assert config.validate_schemas is False
            assert config.contracts_path == "custom/contracts"
            assert config.log_level == "DEBUG"
            assert config.log_format == "text"

    def test_partial_env_override(self):
        """Test partial environment variable override."""
        env_vars = {
            "PRECISION_INTELLIGENCE_TIMEOUT_SECONDS": "20",
            "PRECISION_INTELLIGENCE_LOG_LEVEL": "WARNING",
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            config = Config()
            
            # Overridden values
            assert config.timeout_seconds == 20
            assert config.log_level == "WARNING"
            
            # Default values (not overridden)
            assert config.precision_api_url == "http://localhost:5000"
            assert config.retry_attempts == 3

    def test_boolean_env_parsing(self):
        """Test boolean environment variable parsing."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("0", False),
            ("no", False),
        ]
        
        for env_value, expected in test_cases:
            env_vars = {"PRECISION_INTELLIGENCE_VALIDATE_SCHEMAS": env_value}
            with patch.dict(os.environ, env_vars):
                config = Config()
                assert config.validate_schemas == expected, f"Failed for '{env_value}'"

    def test_numeric_env_parsing(self):
        """Test numeric environment variable parsing."""
        env_vars = {
            "PRECISION_INTELLIGENCE_TIMEOUT_SECONDS": "15",
            "PRECISION_INTELLIGENCE_RETRY_ATTEMPTS": "7",
            "PRECISION_INTELLIGENCE_RETRY_BACKOFF_MULTIPLIER": "1.5",
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            
            assert isinstance(config.timeout_seconds, int)
            assert config.timeout_seconds == 15
            
            assert isinstance(config.retry_attempts, int)
            assert config.retry_attempts == 7
            
            assert isinstance(config.retry_backoff_multiplier, float)
            assert config.retry_backoff_multiplier == 1.5

    def test_url_normalization(self):
        """Test URL trailing slash handling."""
        test_urls = [
            "http://localhost:5000",
            "http://localhost:5000/",
            "http://api.example.com",
            "http://api.example.com/",
        ]
        
        for url in test_urls:
            env_vars = {"PRECISION_INTELLIGENCE_PRECISION_API_URL": url}
            with patch.dict(os.environ, env_vars):
                config = Config()
                # Note: Client handles trailing slash removal, not config
                assert config.precision_api_url == url

    def test_log_level_values(self):
        """Test various log level values."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            env_vars = {"PRECISION_INTELLIGENCE_LOG_LEVEL": level}
            with patch.dict(os.environ, env_vars):
                config = Config()
                assert config.log_level == level

    def test_log_format_values(self):
        """Test log format values."""
        formats = ["json", "text", "console"]
        
        for fmt in formats:
            env_vars = {"PRECISION_INTELLIGENCE_LOG_FORMAT": fmt}
            with patch.dict(os.environ, env_vars):
                config = Config()
                assert config.log_format == fmt

    def test_contracts_path_relative(self):
        """Test relative contracts path."""
        env_vars = {"PRECISION_INTELLIGENCE_CONTRACTS_PATH": "../contracts"}
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            assert config.contracts_path == "../contracts"

    def test_contracts_path_absolute(self):
        """Test absolute contracts path."""
        env_vars = {"PRECISION_INTELLIGENCE_CONTRACTS_PATH": "/opt/contracts"}
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            assert config.contracts_path == "/opt/contracts"

    def test_retry_backoff_range(self):
        """Test retry backoff min/max range."""
        env_vars = {
            "PRECISION_INTELLIGENCE_RETRY_BACKOFF_MIN": "5.0",
            "PRECISION_INTELLIGENCE_RETRY_BACKOFF_MAX": "60.0",
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            assert config.retry_backoff_min == 5.0
            assert config.retry_backoff_max == 60.0
            assert config.retry_backoff_min < config.retry_backoff_max

    def test_global_config_instance(self):
        """Test that global config instance exists."""
        from precision_intelligence.config import config
        
        assert isinstance(config, Config)
        assert config.precision_api_url is not None

    def test_config_immutability_not_enforced(self):
        """Test that config values can be modified (not a frozen config)."""
        config = Config()
        
        # Should be able to modify
        config.timeout_seconds = 99
        assert config.timeout_seconds == 99
        
        # Note: In production, you might want to use pydantic's frozen=True
        # to make config immutable after initialization

    def test_production_config_example(self):
        """Test a production-like configuration."""
        env_vars = {
            "PRECISION_INTELLIGENCE_PRECISION_API_URL": "https://precision.canaswarm.com",
            "PRECISION_INTELLIGENCE_INTELLIGENCE_API_URL": "https://intelligence.canaswarm.com",
            "PRECISION_INTELLIGENCE_TIMEOUT_SECONDS": "30",
            "PRECISION_INTELLIGENCE_RETRY_ATTEMPTS": "5",
            "PRECISION_INTELLIGENCE_RETRY_BACKOFF_MAX": "60.0",
            "PRECISION_INTELLIGENCE_VALIDATE_SCHEMAS": "true",
            "PRECISION_INTELLIGENCE_LOG_LEVEL": "WARNING",
        }
        
        with patch.dict(os.environ, env_vars):
            config = Config()
            
            assert "https://" in config.precision_api_url
            assert "https://" in config.intelligence_api_url
            assert config.timeout_seconds == 30
            assert config.retry_attempts == 5
            assert config.log_level == "WARNING"
