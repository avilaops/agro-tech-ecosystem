# E2E Testing Script for Windows PowerShell
# 
# Usage:
#   .\scripts\e2e.ps1              # Run complete E2E test suite
#   .\scripts\e2e.ps1 up           # Start services only
#   .\scripts\e2e.ps1 down         # Stop services
#   .\scripts\e2e.ps1 logs         # Show logs
#   .\scripts\e2e.ps1 rebuild      # Rebuild images
#   .\scripts\e2e.ps1 clean        # Clean everything

param(
    [Parameter(Position=0)]
    [string]$Command = "run"
)

$ErrorActionPreference = "Stop"
$ComposeFile = "docker-compose.e2e.yml"

function Show-Help {
    Write-Host @"
E2E Testing Commands

Usage: .\scripts\e2e.ps1 <command>

Commands:
  run (default)   Run complete E2E test suite
  up              Start services only (for manual testing)
  down            Stop services
  logs            Show container logs
  rebuild         Rebuild images from scratch
  clean           Clean containers, networks, and images
  help            Show this help message

Examples:
  .\scripts\e2e.ps1
  .\scripts\e2e.ps1 up
  .\scripts\e2e.ps1 logs
  .\scripts\e2e.ps1 clean
"@
}

function Run-E2E-Tests {
    Write-Host "🚀 Starting E2E test suite..." -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "📦 Building and starting services..." -ForegroundColor Gray
    docker-compose -f $ComposeFile up -d --build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to start services" -ForegroundColor Red
        docker-compose -f $ComposeFile logs
        docker-compose -f $ComposeFile down -v
        exit 1
    }
    
    Write-Host ""
    Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Gray
    
    $maxAttempts = 30
    $attempt = 0
    $healthy = $false
    
    while ($attempt -lt $maxAttempts -and -not $healthy) {
        $attempt++
        Write-Host -NoNewline "."
        
        $status = docker-compose -f $ComposeFile ps
        if ($status -match "healthy") {
            $healthy = $true
        } else {
            Start-Sleep -Seconds 2
        }
    }
    
    Write-Host ""
    
    if (-not $healthy) {
        Write-Host "❌ Services failed to become healthy after $maxAttempts attempts" -ForegroundColor Red
        docker-compose -f $ComposeFile logs
        docker-compose -f $ComposeFile down -v
        exit 1
    }
    
    Write-Host "✅ Services are healthy!" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🧪 Running E2E tests..." -ForegroundColor Cyan
    python integration\test_precision_to_intelligence.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "❌ Tests failed" -ForegroundColor Red
        Write-Host ""
        Write-Host "📋 Container logs:" -ForegroundColor Yellow
        docker-compose -f $ComposeFile logs
        docker-compose -f $ComposeFile down -v
        exit 1
    }
    
    Write-Host ""
    Write-Host "✅ All tests passed!" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🛑 Stopping services..." -ForegroundColor Gray
    docker-compose -f $ComposeFile down -v
    
    Write-Host ""
    Write-Host "✅ E2E test suite completed successfully!" -ForegroundColor Green
}

function Start-Services {
    Write-Host "🚀 Starting services..." -ForegroundColor Cyan
    docker-compose -f $ComposeFile up -d --build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to start services" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "⏳ Waiting for health checks..." -ForegroundColor Gray
    
    $maxAttempts = 30
    $attempt = 0
    $healthy = $false
    
    while ($attempt -lt $maxAttempts -and -not $healthy) {
        $attempt++
        Write-Host -NoNewline "."
        
        $status = docker-compose -f $ComposeFile ps
        if ($status -match "healthy") {
            $healthy = $true
        } else {
            Start-Sleep -Seconds 2
        }
    }
    
    Write-Host ""
    
    if (-not $healthy) {
        Write-Host "⚠️  Services started but may not be healthy yet" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Services are running and healthy!" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Precision API:     http://localhost:5000" -ForegroundColor Cyan
    Write-Host "Intelligence API:  http://localhost:6000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To run tests:      python integration\test_precision_to_intelligence.py" -ForegroundColor Gray
    Write-Host "To stop services:  .\scripts\e2e.ps1 down" -ForegroundColor Gray
}

function Stop-Services {
    Write-Host "🛑 Stopping services..." -ForegroundColor Cyan
    docker-compose -f $ComposeFile down -v
    Write-Host "✅ Services stopped" -ForegroundColor Green
}

function Show-Logs {
    Write-Host "📋 Container logs:" -ForegroundColor Cyan
    Write-Host ""
    docker-compose -f $ComposeFile logs
}

function Rebuild-Images {
    Write-Host "🔨 Rebuilding images from scratch..." -ForegroundColor Cyan
    docker-compose -f $ComposeFile build --no-cache
    Write-Host "✅ Rebuild complete" -ForegroundColor Green
}

function Clean-All {
    Write-Host "🧹 Cleaning up..." -ForegroundColor Cyan
    docker-compose -f $ComposeFile down -v --rmi all
    Write-Host "✅ Cleanup complete" -ForegroundColor Green
}

# Execute command
switch ($Command.ToLower()) {
    "run" { Run-E2E-Tests }
    "up" { Start-Services }
    "down" { Stop-Services }
    "logs" { Show-Logs }
    "rebuild" { Rebuild-Images }
    "clean" { Clean-All }
    "help" { Show-Help }
    default {
        Write-Host "❌ Unknown command: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
        exit 1
    }
}
