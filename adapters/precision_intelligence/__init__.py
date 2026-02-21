"""
Precision → Intelligence Adapter Package

Official client library for integrating Precision-Agriculture-Platform
with CanaSwarm-Intelligence decision support system.

This package provides:
- Type-safe clients with Pydantic models
- Automatic schema validation
- Retry logic for transient failures
- Structured logging
- Configuration via environment variables

Usage:
    from adapters.precision_intelligence import PrecisionClient, IntelligenceClient
    
    precision = PrecisionClient()
    intelligence = IntelligenceClient()
    
    # Get recommendations
    recommendations = precision.get_recommendations(field_id="F001")
    
    # Send to intelligence
    result = intelligence.ingest_recommendations(recommendations)
    
    # Get decision
    decision = intelligence.get_decision(field_id="F001")
"""

from .client import PrecisionClient, IntelligenceClient, execute_full_flow
from .exceptions import (
    AdapterError,
    ConnectionError,
    ValidationError,
    TimeoutError,
    APIError,
)
from .config import Config
from .validator import SchemaValidator

__version__ = "1.0.0"

__all__ = [
    "PrecisionClient",
    "IntelligenceClient",
    "execute_full_flow",
    "AdapterError",
    "ConnectionError",
    "ValidationError",
    "TimeoutError",
    "APIError",
    "Config",
    "SchemaValidator",
]
