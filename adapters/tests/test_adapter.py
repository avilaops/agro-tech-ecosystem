"""
Unit tests for Precision-Intelligence adapter.

Run: python -m pytest adapters/tests/test_adapter.py
"""

import pytest
from unittest.mock import Mock, patch
import requests

from adapters.precision_intelligence import (
    PrecisionClient,
    IntelligenceClient,
    AdapterConfig,
    APIConnectionError,
    APIResponseError,
    InvalidSchemaError,
    SchemaValidator,
)


# Mock data
MOCK_RECOMMENDATIONS = {
    "field_id": "F001",
    "crop": "Sugarcane",
    "season": "2023/2024",
    "total_area_ha": 150.5,
    "zones": [
        {
            "zone_id": "Z001",
            "area_ha": 45.2,
            "profitability_score": 6.5,
            "status": "warning",
            "recommendation": "reform",
            "financial_impact": {
                "estimated_impact_brl_year": 120000,
                "confidence": 0.85
            }
        }
    ],
    "summary": {
        "total_zones": 1,
        "avg_profitability_score": 6.5,
        "total_estimated_impact_brl": 120000
    }
}

MOCK_INGEST_RESULT = {
    "field_id": "F001",
    "zones_analyzed": 1,
    "priority": "high",
    "estimated_roi_brl_year": 120000,
    "decision_generated": True
}

MOCK_DECISION = {
    "field_id": "F001",
    "priority": {
        "level": "high",
        "score": 7.5,
        "reason": "1 warning zone requires attention"
    },
    "zones": [
        {
            "zone_id": "Z001",
            "current_status": "warning",
            "action": {
                "action": "reform",
                "priority": "high",
                "estimated_roi_brl_year": 120000
            }
        }
    ],
    "total_estimated_roi_brl_year": 120000,
    "next_steps": [
        "Schedule soil analysis",
        "Request reform quotes"
    ]
}


class TestPrecisionClient:
    """Test PrecisionClient class."""
    
    def test_init_with_default_config(self):
        """Test initialization with default config."""
        client = PrecisionClient()
        assert client.base_url == "http://localhost:5000"
        assert client.timeout == 5
    
    def test_init_with_custom_config(self):
        """Test initialization with custom config."""
        config = AdapterConfig(
            precision_api_url="http://custom:8000",
            timeout_seconds=10
        )
        client = PrecisionClient(config=config)
        assert client.base_url == "http://custom:8000"
        assert client.timeout == 10
    
    @patch('adapters.precision_intelligence.client.requests.request')
    def test_get_recommendations_success(self, mock_request):
        """Test successful get_recommendations call."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_RECOMMENDATIONS
        mock_request.return_value = mock_response
        
        # Make request
        client = PrecisionClient()
        result = client.get_recommendations("F001", validate_schema=False)
        
        # Verify
        assert result == MOCK_RECOMMENDATIONS
        assert result['field_id'] == "F001"
        mock_request.assert_called_once()
    
    @patch('adapters.precision_intelligence.client.requests.request')
    def test_get_recommendations_connection_error(self, mock_request):
        """Test connection error handling."""
        mock_request.side_effect = requests.exceptions.ConnectionError()
        
        client = PrecisionClient()
        with pytest.raises(APIConnectionError) as exc_info:
            client.get_recommendations("F001")
        
        assert "Cannot connect" in str(exc_info.value)
    
    @patch('adapters.precision_intelligence.client.requests.request')
    def test_get_recommendations_http_error(self, mock_request):
        """Test HTTP error handling."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_request.return_value = mock_response
        
        client = PrecisionClient()
        with pytest.raises(APIResponseError) as exc_info:
            client.get_recommendations("F001")
        
        assert exc_info.value.status_code == 404


class TestIntelligenceClient:
    """Test IntelligenceClient class."""
    
    def test_init_with_default_config(self):
        """Test initialization with default config."""
        client = IntelligenceClient()
        assert client.base_url == "http://localhost:6000"
        assert client.timeout == 5
    
    @patch('adapters.precision_intelligence.client.requests.request')
    def test_ingest_recommendations_success(self, mock_request):
        """Test successful ingest_recommendations call."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_INGEST_RESULT
        mock_request.return_value = mock_response
        
        # Make request
        client = IntelligenceClient()
        result = client.ingest_recommendations(MOCK_RECOMMENDATIONS)
        
        # Verify
        assert result == MOCK_INGEST_RESULT
        assert result['field_id'] == "F001"
        assert result['decision_generated'] is True
    
    @patch('adapters.precision_intelligence.client.requests.request')
    def test_get_decision_success(self, mock_request):
        """Test successful get_decision call."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_DECISION
        mock_request.return_value = mock_response
        
        # Make request
        client = IntelligenceClient()
        result = client.get_decision("F001")
        
        # Verify
        assert result == MOCK_DECISION
        assert result['field_id'] == "F001"
        assert result['priority']['level'] == "high"
        assert len(result['next_steps']) > 0


class TestSchemaValidator:
    """Test SchemaValidator class."""
    
    def test_validate_valid_data(self):
        """Test validation of valid data."""
        validator = SchemaValidator()
        
        # Should not raise
        is_valid = validator.validate(MOCK_RECOMMENDATIONS)
        assert is_valid is True
    
    def test_validate_invalid_data(self):
        """Test validation of invalid data."""
        validator = SchemaValidator()
        
        invalid_data = {"field_id": "F001"}  # Missing required fields
        
        with pytest.raises(InvalidSchemaError):
            validator.validate(invalid_data)
    
    def test_validate_safe_valid(self):
        """Test safe validation with valid data."""
        validator = SchemaValidator()
        
        is_valid, error = validator.validate_safe(MOCK_RECOMMENDATIONS)
        assert is_valid is True
        assert error is None
    
    def test_validate_safe_invalid(self):
        """Test safe validation with invalid data."""
        validator = SchemaValidator()
        
        invalid_data = {"field_id": "F001"}
        is_valid, error = validator.validate_safe(invalid_data)
        assert is_valid is False
        assert error is not None
        assert "required" in error.lower()


class TestAdapterConfig:
    """Test AdapterConfig class."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = AdapterConfig()
        assert config.precision_api_url == "http://localhost:5000"
        assert config.intelligence_api_url == "http://localhost:6000"
        assert config.timeout_seconds == 5
        assert config.retry_attempts == 3
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = AdapterConfig(
            precision_api_url="http://prod:5000",
            intelligence_api_url="http://prod:6000",
            timeout_seconds=10,
            retry_attempts=5,
        )
        assert config.precision_api_url == "http://prod:5000"
        assert config.intelligence_api_url == "http://prod:6000"
        assert config.timeout_seconds == 10
        assert config.retry_attempts == 5
    
    @patch.dict('os.environ', {
        'PRECISION_API_URL': 'http://env:5000',
        'INTELLIGENCE_API_URL': 'http://env:6000',
        'ADAPTER_TIMEOUT_SECONDS': '15',
        'ADAPTER_RETRY_ATTEMPTS': '7',
    })
    def test_env_vars(self):
        """Test configuration from environment variables."""
        config = AdapterConfig()
        assert config.precision_api_url == "http://env:5000"
        assert config.intelligence_api_url == "http://env:6000"
        assert config.timeout_seconds == 15
        assert config.retry_attempts == 7
