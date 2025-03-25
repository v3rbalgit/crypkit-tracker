#!/bin/bash
# Local development environment setup script

# Create and activate virtual environment
echo "Creating virtual environment..."
uv venv

# Detect OS for activation command
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    echo "Activating virtual environment (Windows)..."
    echo "Run: .venv\\Scripts\\activate"
else
    # Unix-like
    echo "Activating virtual environment (Unix-like)..."
    echo "Run: source .venv/bin/activate"
fi

echo "Installing dependencies with development extras..."
echo "Run: uv pip install -e \".[dev]\""

echo "To run tests after activation, use:"
echo "pytest"

echo "To run the application with hot reload, use:"
echo "uvicorn app.main:app --reload"

echo "Done! Your local development environment is ready."
