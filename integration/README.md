# Integration Tests - Agro-Tech Ecosystem

E2E integration tests validating data flows between ecosystem components.

## 🎯 Purpose

These tests ensure the **entire system works together**, not just as isolated modules. They validate:
- ✅ API compatibility (request/response formats)
- ✅ Data contract compliance (JSON Schema validation)
- ✅ End-to-end workflows (producer → consumer flows)
- ✅ System health (smoke tests for critical paths)

## 📋 Available Tests

### 1. Precision → Intelligence
**File**: `test_precision_to_intelligence.py`  
**Status**: ✅ Active  
**Last Run**: 2026-02-21 (PASSED)

**Data Flow**:
```
Precision-Agriculture-Platform (port 5000)
    → GET /api/v1/recommendations?field_id=F001
    ↓ FieldRecommendations (JSON)
CanaSwarm-Intelligence (port 6000)
    → POST /api/v1/precision/ingest
    → GET /api/v1/decision?field_id=F001
    ↓ FieldDecision (JSON)
✅ Validated
```

**What it tests**:
- Precision API returns valid field recommendations
- Intelligence API ingests recommendations successfully
- Intelligence generates prioritized decisions with ROI
- Complete data flow: zone analysis → decision support

**Example output**:
```
✅ Field F001: 3 zones analyzed
✅ Priority: CRITICAL (score 9.5/10)
✅ Total ROI: R$ 385,000/year
✅ 6 next steps generated
```

---

## 🚀 Running Tests

### Locally

**Prerequisites**:
```bash
# Start Precision API (terminal 1)
cd Precision-Agriculture-Platform
uvicorn src.api:app --host 127.0.0.1 --port 5000

# Start Intelligence API (terminal 2)
cd CanaSwarm-Intelligence
uvicorn src.api:app --host 127.0.0.1 --port 6000

# Run E2E test (terminal 3)
cd agro-tech-ecosystem
python integration/test_precision_to_intelligence.py
```

**Quick test**:
```bash
# From agro-tech-ecosystem root
python integration/test_precision_to_intelligence.py
```

### CI/CD

Tests run automatically via GitHub Actions:
- **Workflow**: `.github/workflows/e2e.yml`
- **Triggers**: Push to main, PRs, every 6 hours (cron), manual dispatch
- **Environment**: Ubuntu latest, Python 3.11
- **Services**: Both APIs started as background processes
- **Artifacts**: Logs uploaded on failure (7-day retention)

**Manual trigger**:
```bash
gh workflow run e2e.yml -R avilaops/agro-tech-ecosystem
```

---

## 📝 Adding New Tests

### Template Structure

```python
"""
End-to-End Integration Test: {Producer} → {Consumer}

This test validates the complete data flow between the two systems.
"""

import requests
import json
import sys


# API Configuration
PRODUCER_API = "http://localhost:{PORT}"
CONSUMER_API = "http://localhost:{PORT}"
TIMEOUT_SECONDS = 5


class IntegrationTest:
    """E2E integration test for {Producer} → {Consumer} flow."""
    
    def __init__(self):
        self.producer_url = PRODUCER_API
        self.consumer_url = CONSUMER_API
        self.results = {
            "producer_api": False,
            "consumer_ingest": False,
            "consumer_process": False,
        }
    
    def run(self) -> bool:
        """Execute end-to-end test."""
        # Step 1: Get data from producer
        data = self._test_producer_api()
        if not data:
            return self._report_failure("Producer API")
        
        # Step 2: Send to consumer
        result = self._test_consumer_ingest(data)
        if not result:
            return self._report_failure("Consumer Ingest")
        
        # Step 3: Verify processing
        processed = self._test_consumer_process()
        if not processed:
            return self._report_failure("Consumer Process")
        
        return self._report_success(data, processed)
    
    # Implement _test_* methods...


def main():
    """Run end-to-end integration test."""
    test = IntegrationTest()
    success = test.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

### Checklist for New Test

1. **Create test file**: `test_{producer}_to_{consumer}.py`
2. **Implement test class**: Use template above
3. **Add to CI workflow**: Update `.github/workflows/e2e.yml`
4. **Document in README**: Add to "Available Tests" section
5. **Validate contract**: Ensure JSON schemas match
6. **Test locally first**: Run both services + test
7. **Verify CI passes**: Check GitHub Actions

### Example: Telemetry → Coordinator Test

```python
# test_telemetry_to_coordinator.py
TELEMETRY_API = "http://localhost:7000"
COORDINATOR_API = "http://localhost:8000"

# Step 1: GET /api/v1/telemetry?device_id=BOT-A001
# Step 2: POST /api/v1/coordinator/robots/BOT-A001/telemetry
# Step 3: GET /api/v1/coordinator/swarm/status
```

---

## 🔍 Contract Validation

All tests should validate against JSON Schemas in `../contracts/`:

```python
import jsonschema

# Load schema
with open("../contracts/precision.recommendations.schema.json") as f:
    schema = json.load(f)

# Validate data
try:
    jsonschema.validate(instance=data, schema=schema)
    print("✅ Data matches contract")
except jsonschema.ValidationError as e:
    print(f"❌ Contract violation: {e.message}")
    return False
```

---

## 📊 Test Reporting

### Success Output
```
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪
E2E INTEGRATION TEST: {Producer} → {Consumer}
🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪🧪

✅ E2E TEST PASSED: Complete data flow working!

Data Flow Summary:
  1. ✅ {Producer} provided data
  2. ✅ {Consumer} ingested successfully
  3. ✅ {Consumer} processed and returned results

🎉 Integration successful
```

### Failure Output
```
❌ E2E TEST FAILED: {Failed Stage}

Test Results:
  ✅ PASS: producer_api
  ❌ FAIL: consumer_ingest

Error: HTTP 400 - Validation error
```

---

## 🐛 Debugging

### Common Issues

**Connection Refused**:
```
❌ ERROR: Cannot connect to {API}
```
**Solution**: Ensure service is running on correct port

**Schema Validation Failed**:
```
❌ ERROR: Validation error on field 'zones'
```
**Solution**: Check contract version compatibility

**Timeout**:
```
❌ ERROR: Request timed out
```
**Solution**: Increase `TIMEOUT_SECONDS` or optimize API

### Logs

When test fails locally:
```bash
# Check API logs
tail -f {service}/access.log
tail -f {service}/error.log
```

In CI, logs are automatically uploaded as artifacts:
```bash
gh run view {RUN_ID} --log
```

---

## 📈 Coverage Goals

### Current Coverage (2026-02-21)
- ✅ Precision → Intelligence (100%)
- ⏳ Telemetry → Coordinator (0%)
- ⏳ Vision → Intelligence (0%)
- ⏳ AgriBot → Telemetry (0%)

### Target Coverage (Q1 2026)
- Precision → Intelligence ✅
- Telemetry → Coordinator 🎯
- Vision → Intelligence 🎯
- AgriBot → Telemetry 🎯
- MicroGrid → Solar Manager 🎯

---

## 🔗 Related Documentation

- **Data Contracts**: `../contracts/README.md`
- **CI/CD Workflows**: `../.github/workflows/e2e.yml`
- **Precision API**: `../../Precision-Agriculture-Platform/README.md`
- **Intelligence API**: `../../CanaSwarm-Intelligence/README.md`

---

## 📞 Support

- **Issues**: Open GitHub issue with `integration-test` label
- **CI Failures**: Check Actions tab, download logs artifact
- **New Test Requests**: Create issue with `test-coverage` label

---

**Last Updated**: 2026-02-21  
**Maintainer**: @avilaops  
**Status**: ✅ Active
