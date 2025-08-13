#!/bin/bash
# Script to run tests for all packages in the workspace

echo "====================================="
echo "Running tests for all RAG packages"
echo "====================================="
echo ""

# Initialize counters
total_tests=0
passed_tests=0
failed_packages=""

# Function to run tests for a package
run_package_tests() {
    local package=$1
    echo "📦 Testing $package..."
    echo "-----------------------------------"
    
    # Navigate to package directory
    cd "packages/$package" || exit 1
    
    # Install test dependencies if needed
    if [ "$package" == "storm-client" ]; then
        uv sync --extra test > /dev/null 2>&1
    fi
    
    # Run tests and capture output
    if uv run pytest -v --tb=short; then
        echo "✅ $package tests passed"
    else
        echo "❌ $package tests failed"
        failed_packages="$failed_packages $package"
    fi
    
    # Return to root
    cd ../.. || exit 1
    echo ""
}

# Run tests for each package
for package in rag-core storm-client rag-engine rag-service rag-api; do
    run_package_tests "$package"
done

# Summary
echo "====================================="
echo "TEST SUMMARY"
echo "====================================="

if [ -z "$failed_packages" ]; then
    echo "✅ All packages passed!"
else
    echo "❌ Failed packages:$failed_packages"
    exit 1
fi