# Precision→Intelligence Adapter - Makefile
# 
# Usage:
#   make install    # Install package in editable mode
#   make test       # Run tests
#   make test-cov   # Run tests with coverage
#   make lint       # Run linters
#   make format     # Format code
#   make clean      # Clean artifacts
#   make all        # Run all checks

.PHONY: help install test test-cov test-unit lint format clean all

help:
	@echo "Precision→Intelligence Adapter - Development Commands"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  install     Install package in editable mode with dev dependencies"
	@echo "  test        Run tests with pytest"
	@echo "  test-cov    Run tests with coverage report"
	@echo "  test-unit   Run only unit tests"
	@echo "  lint        Run code linters (flake8, mypy)"
	@echo "  format      Format code with black"
	@echo "  clean       Clean build artifacts and caches"
	@echo "  all         Run all checks (format, lint, test)"
	@echo ""

install:
	@echo "📦 Installing precision-intelligence adapter..."
	pip install -e ".[dev]"
	@echo "✅ Installation complete"

test:
	@echo "🧪 Running tests..."
	pytest tests/ -v
	@echo "✅ All tests passed"

test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=precision_intelligence --cov-report=term-missing --cov-report=html -v
	@echo "✅ All tests passed"
	@echo "📊 Coverage report: htmlcov/index.html"

test-unit:
	@echo "🧪 Running unit tests..."
	pytest tests/ -v -m "not integration"
	@echo "✅ All unit tests passed"

lint:
	@echo "🔍 Running linters..."
	@echo "  → flake8..."
	flake8 precision_intelligence/ --max-line-length=100 --exclude=__pycache__,.pytest_cache
	@echo "  → mypy..."
	mypy precision_intelligence/ --ignore-missing-imports
	@echo "✅ Linting passed"

format:
	@echo "🎨 Formatting code..."
	black precision_intelligence/ tests/ --line-length=100
	@echo "✅ Code formatted"

clean:
	@echo "🧹 Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov build dist *.egg-info
	@echo "✅ Cleanup complete"

all: format lint test-cov
	@echo ""
	@echo "✅ All checks passed!"
