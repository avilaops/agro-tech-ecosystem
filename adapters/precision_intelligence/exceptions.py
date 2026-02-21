"""Custom exceptions for Precision-Intelligence adapter."""


class AdapterError(Exception):
    """Base exception for all adapter errors."""
    pass


class ConnectionError(AdapterError):
    """Raised when unable to connect to API."""
    
    def __init__(self, service: str, url: str, original_error: Exception = None):
        self.service = service
        self.url = url
        self.original_error = original_error
        message = f"Failed to connect to {service} at {url}"
        if original_error:
            message += f": {str(original_error)}"
        super().__init__(message)


class ValidationError(AdapterError):
    """Raised when data fails schema validation."""
    
    def __init__(self, schema: str, errors: list, data: dict = None):
        self.schema = schema
        self.errors = errors
        self.data = data
        message = f"Data validation failed against schema '{schema}'"
        if errors:
            message += f": {errors}"
        super().__init__(message)


class TimeoutError(AdapterError):
    """Raised when request exceeds timeout."""
    
    def __init__(self, service: str, url: str, timeout: float):
        self.service = service
        self.url = url
        self.timeout = timeout
        super().__init__(
            f"Request to {service} at {url} timed out after {timeout}s"
        )


class APIError(AdapterError):
    """Raised when API returns error response."""
    
    def __init__(self, service: str, status_code: int, response_text: str):
        self.service = service
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(
            f"{service} API error {status_code}: {response_text}"
        )
