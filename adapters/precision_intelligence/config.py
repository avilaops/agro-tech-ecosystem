"""Configuration management for Precision-Intelligence adapter."""

from pydantic_settings import BaseSettings
from typing import Optional


class Config(BaseSettings):
    """
    Configuration for Precision-Intelligence adapter.
    
    All settings can be overridden via environment variables with 
    PRECISION_INTELLIGENCE_ prefix.
    
    Example:
        export PRECISION_INTELLIGENCE_PRECISION_API_URL="http://prod.example.com:5000"
    """
    
    # API URLs
    precision_api_url: str = "http://localhost:5000"
    intelligence_api_url: str = "http://localhost:6000"
    
    # Request settings
    timeout_seconds: int = 5
    retry_attempts: int = 3
    retry_backoff_multiplier: float = 1.0
    retry_backoff_min: float = 2.0
    retry_backoff_max: float = 10.0
    
    # Validation
    validate_schemas: bool = True
    contracts_path: str = "contracts"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "console"
    
    class Config:
        env_prefix = "PRECISION_INTELLIGENCE_"
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global config instance
config = Config()
