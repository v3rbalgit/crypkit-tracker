@echo off
REM Script to run tests for the Crypkit Tracker application

REM Check if virtual environment exists
if not exist .venv (
    echo Virtual environment not found. Creating one...
    call uv venv
    echo Please run this script again after activating the virtual environment:
    echo .venv\Scripts\activate
    exit /b 1
)

REM Check if Python is from virtual env by checking the path prefix
python -c "import sys; exit(0 if sys.executable.find('.venv') > 0 else 1)" 2>nul
if %ERRORLEVEL% neq 0 (
    echo Virtual environment not activated. Please activate it first with:
    echo .venv\Scripts\activate
    exit /b 1
)

REM Install dev dependencies if needed
python -c "import pytest" 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing development dependencies...
    call uv pip install -e ".[dev]"
)

REM Run the tests
echo Running tests...

REM Check for arguments
if "%~1"=="" (
    REM No arguments, run all tests
    python -m pytest
) else (
    REM Forward arguments to pytest
    python -m pytest %*
)

REM Show help message for common commands
echo.
echo Common test commands:
echo   run_tests.bat                        # Run all tests
echo   run_tests.bat tests\test_models.py   # Run specific test file
echo   run_tests.bat --cov=app              # Run with coverage report
echo   run_tests.bat -v                     # Run with verbose output
