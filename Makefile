# E2E Testing Makefile
# 
# Usage:
#   make e2e          # Run E2E tests with Docker Compose
#   make e2e-up       # Start services only
#   make e2e-down     # Stop services
#   make e2e-logs     # Show logs
#   make e2e-clean    # Clean everything (containers + images)

.PHONY: help e2e e2e-up e2e-down e2e-logs e2e-clean e2e-rebuild

help:
	@echo "E2E Testing Commands"
	@echo ""
	@echo "  make e2e          - Run complete E2E test suite"
	@echo "  make e2e-up       - Start services only (for manual testing)"
	@echo "  make e2e-down     - Stop services"
	@echo "  make e2e-logs     - Show container logs"
	@echo "  make e2e-rebuild  - Rebuild images from scratch"
	@echo "  make e2e-clean    - Clean containers, networks, and images"
	@echo ""

e2e:
	@echo "🚀 Starting E2E test suite..."
	@echo ""
	@echo "📦 Building and starting services..."
	docker-compose -f docker-compose.e2e.yml up -d --build
	@echo ""
	@echo "⏳ Waiting for services to be healthy..."
	@timeout 60 bash -c 'until docker-compose -f docker-compose.e2e.yml ps | grep -q "healthy"; do echo -n "."; sleep 2; done' || (echo "❌ Services failed to start"; docker-compose -f docker-compose.e2e.yml logs; docker-compose -f docker-compose.e2e.yml down -v; exit 1)
	@echo ""
	@echo "✅ Services are healthy!"
	@echo ""
	@echo "🧪 Running E2E tests..."
	python integration/test_precision_to_intelligence.py || (echo "❌ Tests failed"; docker-compose -f docker-compose.e2e.yml logs; docker-compose -f docker-compose.e2e.yml down -v; exit 1)
	@echo ""
	@echo "✅ All tests passed!"
	@echo ""
	@echo "🛑 Stopping services..."
	docker-compose -f docker-compose.e2e.yml down -v
	@echo ""
	@echo "✅ E2E test suite completed successfully!"

e2e-up:
	@echo "🚀 Starting services..."
	docker-compose -f docker-compose.e2e.yml up -d --build
	@echo ""
	@echo "⏳ Waiting for health checks..."
	@timeout 60 bash -c 'until docker-compose -f docker-compose.e2e.yml ps | grep -q "healthy"; do echo -n "."; sleep 2; done'
	@echo ""
	@echo "✅ Services are running!"
	@echo ""
	@echo "Precision API:     http://localhost:5000"
	@echo "Intelligence API:  http://localhost:6000"
	@echo ""
	@echo "To run tests:      python integration/test_precision_to_intelligence.py"
	@echo "To stop services:  make e2e-down"

e2e-down:
	@echo "🛑 Stopping services..."
	docker-compose -f docker-compose.e2e.yml down -v
	@echo "✅ Services stopped"

e2e-logs:
	@echo "📋 Container logs:"
	@echo ""
	docker-compose -f docker-compose.e2e.yml logs

e2e-rebuild:
	@echo "🔨 Rebuilding images from scratch..."
	docker-compose -f docker-compose.e2e.yml build --no-cache
	@echo "✅ Rebuild complete"

e2e-clean:
	@echo "🧹 Cleaning up..."
	docker-compose -f docker-compose.e2e.yml down -v --rmi all
	@echo "✅ Cleanup complete"
