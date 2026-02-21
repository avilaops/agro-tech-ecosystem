# Precision→Intelligence Adapter - Development Commands
# 
# Usage:
#   .\dev.ps1 install    # Install package in editable mode
#   .\dev.ps1 test       # Run tests
#   .\dev.ps1 test-cov   # Run tests with coverage
#   .\dev.ps1 lint       # Run linters
#   .\dev.ps1 format     # Format code with black
#   .\dev.ps1 clean      # Clean build artifacts
#   .\dev.ps1 all        # Run all checks (format, lint, test)

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Host @"
Precision→Intelligence Adapter - Development Commands

Usage: .\dev.ps1 <command>

Commands:
  install     Install package in editable mode with dev dependencies
  test        Run tests with pytest
  test-cov    Run tests with coverage report
  test-unit   Run only unit tests
  lint        Run code linters (flake8, mypy)
  format      Format code with black
  clean       Clean build artifacts and caches
  all         Run all checks (format, lint, test)
  help        Show this help message

Examples:
  .\dev.ps1 install
  .\dev.ps1 test
  .\dev.ps1 format
  .\dev.ps1 all
"@
}

function Install-Package {
    Write-Host "📦 Installing precision-intelligence adapter..." -ForegroundColor Cyan
    
    # Install in editable mode with dev dependencies
    pip install -e ".[dev]"
    
    Write-Host "✅ Installation complete" -ForegroundColor Green
}

function Run-Tests {
    Write-Host "🧪 Running tests..." -ForegroundColor Cyan
    
    pytest tests/ -v
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All tests passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Tests failed" -ForegroundColor Red
        exit 1
    }
}

function Run-TestsCoverage {
    Write-Host "🧪 Running tests with coverage..." -ForegroundColor Cyan
    
    pytest tests/ --cov=precision_intelligence --cov-report=term-missing --cov-report=html -v
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All tests passed" -ForegroundColor Green
        Write-Host "📊 Coverage report: htmlcov/index.html" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Tests failed" -ForegroundColor Red
        exit 1
    }
}

function Run-UnitTests {
    Write-Host "🧪 Running unit tests..." -ForegroundColor Cyan
    
    pytest tests/ -v -m "not integration"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All unit tests passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Tests failed" -ForegroundColor Red
        exit 1
    }
}

function Run-Linters {
    Write-Host "🔍 Running linters..." -ForegroundColor Cyan
    
    Write-Host "  → flake8..." -ForegroundColor Gray
    flake8 precision_intelligence/ --max-line-length=100 --exclude=__pycache__,.pytest_cache
    
    Write-Host "  → mypy..." -ForegroundColor Gray
    mypy precision_intelligence/ --ignore-missing-imports
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Linting passed" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Linting issues found" -ForegroundColor Yellow
    }
}

function Format-Code {
    Write-Host "🎨 Formatting code..." -ForegroundColor Cyan
    
    black precision_intelligence/ tests/ --line-length=100
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Code formatted" -ForegroundColor Green
    } else {
        Write-Host "❌ Formatting failed" -ForegroundColor Red
        exit 1
    }
}

function Clean-Artifacts {
    Write-Host "🧹 Cleaning build artifacts..." -ForegroundColor Cyan
    
    # Remove Python cache
    Get-ChildItem -Path . -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force
    Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force
    Get-ChildItem -Path . -Recurse -Filter "*.pyo" | Remove-Item -Force
    
    # Remove pytest cache
    if (Test-Path ".pytest_cache") { Remove-Item -Recurse -Force ".pytest_cache" }
    
    # Remove coverage
    if (Test-Path ".coverage") { Remove-Item -Force ".coverage" }
    if (Test-Path "htmlcov") { Remove-Item -Recurse -Force "htmlcov" }
    
    # Remove build artifacts
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
    if (Test-Path "*.egg-info") { Remove-Item -Recurse -Force "*.egg-info" }
    
    Write-Host "✅ Cleanup complete" -ForegroundColor Green
}

function Run-All {
    Write-Host "🚀 Running all checks..." -ForegroundColor Cyan
    Write-Host ""
    
    Format-Code
    Write-Host ""
    
    Run-Linters
    Write-Host ""
    
    Run-TestsCoverage
    Write-Host ""
    
    Write-Host "✅ All checks passed!" -ForegroundColor Green
}

# Execute command
switch ($Command.ToLower()) {
    "install" { Install-Package }
    "test" { Run-Tests }
    "test-cov" { Run-TestsCoverage }
    "test-unit" { Run-UnitTests }
    "lint" { Run-Linters }
    "format" { Format-Code }
    "clean" { Clean-Artifacts }
    "all" { Run-All }
    "help" { Show-Help }
    default {
        Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}
