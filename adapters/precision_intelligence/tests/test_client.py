"""Unit tests for client classes."""

import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
import json

from precision_intelligence import (
    PrecisionClient,
    IntelligenceClient,
    execute_full_flow,
    ConnectionError,
    TimeoutError,
    APIError,
    ValidationError,
)


# Sample test data
SAMPLE_RECOMMENDATIONS = {
    "field_id": "F001",
    "timestamp": "2026-06-01T10:00:00Z",
    "total_area_ha": 120.5,
    "zones": [
        {
            "zone_id": "Z1",
            "coordinates": [[0, 0], [10, 0], [10, 10], [0, 10]],
            "area_ha": 40.0,
            "issue_type": "nutrient_deficiency",
            "severity": "high",
            "recommendation": {
                "action": "fertilize",
                "npk_ratio": "10-20-10",
                "quantity_kg_ha": 250.0,
                "estimated_cost_brl_ha": 180.0,
            },
        }
    ],
}

SAMPLE_INGEST_RESULT = {
    "field_id": "F001",
    "priority": "HIGH",
    "zones_analyzed": 3,
    "decision_generated": True,
}

SAMPLE_DECISION = {
    "field_id": "F001",
    "priority": {"level": "HIGH", "score": 0.87},
    "zones": [
        {
            "zone_id": "Z1",
            "priority_score": 0.87,
            "selected_action": "fertilize",
            "estimated_roi_brl_year": 12500.0,
        }
    ],
    "next_steps": ["Step 1", "Step 2"],
    "total_estimated_roi_brl_year": 12500.0,
}


class TestPrecisionClient:
    """Tests for PrecisionClient."""

    def test_init_defaults(self):
        """Test client initialization with defaults."""
        client = PrecisionClient()
        assert client.base_url == "http://localhost:5000"
        assert client.service_name == "PrecisionAPI"
        assert client.timeout == 5

    def test_init_custom(self):
        """Test client initialization with custom values."""
        client = PrecisionClient(
            base_url="http://custom:8000",
            timeout=30,
            validate_schemas=False,
        )
        assert client.base_url == "http://custom:8000"
        assert client.timeout == 30
        assert client.validate_schemas is False

    @patch("requests.request")
    def test_get_recommendations_success(self, mock_request):
        """Test successful get_recommendations call."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_RECOMMENDATIONS
        mock_response.elapsed.total_seconds.return_value = 0.127
        mock_request.return_value = mock_response

        client = PrecisionClient(validate_schemas=False)
        result = client.get_recommendations("F001")

        # Assertions
        assert result == SAMPLE_RECOMMENDATIONS
        assert result["field_id"] == "F001"
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["url"] == "http://localhost:5000/api/v1/recommendations"
        assert call_kwargs["params"] == {"field_id": "F001"}

    @patch("requests.request")
    def test_get_recommendations_connection_error(self, mock_request):
        """Test connection error handling."""
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection refused")

        client = PrecisionClient()
        with pytest.raises(ConnectionError) as exc_info:
            client.get_recommendations("F001")

        assert exc_info.value.service == "PrecisionAPI"
        assert "Connection refused" in str(exc_info.value.original_error)

    @patch("requests.request")
    def test_get_recommendations_timeout(self, mock_request):
        """Test timeout error handling."""
        mock_request.side_effect = requests.exceptions.Timeout()

        client = PrecisionClient()
        with pytest.raises(TimeoutError) as exc_info:
            client.get_recommendations("F001")

        assert exc_info.value.service == "PrecisionAPI"
        assert exc_info.value.timeout == 5

    @patch("requests.request")
    def test_get_recommendations_http_error(self, mock_request):
        """Test HTTP error handling."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_request.return_value = mock_response

        client = PrecisionClient()
        with pytest.raises(APIError) as exc_info:
            client.get_recommendations("F001")

        assert exc_info.value.service == "PrecisionAPI"
        assert exc_info.value.status_code == 500

    @patch("requests.request")
    def test_list_fields(self, mock_request):
        """Test list_fields method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"fields": ["F001", "F002", "F003"]}
        mock_response.elapsed.total_seconds.return_value = 0.050
        mock_request.return_value = mock_response

        client = PrecisionClient()
        result = client.list_fields()

        assert "fields" in result
        assert len(result["fields"]) == 3
        assert "F001" in result["fields"]

    @patch("requests.request")
    def test_health_check_success(self, mock_request):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.010
        mock_request.return_value = mock_response

        client = PrecisionClient()
        assert client.health_check() is True

    @patch("requests.request")
    def test_health_check_failure(self, mock_request):
        """Test failed health check."""
        mock_request.side_effect = requests.exceptions.ConnectionError()

        client = PrecisionClient()
        assert client.health_check() is False


class TestIntelligenceClient:
    """Tests for IntelligenceClient."""

    def test_init_defaults(self):
        """Test client initialization with defaults."""
        client = IntelligenceClient()
        assert client.base_url == "http://localhost:6000"
        assert client.service_name == "IntelligenceAPI"
        assert client.timeout == 5

    def test_init_custom(self):
        """Test client initialization with custom values."""
        client = IntelligenceClient(
            base_url="http://custom:9000",
            timeout=20,
            validate_schemas=False,
        )
        assert client.base_url == "http://custom:9000"
        assert client.timeout == 20
        assert client.validate_schemas is False

    @patch("requests.request")
    def test_ingest_recommendations_success(self, mock_request):
        """Test successful ingest_recommendations call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_INGEST_RESULT
        mock_response.elapsed.total_seconds.return_value = 0.234
        mock_request.return_value = mock_response

        client = IntelligenceClient()
        result = client.ingest_recommendations(SAMPLE_RECOMMENDATIONS)

        # Assertions
        assert result == SAMPLE_INGEST_RESULT
        assert result["field_id"] == "F001"
        assert result["decision_generated"] is True
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs["url"] == "http://localhost:6000/api/v1/precision/ingest"
        assert call_kwargs["json"] == SAMPLE_RECOMMENDATIONS

    @patch("requests.request")
    def test_get_decision_success(self, mock_request):
        """Test successful get_decision call."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_DECISION
        mock_response.elapsed.total_seconds.return_value = 0.089
        mock_request.return_value = mock_response

        client = IntelligenceClient(validate_schemas=False)
        result = client.get_decision("F001")

        # Assertions
        assert result == SAMPLE_DECISION
        assert result["field_id"] == "F001"
        assert result["priority"]["level"] == "HIGH"
        assert result["total_estimated_roi_brl_year"] == 12500.0

    @patch("requests.request")
    def test_get_decision_not_found(self, mock_request):
        """Test get_decision with 404 error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Decision not found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_request.return_value = mock_response

        client = IntelligenceClient()
        with pytest.raises(APIError) as exc_info:
            client.get_decision("F999")

        assert exc_info.value.status_code == 404

    @patch("requests.request")
    def test_list_fields(self, mock_request):
        """Test list_fields method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total_fields": 3,
            "fields": ["F001", "F002", "F003"],
        }
        mock_response.elapsed.total_seconds.return_value = 0.045
        mock_request.return_value = mock_response

        client = IntelligenceClient()
        result = client.list_fields()

        assert result["total_fields"] == 3
        assert len(result["fields"]) == 3

    @patch("requests.request")
    def test_health_check_success(self, mock_request):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.008
        mock_request.return_value = mock_response

        client = IntelligenceClient()
        assert client.health_check() is True

    @patch("requests.request")
    def test_health_check_failure(self, mock_request):
        """Test failed health check."""
        mock_request.side_effect = Exception("Network error")

        client = IntelligenceClient()
        assert client.health_check() is False


class TestExecuteFullFlow:
    """Tests for execute_full_flow convenience function."""

    @patch("precision_intelligence.client.IntelligenceClient")
    @patch("precision_intelligence.client.PrecisionClient")
    def test_full_flow_success(self, mock_precision_cls, mock_intelligence_cls):
        """Test successful full flow execution."""
        # Mock PrecisionClient
        mock_precision = Mock()
        mock_precision.get_recommendations.return_value = SAMPLE_RECOMMENDATIONS
        mock_precision_cls.return_value = mock_precision

        # Mock IntelligenceClient
        mock_intelligence = Mock()
        mock_intelligence.ingest_recommendations.return_value = SAMPLE_INGEST_RESULT
        mock_intelligence.get_decision.return_value = SAMPLE_DECISION
        mock_intelligence_cls.return_value = mock_intelligence

        # Execute flow
        result = execute_full_flow("F001")

        # Assertions
        assert "recommendations" in result
        assert "ingest_result" in result
        assert "decision" in result
        assert result["recommendations"] == SAMPLE_RECOMMENDATIONS
        assert result["ingest_result"] == SAMPLE_INGEST_RESULT
        assert result["decision"] == SAMPLE_DECISION

        # Verify call order
        mock_precision.get_recommendations.assert_called_once_with("F001")
        mock_intelligence.ingest_recommendations.assert_called_once_with(
            SAMPLE_RECOMMENDATIONS
        )
        mock_intelligence.get_decision.assert_called_once_with("F001")


class TestRetryLogic:
    """Tests for retry logic."""

    @patch("requests.request")
    def test_retry_on_connection_error(self, mock_request):
        """Test that connection errors are retried."""
        # Fail twice, then succeed
        mock_request.side_effect = [
            requests.exceptions.ConnectionError("Connection refused"),
            requests.exceptions.ConnectionError("Connection refused"),
            Mock(
                status_code=200,
                json=lambda: SAMPLE_RECOMMENDATIONS,
                elapsed=Mock(total_seconds=lambda: 0.3),
            ),
        ]

        client = PrecisionClient(validate_schemas=False)
        result = client.get_recommendations("F001")

        # Should succeed after retries
        assert result == SAMPLE_RECOMMENDATIONS
        assert mock_request.call_count == 3

    @patch("requests.request")
    def test_no_retry_on_http_error(self, mock_request):
        """Test that HTTP errors are NOT retried."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_request.return_value = mock_response

        client = PrecisionClient()
        with pytest.raises(APIError):
            client.get_recommendations("F001")

        # Should only be called once (no retry for HTTP errors)
        assert mock_request.call_count == 1
