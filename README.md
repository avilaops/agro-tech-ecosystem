# Agro-Tech Ecosystem

**Unified integration repo for CanaSwarm intelligence + precision agriculture services.**

[![E2E Integration Tests](https://github.com/avilaops/agro-tech-ecosystem/actions/workflows/e2e.yml/badge.svg)](https://github.com/avilaops/agro-tech-ecosystem/actions/workflows/e2e.yml)
[![Contract Validation](https://github.com/avilaops/agro-tech-ecosystem/actions/workflows/contracts.yml/badge.svg)](https://github.com/avilaops/agro-tech-ecosystem/actions/workflows/contracts.yml)

## 🎯 Purpose

This repository orchestrates integration testing and data contracts across multiple CanaSwarm services:

- **Precision-Agriculture-Platform**: Field analysis and recommendations
- **CanaSwarm-Intelligence**: Decision support system
- **AI-Vision-Agriculture**: Computer vision for crop monitoring (coming soon)
- **CanaSwarm-Telemetry**: Equipment telemetry (coming soon)

## 📦 Repository Structure

```
agro-tech-ecosystem/
├── adapters/                           # Official SDK clients
│   └── precision_intelligence/         # Precision→Intelligence adapter (97% coverage)
│       ├── client.py                   # PrecisionClient + IntelligenceClient
│       ├── config.py                   # Pydantic Settings
│       ├── exceptions.py               # Custom exceptions
│       ├── validator.py                # Schema validation
│       ├── tests/                      # Unit tests (46/51 passing)
│       └── README.md                   # Full documentation
│
├── contracts/                          # JSON Schema data contracts
│   ├── precision.recommendations.schema.json
│   ├── intelligence.decision.schema.json
│   ├── vision.detection.schema.json
│   └── README.md
│
├── integration/                        # E2E integration tests
│   ├── test_precision_to_intelligence.py
│   └── README.md
│
├── .github/workflows/                  # CI/CD pipelines
│   ├── e2e.yml                         # E2E tests (Docker Compose)
│   └── contracts.yml                   # Schema validation
│
├── docker-compose.e2e.yml              # E2E test environment
├── Makefile                            # Dev commands (Linux/Mac)
└── scripts/
    └── e2e.ps1                         # Dev commands (Windows)
```

## 🚀 Quick Start

### Running E2E Tests

#### Option 1: Docker Compose (Recommended)

```bash
# Linux/Mac
make e2e

# Windows PowerShell
.\scripts\e2e.ps1
```

This will:
1. Build Docker images for Precision + Intelligence APIs
2. Start services with health checks
3. Run E2E integration test
4. Stop and clean up containers

#### Option 2: Manual (Development)

**Terminal 1: Start Precision API**
```bash
cd ../Precision-Agriculture-Platform
python -m uvicorn src.api:app --host 127.0.0.1 --port 5000
```

**Terminal 2: Start Intelligence API**
```bash
cd ../CanaSwarm-Intelligence
python -m uvicorn src.api:app --host 127.0.0.1 --port 6000
```

**Terminal 3: Run E2E Test**
```bash
python integration/test_precision_to_intelligence.py
```

### Working with Services Only

```bash
# Start services (keep running for manual testing)
make e2e-up
# or
.\scripts\e2e.ps1 up

# Services will be available at:
# - Precision API: http://localhost:5000
# - Intelligence API: http://localhost:6000

# Stop services
make e2e-down
# or
.\scripts\e2e.ps1 down
```

### View Logs

```bash
make e2e-logs
# or
.\scripts\e2e.ps1 logs
```

### Clean Everything

```bash
# Removes containers, networks, and images
make e2e-clean
# or
.\scripts\e2e.ps1 clean
```

## 📚 Using the Adapter SDK

### Installation

```bash
cd adapters/precision_intelligence
pip install -e .
```

### Basic Usage

```python
from precision_intelligence import PrecisionClient, IntelligenceClient

# Initialize clients
precision = PrecisionClient()
intelligence = IntelligenceClient()

# Get recommendations from Precision
recommendations = precision.get_recommendations("F001")
print(f"Field: {recommendations['field_id']}")
print(f"Zones: {len(recommendations['zones'])}")

# Ingest into Intelligence
result = intelligence.ingest_recommendations(recommendations)
print(f"Priority: {result['priority']}")

# Get generated decision
decision = intelligence.get_decision("F001")
print(f"Total ROI: {decision['total_estimated_roi_brl_year']:,.2f} BRL/year")
```

### Full Flow (One-Liner)

```python
from precision_intelligence import execute_full_flow

result = execute_full_flow("F001")
print(result["decision"]["priority"]["level"])  # HIGH, MEDIUM, LOW
```

See [adapters/precision_intelligence/README.md](adapters/precision_intelligence/README.md) for full documentation.

## 🔗 Data Contracts

All service-to-service communication follows formal JSON Schema contracts:

- [precision.recommendations.schema.json](contracts/precision.recommendations.schema.json) - Field recommendations output
- [intelligence.decision.schema.json](contracts/intelligence.decision.schema.json) - Decision support output

Contracts are validated automatically in:
- CI/CD pipeline (`.github/workflows/contracts.yml`)
- Adapter SDK (optional, configurable via `PRECISION_INTELLIGENCE_VALIDATE_SCHEMAS`)

See [contracts/README.md](contracts/README.md) for details.

## 🧪 CI/CD Pipeline

### Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **E2E Tests** | PR, Push to main/develop, Every 6h | Tests Precision→Intelligence flow with Docker Compose |
| **Contract Validation** | PR, Push to main/develop | Validates JSON schemas and examples |

### Branch Protection

The `main` branch is protected:
- ✅ **E2E tests must pass** before merging
- ✅ **Contract validation must pass** before merging
- ✅ **No force pushes allowed**

To merge a PR:
1. All CI checks must be green
2. Code review required (if configured)
3. PR cannot have merge conflicts

## 🛠️ Development

### Prerequisites

- Python 3.11+
- Docker + Docker Compose
- Git

### Setup Development Environment

```bash
# Clone ecosystem repo
git clone https://github.com/avilaops/agro-tech-ecosystem.git
cd agro-tech-ecosystem

# Clone service repos (parallel to ecosystem)
cd ..
git clone https://github.com/avilaops/Precision-Agriculture-Platform.git
git clone https://github.com/avilaops/CanaSwarm-Intelligence.git
```

Expected directory structure:
```
parent-folder/
├── agro-tech-ecosystem/
├── Precision-Agriculture-Platform/
└── CanaSwarm-Intelligence/
```

### Adding New Service Integration

1. **Define contract** in `contracts/<service>.schema.json`
2. **Create adapter** in `adapters/<service_name>/`
3. **Add E2E test** in `integration/test_<service>_integration.py`
4. **Update docker-compose.e2e.yml** with new service
5. **Update CI workflow** `.github/workflows/e2e.yml`

See [INTEGRATION-MATRIX.md](INTEGRATION-MATRIX.md) for integration roadmap.

## 📊 Test Coverage

| Package | Coverage | Tests |
|---------|----------|-------|
| **precision_intelligence adapter** | 97% | 46/51 passing |
| **E2E precision→intelligence** | 100% | 1/1 passing |
| **Contract validation** | 100% | Schema validation active |

## 🐛 Troubleshooting

### Services fail to start

```bash
# Check logs
make e2e-logs
# or
.\scripts\e2e.ps1 logs

# Rebuild images from scratch
make e2e-rebuild
# or
.\scripts\e2e.ps1 rebuild
```

### E2E test times out

- **Health checks**: Services must respond to `/api/v1/health` within 30s
- **Network**: Check if ports 5000/6000 are available
- **Resources**: Docker needs ~2GB RAM minimum

### Contract validation fails

```bash
# Validate schema manually
python -m jsonschema -i contracts/examples/precision_recommendations.json \
                     contracts/precision.recommendations.schema.json
```

## 📝 Documentation

- [Data Contracts README](contracts/README.md)
- [Integration Tests README](integration/README.md)
- [Adapter SDK Documentation](adapters/precision_intelligence/README.md)
- [Integration Matrix](INTEGRATION-MATRIX.md)
- [Governance & Roadmap](GOVERNANCE.md)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agro-Tech Ecosystem                      │
│                                                             │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐ │
│  │  Precision   │ ───▶ │ Intelligence │ ───▶ │ Decision │ │
│  │  Platform    │      │     API      │      │  Output  │ │
│  └──────────────┘      └──────────────┘      └──────────┘ │
│         │                      │                           │
│         ▼                      ▼                           │
│  ┌──────────────────────────────────┐                     │
│  │      Data Contracts (JSON)       │                     │
│  │  - precision.recommendations     │                     │
│  │  - intelligence.decision         │                     │
│  └──────────────────────────────────┘                     │
│                                                            │
│  ┌──────────────────────────────────┐                     │
│  │   Adapter SDK (precision_intell) │                     │
│  │  - Client classes                │                     │
│  │  - Schema validation             │                     │
│  │  - Retry logic                   │                     │
│  └──────────────────────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Security

- **No credentials in code**: All secrets via environment variables
- **Container isolation**: Services run in isolated Docker network
- **Branch protection**: Main branch requires passing CI
- **Dependency scanning**: Automated with GitHub Dependabot

## 📈 Metrics & Monitoring

CI/CD health:
- **E2E Success Rate**: Tracked in GitHub Actions
- **Test Duration**: ~2-3 minutes average
- **Build Cache**: Docker layers cached for speed

## 🤝 Contributing

1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Make changes** and add tests
3. **Run E2E locally**: `make e2e` or `.\scripts\e2e.ps1`
4. **Create PR** to `main`
5. **Wait for CI**: All checks must pass
6. **Merge** when approved

## 📜 License

Proprietary - CanaSwarm Ecosystem

---

**Maintainer**: @avilaops  
**Status**: ✅ Production-ready with 97% adapter coverage

<!-- Test: Validating CI blocking on main branch -->
