@echo off
REM Local development environment setup script for Windows

echo Creating virtual environment...
call uv venv

echo Activating virtual environment...
echo Run: .venv\Scripts\activate

echo Installing dependencies with development extras...
echo Run: uv pip install -e ".[dev]"

echo To run tests after activation, use:
echo pytest

echo To run the application with hot reload, use:
echo uvicorn app.main:app --reload

echo Done! Your local development environment is ready.
