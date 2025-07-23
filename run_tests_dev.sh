#!/bin/bash

# Development test runner - mounts the entire project for live updates

echo "Customer Support Agent - Development Test Runner"
echo "==============================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Please create one based on .env.example"
    exit 1
fi

# Run with full project mount for development
case "${1:-all}" in
    all)
        echo "Running all test cases with live code..."
        docker run --rm \
            --env-file .env \
            -v "$(pwd):/app" \
            customer-support-agent \
            python test_all_cases.py
        ;;
    single)
        if [ -z "$2" ]; then
            echo "Usage: $0 single <case_number>"
            exit 1
        fi
        echo "Running test case #$2 with live code..."
        docker run --rm \
            --env-file .env \
            -v "$(pwd):/app" \
            customer-support-agent \
            python test_single_case.py $2
        ;;
    simple)
        echo "Running simple debug test..."
        docker run --rm \
            --env-file .env \
            -v "$(pwd):/app" \
            customer-support-agent \
            python test_simple.py
        ;;
    *)
        echo "Usage: $0 {all|single <num>|simple}"
        ;;
esac