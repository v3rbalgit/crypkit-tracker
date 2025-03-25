# CrypKit Tracker Backend

The backend service for the CrypKit Tracker application, providing API endpoints for cryptocurrency portfolio tracking.

## Technology Stack

- **FastAPI**: Modern, high-performance web framework for building APIs
- **PostgreSQL**: Relational database for persistent storage
- **SQLAlchemy**: SQL toolkit and ORM for database interactions
- **Alembic**: Database migration tool
- **Redis**: In-memory data store used for caching
- **Pydantic**: Data validation and settings management
- **uv**: Fast Python package installer and resolver
- **Docker**: Containerization for consistent deployment

## Project Structure

```
backend/
├── alembic/                 # Database migration scripts
│   ├── versions/            # Migration version files
│   ├── env.py               # Alembic environment configuration
│   └── script.py.mako       # Migration script template
├── app/                     # Main application code
│   ├── api/                 # API endpoints
│   │   ├── coins.py         # Cryptocurrency endpoints
│   │   └── portfolio.py     # Portfolio management endpoints
│   ├── core/                # Core application components
│   │   └── config.py        # Application configuration
│   ├── db/                  # Database related code
│   │   ├── database.py      # Database connection management
│   │   └── models.py        # SQLAlchemy ORM models
│   ├── repositories/        # Data access layer
│   │   └── portfolio_repository.py  # Portfolio data operations
│   ├── schemas/             # Pydantic models for validation
│   │   └── models.py        # Data schemas
│   ├── services/            # Business logic services
│   │   ├── coingecko.py     # CoinGecko API integration
│   │   ├── portfolio.py     # Portfolio management logic
│   │   └── redis_cache.py   # Redis caching service
│   ├── utils/               # Utility functions
│   │   ├── decimal_utils.py # Decimal handling utilities
│   │   ├── logger.py        # Logging configuration
│   │   └── rate_limiter.py  # API rate limiting
│   ├── __init__.py          # Package initialization
│   └── main.py              # Application entry point
├── logs/                    # Application logs (mapped to local filesystem)
├── Dockerfile               # Container definition
├── alembic.ini              # Alembic configuration
├── pyproject.toml           # Project dependencies and metadata
└── README.md                # This file
```

## Setup & Installation

### Local Development Setup

1. **Create a virtual environment and install dependencies**:

```bash
# Create and activate virtual environment using uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package with all extras
uv sync --all-extras
```

2. **Configure environment variables**:

Create a `.env` file in the project root with the following variables:

```
# Database
POSTGRES_DB=tracker
POSTGRES_USER=crypkit
POSTGRES_PASSWORD=crypkit_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# App settings
DEBUG=true
COINGECKO_API_KEY=your_demo_api_key
COINGECKO_CACHE_TTL=86400
```

3. **Run database migrations**:

```bash
alembic upgrade head
```

4. **Start the application**:

```bash
# Run with live reload for development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or run directly
python -m app.main
```

### Docker Setup

The backend can be run in Docker as specified in the main project's docker-compose configuration.

## API Endpoints

### Health Check
- `GET /api/health` - Check API health status

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

## Database Management

### Migrations

The project uses Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Logging

The application uses Python's built-in logging module with the following configuration:

- **Console logs**: All INFO level and above logs are printed to stdout
- **File logs**:
  - `logs/app.log`: All DEBUG level and above logs
  - `logs/error.log`: All ERROR level and above logs

Logs are configured with rotation to prevent excessive file size:
- Maximum file size: 10 MB
- Backup count: 5 log files

In Docker, logs are mapped from the container to the local filesystem at `./backend/logs/` using a bind mount.

## Code Quality

The project uses Ruff for linting and formatting:

```bash
# Run linter
ruff check .

# Run formatter
ruff format .
