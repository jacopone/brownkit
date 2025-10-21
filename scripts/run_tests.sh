#!/bin/bash
# Test runner script for Brownfield-Kit
# Provides convenient shortcuts for running different test suites

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${BLUE}===================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    print_error "pytest not found. Install with: pip install -r requirements-dev.txt"
    exit 1
fi

# Parse command line arguments
TEST_TYPE="${1:-all}"
COVERAGE="${2:-}"

case "$TEST_TYPE" in
    unit)
        print_header "Running Unit Tests"
        if [ "$COVERAGE" = "--coverage" ]; then
            pytest tests/unit/ --cov=src/brownfield --cov-report=term --cov-report=html
        else
            pytest tests/unit/ -v
        fi
        ;;

    contract)
        print_header "Running Contract Tests"
        pytest tests/contract/ -v
        ;;

    integration)
        print_header "Running Integration Tests"
        print_warning "Integration tests may take longer to run..."
        if [ "$COVERAGE" = "--coverage" ]; then
            pytest tests/integration/ --cov=src/brownfield --cov-report=term --cov-report=html
        else
            pytest tests/integration/ -v
        fi
        ;;

    fast)
        print_header "Running Fast Tests (unit + contract)"
        pytest tests/unit/ tests/contract/ -v
        ;;

    all)
        print_header "Running All Tests"
        if [ "$COVERAGE" = "--coverage" ]; then
            pytest tests/ --cov=src/brownfield --cov-report=term --cov-report=html
            print_success "Coverage report generated: htmlcov/index.html"
        else
            pytest tests/ -v
        fi
        ;;

    coverage)
        print_header "Running All Tests with Coverage"
        pytest tests/ --cov=src/brownfield --cov-report=term --cov-report=html
        print_success "Coverage report generated: htmlcov/index.html"
        print_success "Open with: open htmlcov/index.html (macOS) or xdg-open htmlcov/index.html (Linux)"
        ;;

    quick)
        print_header "Running Quick Test Suite"
        pytest tests/unit/ tests/contract/ -v --tb=line -q
        ;;

    watch)
        print_header "Running Tests in Watch Mode"
        print_warning "Tests will re-run on file changes (Ctrl+C to stop)"
        pytest-watch tests/ -- -v
        ;;

    help|--help|-h)
        echo "Brownfield-Kit Test Runner"
        echo ""
        echo "Usage: ./scripts/run_tests.sh [TEST_TYPE] [OPTIONS]"
        echo ""
        echo "Test Types:"
        echo "  unit        - Run unit tests only"
        echo "  contract    - Run contract tests only"
        echo "  integration - Run integration tests only"
        echo "  fast        - Run unit + contract tests (skip slow integration)"
        echo "  all         - Run all tests (default)"
        echo "  coverage    - Run all tests with coverage report"
        echo "  quick       - Run fast tests with minimal output"
        echo "  watch       - Run tests in watch mode (requires pytest-watch)"
        echo ""
        echo "Options:"
        echo "  --coverage  - Generate coverage report (for unit/integration/all)"
        echo ""
        echo "Examples:"
        echo "  ./scripts/run_tests.sh                    # Run all tests"
        echo "  ./scripts/run_tests.sh unit               # Run unit tests"
        echo "  ./scripts/run_tests.sh all --coverage     # All tests with coverage"
        echo "  ./scripts/run_tests.sh integration        # Run integration tests"
        echo "  ./scripts/run_tests.sh fast               # Quick smoke test"
        echo ""
        exit 0
        ;;

    *)
        print_error "Unknown test type: $TEST_TYPE"
        echo "Run './scripts/run_tests.sh help' for usage"
        exit 1
        ;;
esac

# Capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    print_success "All tests passed!"
else
    print_error "Some tests failed (exit code: $EXIT_CODE)"
fi

exit $EXIT_CODE
