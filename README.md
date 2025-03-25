# CrypKit Tracker

A cryptocurrency portfolio tracker application that allows users to track their cryptocurrency holdings and view portfolio value.

## Features

- Search for cryptocurrencies using CoinGecko API
- Add cryptocurrencies to your portfolio
- Update or remove coins from your portfolio
- View portfolio summary with total value
- Refresh cryptocurrency prices
- Redis caching for improved performance

## Technology Stack

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Redis
- Pydantic
- Alembic (migrations)

### Frontend
- React
- Material UI
- React Query
- Axios

### Infrastructure
- Docker
- Docker Compose
- Nginx

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your system (for production-like environment)
- Python 3.12+ and uv (for local development)

### Running the Application in Docker

1. Clone the repository
2. Run the application using Docker Compose:

```bash
docker-compose up
```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

### Local Development

For local development without Docker, use the provided setup scripts:

```bash
# On Linux/Mac
cd backend
./scripts/setup_local_dev.sh
source .venv/bin/activate
uv pip install -e ".[dev]"
uvicorn app.main:app --reload

# On Windows
cd backend
scripts\setup_local_dev.bat
.venv\Scripts\activate
uv pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Running Tests

The project includes a comprehensive test suite:

```bash
# On Linux/Mac
cd backend
./scripts/run_tests.sh

# On Windows
cd backend
scripts\run_tests.bat

# Run with coverage
./scripts/run_tests.sh --cov=app
```

## API Endpoints

### Coins API
- `GET /api/coins` - List all available coins
- `GET /api/coins/{coin_id}` - Get details for a specific coin
- `GET /api/coins/search` - Search for coins by name or symbol

### Portfolio API
- `GET /api/portfolio` - Get all portfolio entries
- `GET /api/portfolio/summary` - Get portfolio summary
- `POST /api/portfolio` - Add a coin to portfolio
- `PUT /api/portfolio/{entry_id}` - Update a portfolio entry
- `DELETE /api/portfolio/{entry_id}` - Remove a coin from portfolio
- `POST /api/portfolio/refresh-prices` - Refresh all coin prices

## Development

### Backend

To run the backend in development mode:

```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"  # Install with development dependencies
python -m app.main
```

For local development with hot reload:

```bash
uvicorn app.main:app --reload
```

### Frontend

To run the frontend in development mode:

```bash
cd frontend
npm install
npm start
```

## Testing

### Running Tests

The project includes a comprehensive test suite for both API endpoints and data models:

```bash
# Navigate to backend directory
cd backend

# Install development dependencies if not already installed
uv pip install -e ".[dev]"

# Run all tests
pytest

# Run specific test modules
pytest tests/test_models.py
pytest tests/test_api/

# Run tests with coverage report
pytest --cov=app
```

### Testing in Docker

You can also run tests in the Docker environment:

```bash
# Run tests in the backend container
docker-compose run --rm backend pytest
```

### Test Structure

- `tests/conftest.py` - Test fixtures and configuration
- `tests/test_models.py` - Tests for Pydantic models and validation
- `tests/test_api/` - API endpoint tests

## Project Structure

```
crypkit-tracker/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── alembic/
│   ├── scripts/
│   │   ├── setup_local_dev.sh
│   │   ├── setup_local_dev.bat
│   │   ├── run_tests.sh
│   │   └── run_tests.bat
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_models.py
│   │   └── test_api/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── pytest.ini
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
