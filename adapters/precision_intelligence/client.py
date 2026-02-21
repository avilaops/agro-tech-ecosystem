"""Client classes for Precision and Intelligence APIs."""

import requests
from typing import Dict, Any, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import structlog

from .config import config
from .exceptions import (
    ConnectionError as AdapterConnectionError,
    TimeoutError as AdapterTimeoutError,
    APIError,
)
from .validator import SchemaValidator

logger = structlog.get_logger()


class BaseClient:
    """Base client with common HTTP functionality."""
    
    def __init__(
        self,
        base_url: str,
        service_name: str,
        timeout: int = None,
        validate_schemas: bool = None,
    ):
        """
        Initialize base client.
        
        Args:
            base_url: API base URL
            service_name: Service name for logging
            timeout: Request timeout in seconds
            validate_schemas: Whether to validate responses
        """
        self.base_url = base_url.rstrip("/")
        self.service_name = service_name
        self.timeout = timeout or config.timeout_seconds
        self.validate_schemas = (
            validate_schemas 
            if validate_schemas is not None 
            else config.validate_schemas
        )
        self.validator = SchemaValidator() if self.validate_schemas else None
    
    @retry(
        stop=stop_after_attempt(config.retry_attempts),
        wait=wait_exponential(
            multiplier=config.retry_backoff_multiplier,
            min=config.retry_backoff_min,
            max=config.retry_backoff_max,
        ),
        retry=retry_if_exception_type((requests.exceptions.ConnectionError,)),
    )
    def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> requests.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (without base URL)
            **kwargs: Additional arguments for requests.request()
        
        Returns:
            Response object
        
        Raises:
            AdapterConnectionError: If connection fails
            AdapterTimeoutError: If request times out
            APIError: If API returns error status
        """
        url = f"{self.base_url}{path}"
        
        logger.info(
            f"{self.service_name}.request",
            method=method,
            url=url,
            timeout=self.timeout,
        )
        
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs,
            )
            
            logger.info(
                f"{self.service_name}.response",
                method=method,
                url=url,
                status_code=response.status_code,
                duration_ms=response.elapsed.total_seconds() * 1000,
            )
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.ConnectionError as e:
            logger.error(
                f"{self.service_name}.connection_error",
                url=url,
                error=str(e),
            )
            raise AdapterConnectionError(
                service=self.service_name,
                url=url,
                original_error=e,
            )
        
        except requests.exceptions.Timeout as e:
            logger.error(
                f"{self.service_name}.timeout",
                url=url,
                timeout=self.timeout,
            )
            raise AdapterTimeoutError(
                service=self.service_name,
                url=url,
                timeout=self.timeout,
            )
        
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"{self.service_name}.http_error",
                url=url,
                status_code=response.status_code,
                response_text=response.text[:500],
            )
            raise APIError(
                service=self.service_name,
                status_code=response.status_code,
                response_text=response.text,
            )


class PrecisionClient(BaseClient):
    """
    Client for Precision-Agriculture-Platform API.
    
    Provides methods to fetch field recommendations and validate
    against precision.recommendations schema.
    
    Example:
        client = PrecisionClient()
        recommendations = client.get_recommendations("F001")
        print(f"Field: {recommendations['field_id']}")
        print(f"Zones: {len(recommendations['zones'])}")
    """
    
    def __init__(
        self,
        base_url: str = None,
        timeout: int = None,
        validate_schemas: bool = None,
    ):
        """
        Initialize Precision client.
        
        Args:
            base_url: API base URL (defaults to config)
            timeout: Request timeout (defaults to config)
            validate_schemas: Whether to validate (defaults to config)
        """
        super().__init__(
            base_url=base_url or config.precision_api_url,
            service_name="PrecisionAPI",
            timeout=timeout,
            validate_schemas=validate_schemas,
        )
    
    def get_recommendations(self, field_id: str) -> Dict[str, Any]:
        """
        Get field recommendations.
        
        Args:
            field_id: Field identifier (e.g., "F001")
        
        Returns:
            Field recommendations dict matching precision.recommendations schema
        
        Raises:
            AdapterConnectionError: If connection fails
            AdapterTimeoutError: If request times out
            APIError: If API returns error
            ValidationError: If response doesn't match schema
        """
        logger.info(
            "precision.get_recommendations",
            field_id=field_id,
        )
        
        response = self._request(
            method="GET",
            path=f"/api/v1/recommendations",
            params={"field_id": field_id},
        )
        
        data = response.json()
        
        # Validate against schema
        if self.validator:
            self.validator.validate_precision_recommendations(data)
        
        logger.info(
            "precision.get_recommendations.success",
            field_id=data.get("field_id"),
            zones_count=len(data.get("zones", [])),
            total_area_ha=data.get("total_area_ha"),
        )
        
        return data
    
    def list_fields(self) -> Dict[str, Any]:
        """
        List all available fields.
        
        Returns:
            Dict with fields list
        """
        response = self._request(
            method="GET",
            path="/api/v1/fields",
        )
        
        return response.json()
    
    def health_check(self) -> bool:
        """
        Check API health.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = self._request(
                method="GET",
                path="/api/v1/health",
            )
            return response.status_code == 200
        except Exception:
            return False


class IntelligenceClient(BaseClient):
    """
    Client for CanaSwarm-Intelligence API.
    
    Provides methods to ingest recommendations and retrieve decisions.
    
    Example:
        client = IntelligenceClient()
        
        # Ingest recommendations
        result = client.ingest_recommendations(recommendations_data)
        print(f"Priority: {result['priority']}")
        
        # Get decision
        decision = client.get_decision("F001")
        print(f"Total ROI: {decision['total_estimated_roi_brl_year']}")
    """
    
    def __init__(
        self,
        base_url: str = None,
        timeout: int = None,
        validate_schemas: bool = None,
    ):
        """
        Initialize Intelligence client.
        
        Args:
            base_url: API base URL (defaults to config)
            timeout: Request timeout (defaults to config)
            validate_schemas: Whether to validate (defaults to config)
        """
        super().__init__(
            base_url=base_url or config.intelligence_api_url,
            service_name="IntelligenceAPI",
            timeout=timeout,
            validate_schemas=validate_schemas,
        )
    
    def ingest_recommendations(
        self,
        recommendations: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Ingest field recommendations from Precision Platform.
        
        Automatically generates a decision based on the recommendations.
        
        Args:
            recommendations: Field recommendations dict 
                           (from PrecisionClient.get_recommendations)
        
        Returns:
            Ingest result with decision summary
        
        Raises:
            AdapterConnectionError: If connection fails
            AdapterTimeoutError: If request times out
            APIError: If API returns error
        """
        field_id = recommendations.get("field_id", "unknown")
        
        logger.info(
            "intelligence.ingest_recommendations",
            field_id=field_id,
            zones_count=len(recommendations.get("zones", [])),
        )
        
        response = self._request(
            method="POST",
            path="/api/v1/precision/ingest",
            json=recommendations,
            headers={"Content-Type": "application/json"},
        )
        
        data = response.json()
        
        logger.info(
            "intelligence.ingest_recommendations.success",
            field_id=data.get("field_id"),
            priority=data.get("priority"),
            decision_generated=data.get("decision_generated"),
        )
        
        return data
    
    def get_decision(self, field_id: str) -> Dict[str, Any]:
        """
        Get generated decision for field.
        
        Args:
            field_id: Field identifier (e.g., "F001")
        
        Returns:
            Decision dict with priority, zones, next_steps, ROI
        
        Raises:
            AdapterConnectionError: If connection fails
            AdapterTimeoutError: If request times out
            APIError: If API returns error (404 if no decision exists)
        """
        logger.info(
            "intelligence.get_decision",
            field_id=field_id,
        )
        
        response = self._request(
            method="GET",
            path=f"/api/v1/decision",
            params={"field_id": field_id},
        )
        
        data = response.json()
        
        # Basic validation
        if self.validator:
            self.validator.validate_intelligence_decision(data)
        
        logger.info(
            "intelligence.get_decision.success",
            field_id=data.get("field_id"),
            priority=data.get("priority", {}).get("level"),
            priority_score=data.get("priority", {}).get("score"),
            zones_count=len(data.get("zones", [])),
            total_roi=data.get("total_estimated_roi_brl_year"),
        )
        
        return data
    
    def list_fields(self) -> Dict[str, Any]:
        """
        List fields with decisions.
        
        Returns:
            Dict with fields list and summary stats
        """
        response = self._request(
            method="GET",
            path="/api/v1/fields",
        )
        
        return response.json()
    
    def health_check(self) -> bool:
        """
        Check API health.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = self._request(
                method="GET",
                path="/api/v1/health",
            )
            return response.status_code == 200
        except Exception:
            return False


# Convenience function for full flow
def execute_full_flow(field_id: str) -> Dict[str, Any]:
    """
    Execute complete Precision → Intelligence flow.
    
    This is a convenience function that:
    1. Fetches recommendations from Precision
    2. Ingests them into Intelligence
    3. Retrieves the generated decision
    
    Args:
        field_id: Field identifier
    
    Returns:
        Dict with all data:
            - recommendations: From Precision
            - ingest_result: From Intelligence ingest
            - decision: Generated decision
    
    Example:
        result = execute_full_flow("F001")
        print(f"Priority: {result['decision']['priority']['level']}")
        print(f"ROI: {result['decision']['total_estimated_roi_brl_year']}")
    """
    precision = PrecisionClient()
    intelligence = IntelligenceClient()
    
    logger.info("flow.start", field_id=field_id)
    
    # Step 1: Get recommendations
    recommendations = precision.get_recommendations(field_id)
    
    # Step 2: Ingest into intelligence
    ingest_result = intelligence.ingest_recommendations(recommendations)
    
    # Step 3: Get decision
    decision = intelligence.get_decision(field_id)
    
    logger.info("flow.complete", field_id=field_id)
    
    return {
        "recommendations": recommendations,
        "ingest_result": ingest_result,
        "decision": decision,
    }
