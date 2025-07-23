#!/bin/bash

# Always rebuild and run tests with fresh image
# This ensures you're always testing the latest code

echo "Customer Support Agent - Fresh Build Test Runner"
echo "==============================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Please create one based on .env.example"
    exit 1
fi

# Function to build and run
build_and_run() {
    echo "🔨 Building fresh Docker image..."
    docker build -t customer-support-agent . || {
        echo "❌ Build failed!"
        exit 1
    }
    echo "✅ Build complete!"
    echo ""
}

case "${1:-all}" in
    all)
        build_and_run
        echo "🧪 Running all test cases..."
        docker run --rm \
            --env-file .env \
            -v "$(pwd)/data:/app/data" \
            customer-support-agent \
            python test_all_cases.py
        ;;
    single)
        if [ -z "$2" ]; then
            echo "Usage: $0 single <case_number>"
            echo ""
            echo "Available test cases:"
            echo "  1: Export button grayed out"
            echo "  2: Database corrupted"
            echo "  3: Double billing"
            echo "  4: Feature request"
            echo "  5: API rate limiting"
            echo "  6: Pricing inquiry"
            echo "  7: 2FA issues"
            echo "  8: GDPR request"
            echo "  9: Integration failure"
            echo "  10: Positive feedback"
            echo "  11: Memory leak"
            echo "  12: Accessibility"
            echo "  13: Cancellation issues"
            echo "  14: Sync conflicts"
            echo "  15: Performance issues"
            exit 1
        fi
        build_and_run
        echo "🧪 Running test case #$2..."
        docker run --rm \
            --env-file .env \
            -v "$(pwd)/data:/app/data" \
            customer-support-agent \
            python test_single_case.py $2
        ;;
    simple)
        build_and_run
        echo "🧪 Running simple debug test..."
        docker run --rm \
            --env-file .env \
            -v "$(pwd)/data:/app/data" \
            customer-support-agent \
            python test_simple.py
        ;;
    demo)
        build_and_run
        echo "🧪 Running original demo..."
        docker run --rm \
            --env-file .env \
            -v "$(pwd)/data:/app/data" \
            customer-support-agent
        ;;
    *)
        echo "Usage: $0 {all|single <num>|simple|demo}"
        echo ""
        echo "Commands:"
        echo "  all         - Build and run all 15 test cases"
        echo "  single <n>  - Build and run specific test case"
        echo "  simple      - Build and run simple debug test"
        echo "  demo        - Build and run original demo"
        echo ""
        echo "This script always rebuilds the Docker image before running tests."
        ;;
esac