.PHONY: test test-all test-single test-fresh build clean

# Default target
test: test-fresh

# Always rebuild before testing
test-fresh: build test-all

# Build the Docker image
build:
	@echo "🔨 Building Docker image..."
	docker build -t customer-support-agent .

# Run all test cases
test-all:
	@echo "🧪 Running all test cases..."
	docker run --rm --env-file .env -v "$$(pwd)/data:/app/data" customer-support-agent python test_all_cases.py

# Run single test case (usage: make test-single CASE=5)
test-single:
	@echo "🧪 Running test case #$(CASE)..."
	docker run --rm --env-file .env -v "$$(pwd)/data:/app/data" customer-support-agent python test_single_case.py $(CASE)

# Run with fresh build and specific case
test-case: build
	@echo "🧪 Running test case #$(CASE) with fresh build..."
	docker run --rm --env-file .env -v "$$(pwd)/data:/app/data" customer-support-agent python test_single_case.py $(CASE)

# Run simple debug test
test-simple: build
	@echo "🧪 Running simple debug test..."
	docker run --rm --env-file .env -v "$$(pwd)/data:/app/data" customer-support-agent python test_simple.py

# Clean up Docker images
clean:
	docker rmi customer-support-agent || true

# Help
help:
	@echo "Available targets:"
	@echo "  make test          - Build and run all tests (default)"
	@echo "  make test-fresh    - Force rebuild and run all tests"
	@echo "  make test-all      - Run all tests (no rebuild)"
	@echo "  make test-single CASE=5  - Run single test case"
	@echo "  make test-case CASE=5    - Rebuild and run single test"
	@echo "  make test-simple   - Build and run simple debug test"
	@echo "  make build         - Build Docker image only"
	@echo "  make clean         - Remove Docker image"