# CrypKit Tracker

A cryptocurrency portfolio tracker application that allows users to track their cryptocurrency holdings and view portfolio value.

## Features

- Search for cryptocurrencies using CoinGecko API
- Add cryptocurrencies to your portfolio
- Update or remove coins from your portfolio
- View portfolio summary with total value
- Refresh cryptocurrency prices
- Redis caching for improved performance
- Configurable logging with file rotation

## Technology Stack

### Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Redis
- Pydantic
- Alembic (migrations)
- uv (Python package manager)

### Frontend
- React
- TypeScript
- Material UI
- React Query
- Axios

### Infrastructure
- Docker
- Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your system

### Environment Setup

Create a `.env` file in the project root with the following variables:

```
# Database settings
POSTGRES_USER=crypkit
POSTGRES_PASSWORD=crypkit_password
POSTGRES_DB=tracker
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# CoinGecko API settings
COINGECKO_API_URL=https://api.coingecko.com/api/v3
COINGECKO_API_KEY=your_api_demo_key
COINGECKO_CACHE_TTL=86400  # 24 hours in seconds

# Debug flag
DEBUG=true
```

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

## Project Structure

```
crypkit-tracker/
├── backend/             # FastAPI backend application
├── frontend/            # React TypeScript frontend
└── docker-compose.yml   # Docker configuration
```

For detailed documentation on setup, configuration, and development:

- [Backend Documentation](./backend/README.md)
- [Frontend Documentation](./frontend/README.md)
