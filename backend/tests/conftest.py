"""Test configuration and fixtures for pytest."""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Dict

# Add the parent directory to Python path to make 'app' imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.database import Base, get_db
from app.main import app as fastapi_app


def strip_timezone(dt: datetime) -> datetime:
    """Strip timezone info from a datetime object."""
    return dt.replace(tzinfo=None) if dt and dt.tzinfo else dt


# Create a test database engine and session
@pytest.fixture
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create a test database engine."""
    # Use SQLite in-memory database for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # SQLite datetime compatibility hook
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Remove timezone info before storing in SQLite
    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def convert_datetime(conn, cursor, statement, params, context, executemany):
        if not params:
            return

        if isinstance(params, dict):
            for key, value in params.items():
                if isinstance(value, datetime):
                    params[key] = strip_timezone(value)
        else:
            params = [strip_timezone(p) if isinstance(p, datetime) else p for p in params]

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session_maker(test_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create a test session maker."""
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


@pytest.fixture
async def test_session(test_session_maker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_session_maker() as session:
        yield session
        # Rollback all changes after test
        await session.rollback()


@pytest.fixture
async def test_app(test_session_maker: async_sessionmaker[AsyncSession]) -> FastAPI:
    """Create a test FastAPI app with dependency overrides."""

    # Override the get_db dependency
    async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
        async with test_session_maker() as session:
            yield session

    app = fastapi_app
    # Override the get_db dependency
    app.dependency_overrides[get_db] = get_test_db

    return app


@pytest.fixture
async def test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for FastAPI app."""
    from httpx import ASGITransport

    # Create ASGITransport with FastAPI app
    transport = ASGITransport(app=test_app)

    # Create AsyncClient with the transport
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# Sample mock data
@pytest.fixture
def sample_coin_data() -> Dict[str, Any]:
    """Return sample coin data for testing."""
    from decimal import Decimal

    current_time = datetime.now(timezone.utc)

    # Using 8 decimal places for price-related decimals
    return {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": Decimal("50000.00000000"),
        "price_change_percentage_24h": 3.5,  # Matches the test expectation
        "market_cap": Decimal("1000000000000.00"),  # 2 decimal places for market cap
        "market_cap_rank": 1,
        "circulating_supply": Decimal("19000000.00"),  # 2 decimal places for supply
        "max_supply": Decimal("21000000.00"),  # 2 decimal places for supply
        "image_url": "https://example.com/bitcoin.png",
        "description": "Bitcoin is a decentralized digital currency.",
        "last_updated": current_time,
        "created_at": current_time,
    }


@pytest.fixture
def sample_portfolio_entry_data() -> Dict[str, Any]:
    """Return sample portfolio entry data for testing."""
    from decimal import Decimal

    return {"coin_id": "bitcoin", "amount": Decimal("0.50000000")}
