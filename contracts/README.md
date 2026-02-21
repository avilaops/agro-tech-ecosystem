# Data Contracts - Agro-Tech Ecosystem

This directory contains **JSON Schema** definitions for all data exchanges between systems in the agro-tech ecosystem.

## 📋 Overview

Data contracts ensure **compatibility**, **versioning**, and **validation** across all integrations:

- ✅ **Type Safety**: Validate data before transmission
- ✅ **Documentation**: Self-documenting API contracts
- ✅ **Versioning**: Semantic versioning for breaking changes
- ✅ **Interoperability**: Standard format for all systems

## 📚 Available Contracts

### 1. Precision Agriculture Recommendations
**File**: `precision.recommendations.schema.json`  
**Version**: 1.0.0  
**Producer**: Precision-Agriculture-Platform  
**Consumers**: CanaSwarm-Intelligence, MicroGrid-Manager

Field zone analysis with agronomic recommendations and financial impact estimates.

**Key Fields**:
- `field_id`: Unique field identifier (e.g., F001-UsinaGuarani)
- `zones[]`: Management zones with yield gaps, profitability scores
- `summary`: Aggregated statistics and total financial impact

**Example**:
```json
{
  "field_id": "F001-UsinaGuarani",
  "crop": "Sugarcane",
  "season": "2023/2024",
  "total_area_ha": 150.5,
  "zones": [
    {
      "zone_id": "Z001",
      "area_ha": 45.2,
      "profitability_score": 6.5,
      "status": "warning",
      "recommendation": {
        "action": "consider_reform",
        "priority": "medium"
      }
    }
  ]
}
```

---

### 2. Telemetry Data
**File**: `telemetry.schema.json`  
**Version**: 1.0.0  
**Producers**: AgriBot-Retrofit, CanaSwarm-MicroBot, CanaSwarm-Core  
**Consumers**: CanaSwarm-Swarm-Coordinator, Telemetry, Industrial-Automation-OS

Real-time telemetry from agricultural robots and drones.

**Key Fields**:
- `device_id`: Unique device identifier (e.g., BOT-A001, SWARM-C42A)
- `location`: GPS coordinates, heading, speed
- `battery`: Level, voltage, estimated runtime
- `task`: Current task info (type, progress, field/zone reference)
- `sensors`: Environmental data (soil moisture, temperature, etc.)

**Example**:
```json
{
  "device_id": "BOT-A001",
  "timestamp": "2024-02-20T14:32:18Z",
  "location": {
    "latitude": -22.5678,
    "longitude": -47.4321,
    "heading_degrees": 90,
    "speed_km_h": 2.5
  },
  "battery": {
    "level_percent": 85,
    "estimated_runtime_minutes": 120
  },
  "status": "working",
  "task": {
    "task_id": "TASK-20240220-001",
    "task_type": "harvest",
    "progress_percent": 45,
    "field_id": "F001",
    "zone_id": "Z002"
  }
}
```

---

### 3. Vision Analysis Results
**File**: `vision.analysis.schema.json`  
**Version**: 1.0.0  
**Producers**: AI-Vision-Agriculture, CanaSwarm-Vision  
**Consumers**: CanaSwarm-Intelligence, Precision-Agriculture-Platform

Computer vision analysis results with crop health, pest/disease detection.

**Key Fields**:
- `analysis_id`: Unique analysis identifier (e.g., VIS-20240220143218-A001)
- `source`: Device info (drone, robot, camera)
- `detections`: Crop health, weeds, pests, diseases, deficiencies
- `recommendations`: Automated actions based on detections

**Example**:
```json
{
  "analysis_id": "VIS-20240220143218-A001",
  "timestamp": "2024-02-20T14:32:18Z",
  "source": {
    "device_id": "DRONE-V123",
    "device_type": "drone"
  },
  "location": {
    "field_id": "F001",
    "zone_id": "Z003"
  },
  "detections": {
    "crop_health": {
      "status": "stressed",
      "ndvi": 0.55,
      "confidence": 0.87
    },
    "weeds": [
      {
        "class": "braquiaria",
        "confidence": 0.92,
        "severity": "high",
        "area_m2": 125.5
      }
    ]
  },
  "recommendations": [
    {
      "action": "apply_herbicide",
      "priority": "high",
      "reason": "High-severity weed infestation detected"
    }
  ]
}
```

---

## 🔄 Versioning Policy

We follow **Semantic Versioning** (SemVer) for all contracts:

### Version Format: `MAJOR.MINOR.PATCH`

- **MAJOR** (1.x.x → 2.x.x): Breaking changes
  - Removing required fields
  - Changing field types
  - Renaming fields
  - Changing validation rules (stricter)
  
- **MINOR** (1.0.x → 1.1.x): Backward-compatible additions
  - Adding optional fields
  - Adding new enum values
  - Relaxing validation rules
  
- **PATCH** (1.0.0 → 1.0.1): Documentation/metadata changes
  - Fixing typos in descriptions
  - Adding examples
  - Clarifying documentation

### Breaking Change Policy

**Before introducing breaking changes**:
1. ⚠️ Announce deprecation at least **30 days in advance**
2. 📢 Create GitHub issue tagged `breaking-change`
3. 📝 Document migration path in `MIGRATION.md`
4. 🔄 Provide both versions during transition period
5. 🧪 Update integration tests

**Transition Period**: Old version supported for **90 days** after new major version release.

---

## ✅ Validation

### Python (Pydantic)
```python
from pydantic import BaseModel, Field
import json

# Load schema
with open("contracts/precision.recommendations.schema.json") as f:
    schema = json.load(f)

# Define Pydantic model
class FieldRecommendations(BaseModel):
    field_id: str = Field(..., pattern=r"^F[0-9]{3}(-[A-Za-z0-9_-]+)?$")
    crop: str
    season: str
    # ... (rest of fields)

# Validate data
data = {"field_id": "F001", "crop": "Sugarcane", ...}
validated = FieldRecommendations(**data)
```

### JavaScript/TypeScript
```typescript
import Ajv from "ajv";
import schema from "./contracts/precision.recommendations.schema.json";

const ajv = new Ajv();
const validate = ajv.compile(schema);

const data = { field_id: "F001", crop: "Sugarcane", ... };
const valid = validate(data);

if (!valid) {
  console.error(validate.errors);
}
```

### JSON Schema CLI
```bash
# Install ajv-cli
npm install -g ajv-cli

# Validate JSON file
ajv validate -s contracts/precision.recommendations.schema.json \
             -d data/sample_field.json
```

---

## 🧪 Testing

All contracts MUST have:
1. **Example data** in the schema (`examples` section)
2. **Unit tests** validating example data
3. **Integration tests** in `../integration/` directory

### Running Contract Tests
```bash
# Python
cd integration
python -m pytest test_contracts.py

# JavaScript
npm test -- contracts
```

---

## 📁 File Naming Convention

```
{domain}.{subdomain}.schema.json          # Current version (symlink)
{domain}.{subdomain}.v{MAJOR}.json         # Major version
{domain}.{subdomain}.v{MAJOR}.{MINOR}.json # Specific version
```

**Examples**:
- `precision.recommendations.schema.json` → symlink to v1
- `precision.recommendations.v1.json` → Latest v1.x.x
- `precision.recommendations.v1.0.json` → Specific v1.0.x
- `precision.recommendations.v2.json` → Latest v2.x.x (future)

---

## 🚀 Usage Guidelines

### For Producers (Data Senders)

1. **Always validate before sending**:
   ```python
   # Validate against schema before API call
   validated_data = FieldRecommendations(**raw_data)
   response = requests.post(API_URL, json=validated_data.dict())
   ```

2. **Include version in API**:
   ```python
   # Add version header
   headers = {"X-Contract-Version": "1.0.0"}
   ```

3. **Never break contracts**:
   - Add optional fields only
   - Create new major version for breaking changes

### For Consumers (Data Receivers)

1. **Validate incoming data**:
   ```python
   try:
       data = FieldRecommendations(**request.json())
   except ValidationError as e:
       return JSONResponse({"error": str(e)}, status_code=400)
   ```

2. **Handle unknown fields gracefully**:
   ```python
   # Pydantic: Allow extra fields
   class Config:
       extra = "allow"  # Don't fail on unknown fields
   ```

3. **Check version compatibility**:
   ```python
   version = request.headers.get("X-Contract-Version", "1.0.0")
   if not is_compatible(version, SUPPORTED_VERSIONS):
       return error_response("Unsupported contract version")
   ```

---

## 📦 Integration with Repos

Each repository should:

1. **Copy relevant schemas** to local `contracts/` directory
2. **Import schemas in code** for validation
3. **Run contract tests** in CI/CD pipeline
4. **Subscribe to breaking change notifications**

### Example: CanaSwarm-Intelligence Setup
```bash
# Copy precision contract (producer)
cp ../agro-tech-ecosystem/contracts/precision.recommendations.schema.json \
   ./contracts/

# Copy telemetry contract (consumer)
cp ../agro-tech-ecosystem/contracts/telemetry.schema.json \
   ./contracts/

# Install validation library
pip install jsonschema pydantic

# Add to requirements.txt
echo "jsonschema>=4.0.0" >> requirements.txt
echo "pydantic>=2.0.0" >> requirements.txt
```

---

## 🔗 References

- **JSON Schema Specification**: https://json-schema.org/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **SemVer Specification**: https://semver.org/
- **OpenAPI 3.1** (uses JSON Schema): https://spec.openapis.org/oas/v3.1.0

---

## 📞 Support

- **Issues**: Open GitHub issue with `data-contract` label
- **Breaking Changes**: Tag maintainers in GitHub Projects
- **Questions**: Ask in `#integrations` Slack channel (when available)

---

## 📝 Changelog

### Version 1.0.0 (2024-02-20)
- ✅ Initial contracts for Precision, Telemetry, Vision
- ✅ Established versioning policy
- ✅ Created integration test framework

---

**Last Updated**: 2024-02-20  
**Maintainers**: @avilaops  
**Status**: ✅ Active
