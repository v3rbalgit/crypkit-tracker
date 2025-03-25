#!/bin/bash
# Script to run tests for the Crypkit Tracker application

set -e  # Exit on error

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    uv venv
    echo "Please run this script again after activating the virtual environment:"
    echo "source .venv/bin/activate"
    exit 1
fi

# Make sure we're in the virtual environment, if not suggest activating it
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment not activated. Please activate it first with:"
    echo "source .venv/bin/activate"
    exit 1
fi

# Install dev dependencies if needed
if ! python -c "import pytest" &> /dev/null; then
    echo "Installing development dependencies..."
    uv pip install -e ".[dev]"
fi

# Run the tests
echo "Running tests..."

# Parse arguments to forward to pytest
if [ "$#" -eq 0 ]; then
    # No arguments, run all tests
    python -m pytest
else
    # Forward arguments to pytest
    python -m pytest "$@"
fi

# Show help message for common commands
echo ""
echo "Common test commands:"
echo "  ./run_tests.sh                       # Run all tests"
echo "  ./run_tests.sh tests/test_models.py  # Run specific test file"
echo "  ./run_tests.sh --cov=app             # Run with coverage report"
echo "  ./run_tests.sh -v                    # Run with verbose output"
