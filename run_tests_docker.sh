#!/bin/bash

# Script to run test cases in Docker

echo "Customer Support Agent - Docker Test Runner"
echo "=========================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found. Please create one based on .env.example"
    exit 1
fi

# Function to run all test cases
run_all_tests() {
    echo "Running all test cases..."
    docker run --rm \
        --env-file .env \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/.env:/app/.env:ro" \
        customer-support-agent \
        python test_all_cases.py
}

# Function to run a single test case
run_single_test() {
    local case_num=$1
    echo "Running test case #$case_num..."
    docker run --rm \
        --env-file .env \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/.env:/app/.env:ro" \
        customer-support-agent \
        python test_single_case.py $case_num
}

# Function to run the original demo
run_demo() {
    echo "Running original demo..."
    docker-compose up customer-support-agent
}

# Function to build the Docker image
build_image() {
    echo "Building Docker image..."
    docker build -t customer-support-agent .
}

# Main menu
case "${1:-menu}" in
    build)
        build_image
        ;;
    all)
        build_image
        run_all_tests
        ;;
    single)
        if [ -z "$2" ]; then
            echo "Usage: $0 single <case_number>"
            echo ""
            echo "Available test cases:"
            echo "  1: Export button grayed out despite Professional plan"
            echo "  2: URGENT: Database corrupted - lost all customer data!!!"
            echo "  3: Double charged for annual subscription"
            echo "  4: Feature request: Dark mode for mobile app"
            echo "  5: API rate limiting issues affecting production"
            echo "  6: Confused about pricing tiers"
            echo "  7: Two-factor authentication not working"
            echo "  8: GDPR data deletion request"
            echo "  9: Integration with Slack broken after update"
            echo "  10: Incredible support - thank you!"
            echo "  11: Memory leak causing server crashes"
            echo "  12: Accessibility issues with screen reader"
            echo "  13: Subscription cancellation not processed"
            echo "  14: Data sync conflicts between devices"
            echo "  15: Performance degradation with large datasets"
            exit 1
        fi
        build_image
        run_single_test $2
        ;;
    demo)
        run_demo
        ;;
    *)
        echo "Usage: $0 {build|all|single <number>|demo}"
        echo ""
        echo "Commands:"
        echo "  build          - Build the Docker image"
        echo "  all            - Run all test cases"
        echo "  single <num>   - Run a specific test case"
        echo "  demo           - Run the original demo"
        echo ""
        echo "Examples:"
        echo "  $0 all                    # Run all 15 test cases"
        echo "  $0 single 2               # Run test case #2 (database corruption)"
        echo "  $0 demo                   # Run the original demo"
        ;;
esac