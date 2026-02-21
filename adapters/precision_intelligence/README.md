# Precision → Intelligence Adapter

Official Python SDK for integrating **Precision-Agriculture-Platform** with **CanaSwarm-Intelligence**.

## Features

- **Type-safe clients** for both APIs
- **Automatic schema validation** against data contracts
- **Retry logic** with exponential backoff
- **Structured logging** (JSON format)
- **Custom exceptions** with context
- **Configuration via environment variables**
- **Health check methods**
- **Convenience function** for complete flow execution

## Installation

```bash
# From project root
pip install -e ./adapters/precision_intelligence

# Or with dependencies
pip install requests pydantic-settings jsonschema tenacity structlog
```

## Quick Start

```python
from precision_intelligence import PrecisionClient, IntelligenceClient

# Initialize clients
precision = PrecisionClient()
intelligence = IntelligenceClient()

# Get recommendations from Precision
recommendations = precision.get_recommendations("F001")

# Ingest into Intelligence
result = intelligence.ingest_recommendations(recommendations)
print(f"Priority: {result['priority']}")

# Get generated decision
decision = intelligence.get_decision("F001")
print(f"ROI: {decision['total_estimated_roi_brl_year']:,.2f} BRL/year")
```

### Full Flow (One-Liner)

```python
from precision_intelligence import execute_full_flow

result = execute_full_flow("F001")
print(result["decision"]["priority"]["level"])  # HIGH, MEDIUM, LOW
```

## Configuration

Configure via environment variables with `PRECISION_INTELLIGENCE_` prefix:

```bash
# API URLs
export PRECISION_INTELLIGENCE_PRECISION_API_URL=http://localhost:5000
export PRECISION_INTELLIGENCE_INTELLIGENCE_API_URL=http://localhost:6000

# Timeouts
export PRECISION_INTELLIGENCE_TIMEOUT_SECONDS=5

# Retry logic
export PRECISION_INTELLIGENCE_RETRY_ATTEMPTS=3
export PRECISION_INTELLIGENCE_RETRY_BACKOFF_MULTIPLIER=1.0
export PRECISION_INTELLIGENCE_RETRY_BACKOFF_MIN=2.0
export PRECISION_INTELLIGENCE_RETRY_BACKOFF_MAX=10.0

# Schema validation (set to false to disable)
export PRECISION_INTELLIGENCE_VALIDATE_SCHEMAS=true
export PRECISION_INTELLIGENCE_CONTRACTS_PATH=contracts

# Logging
export PRECISION_INTELLIGENCE_LOG_LEVEL=INFO
export PRECISION_INTELLIGENCE_LOG_FORMAT=json
```

Or create a `.env` file:

```ini
PRECISION_INTELLIGENCE_PRECISION_API_URL=http://localhost:5000
PRECISION_INTELLIGENCE_INTELLIGENCE_API_URL=http://localhost:6000
PRECISION_INTELLIGENCE_TIMEOUT_SECONDS=10
PRECISION_INTELLIGENCE_RETRY_ATTEMPTS=5
PRECISION_INTELLIGENCE_VALIDATE_SCHEMAS=true
PRECISION_INTELLIGENCE_LOG_LEVEL=DEBUG
```

## Usage

### PrecisionClient

```python
from precision_intelligence import PrecisionClient

client = PrecisionClient()

# Get recommendations for a field
recommendations = client.get_recommendations("F001")
print(f"Field: {recommendations['field_id']}")
print(f"Zones: {len(recommendations['zones'])}")

# List all fields
fields = client.list_fields()
print(f"Available fields: {fields['fields']}")

# Health check
if client.health_check():
    print("Precision API is healthy")
```

### IntelligenceClient

```python
from precision_intelligence import IntelligenceClient

client = IntelligenceClient()

# Ingest recommendations (auto-generates decision)
result = client.ingest_recommendations(recommendations)
print(f"Priority: {result['priority']}")
print(f"Decision generated: {result['decision_generated']}")

# Get decision
decision = client.get_decision("F001")
print(f"Priority: {decision['priority']['level']} ({decision['priority']['score']})")
print(f"Total ROI: {decision['total_estimated_roi_brl_year']:,.2f} BRL/year")

# List fields with decisions
fields = client.list_fields()
print(f"Fields with decisions: {fields['total_fields']}")

# Health check
if client.health_check():
    print("Intelligence API is healthy")
```

### Custom Configuration

```python
from precision_intelligence import PrecisionClient, IntelligenceClient

# Custom URLs and timeouts
precision = PrecisionClient(
    base_url="http://production-precision.example.com",
    timeout=30,
    validate_schemas=False,  # Disable validation for performance
)

intelligence = IntelligenceClient(
    base_url="http://production-intelligence.example.com",
    timeout=30,
)

recommendations = precision.get_recommendations("F999")
result = intelligence.ingest_recommendations(recommendations)
```

## Error Handling

The adapter provides custom exceptions with contextual information:

```python
from precision_intelligence import (
    PrecisionClient,
    AdapterError,
    ConnectionError,
    ValidationError,
    TimeoutError,
    APIError,
)

client = PrecisionClient()

try:
    recommendations = client.get_recommendations("F001")
except ConnectionError as e:
    print(f"Failed to connect to {e.service}: {e.url}")
    print(f"Original error: {e.original_error}")
except TimeoutError as e:
    print(f"Request to {e.service} timed out after {e.timeout}s")
except ValidationError as e:
    print(f"Schema validation failed for {e.schema}:")
    for error in e.errors:
        print(f"  - {error}")
except APIError as e:
    print(f"API returned error {e.status_code}: {e.response_text}")
except AdapterError as e:
    print(f"Generic adapter error: {e}")
```

## Schema Validation

By default, responses are validated against JSON schemas in `contracts/`:

- **Precision**: `contracts/precision.recommendations.schema.json`
- **Intelligence**: `contracts/intelligence.decision.schema.json`

```python
from precision_intelligence import SchemaValidator, ValidationError

validator = SchemaValidator(contracts_path="contracts")

try:
    validator.validate_precision_recommendations(data)
    print("✅ Data is valid")
except ValidationError as e:
    print(f"❌ Validation failed:")
    for error in e.errors:
        print(f"  - {error}")
```

Disable validation for performance (after initial testing):

```bash
export PRECISION_INTELLIGENCE_VALIDATE_SCHEMAS=false
```

## Logging

The adapter uses structured logging (JSON format by default):

```python
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)

# Now all adapter operations will log structured JSON
client = PrecisionClient()
recommendations = client.get_recommendations("F001")

# Example log output:
# {
#   "event": "PrecisionAPI.request",
#   "method": "GET",
#   "url": "http://localhost:5000/api/v1/recommendations",
#   "timeout": 5,
#   "timestamp": "2026-06-01T10:30:00.123456Z",
#   "level": "info"
# }
# {
#   "event": "PrecisionAPI.response",
#   "method": "GET",
#   "url": "http://localhost:5000/api/v1/recommendations",
#   "status_code": 200,
#   "duration_ms": 127.45,
#   "timestamp": "2026-06-01T10:30:00.251234Z",
#   "level": "info"
# }
```

## Retry Logic

The adapter automatically retries failed requests with exponential backoff:

- **Default attempts**: 3
- **Backoff multiplier**: 1.0
- **Min wait**: 2 seconds
- **Max wait**: 10 seconds

Only **connection errors** are retried (not HTTP errors like 404, 500).

```python
# Configure retry behavior
export PRECISION_INTELLIGENCE_RETRY_ATTEMPTS=5
export PRECISION_INTELLIGENCE_RETRY_BACKOFF_MIN=1.0
export PRECISION_INTELLIGENCE_RETRY_BACKOFF_MAX=30.0
```

## Testing

See `tests/` directory for examples:

```bash
# Run all tests
pytest adapters/precision_intelligence/tests/

# Run with coverage
pytest --cov=precision_intelligence tests/

# Run specific test
pytest tests/test_client.py::test_precision_get_recommendations
```

## Integration with E2E Tests

The adapter can replace direct `requests` calls in integration tests:

```python
# Before (direct requests)
import requests
response = requests.get("http://localhost:5000/api/v1/recommendations?field_id=F001")
data = response.json()

# After (using adapter)
from precision_intelligence import PrecisionClient
client = PrecisionClient()
data = client.get_recommendations("F001")
```

## Architecture

```
precision_intelligence/
├── __init__.py          # Public API exports
├── client.py            # PrecisionClient + IntelligenceClient
├── config.py            # Pydantic Settings configuration
├── exceptions.py        # Custom exception hierarchy
├── validator.py         # JSON Schema validation
├── tests/               # Unit tests
│   ├── test_client.py
│   ├── test_validator.py
│   └── test_config.py
└── README.md            # This file
```

## Development

### Adding New Endpoints

1. Add method to `PrecisionClient` or `IntelligenceClient`:

```python
def get_field_history(self, field_id: str, days: int = 30) -> Dict[str, Any]:
    """Get field history."""
    response = self._request(
        method="GET",
        path="/api/v1/history",
        params={"field_id": field_id, "days": days},
    )
    return response.json()
```

2. Add corresponding test in `tests/test_client.py`

3. Update this README with usage example

### Debugging

Enable DEBUG logging to see all requests/responses:

```bash
export PRECISION_INTELLIGENCE_LOG_LEVEL=DEBUG
```

Or programmatically:

```python
import structlog
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
)
```

## Troubleshooting

### Connection Refused

```
ConnectionError: Failed to connect to PrecisionAPI at http://localhost:5000/api/v1/recommendations
```

**Solution**: Ensure APIs are running:

```bash
# Terminal 1
cd Precision-Agriculture-Platform
python app.py

# Terminal 2
cd CanaSwarm-Intelligence
python app.py
```

### Schema Validation Failed

```
ValidationError: Schema validation failed for precision.recommendations
```

**Solution**: Check API response matches schema in `contracts/`. Disable validation temporarily:

```python
client = PrecisionClient(validate_schemas=False)
```

### Timeout Errors

```
TimeoutError: Request to PrecisionAPI timed out after 5 seconds
```

**Solution**: Increase timeout:

```bash
export PRECISION_INTELLIGENCE_TIMEOUT_SECONDS=30
```

Or in code:

```python
client = PrecisionClient(timeout=30)
```

## Related Documentation

- [Data Contracts](../../contracts/README.md) - JSON schemas for APIs
- [Integration Tests](../../integration/README.md) - E2E testing guide
- [Precision API](../../Precision-Agriculture-Platform/README.md) - Source API
- [Intelligence API](../../CanaSwarm-Intelligence/README.md) - Target API

## Contributing

When adding features:

1. Update clients in `client.py`
2. Add tests in `tests/`
3. Update this README
4. Validate schemas in `contracts/`
5. Test with E2E integration

## License

Proprietary - CanaSwarm Ecosystem
