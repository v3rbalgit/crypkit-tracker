"""Test portfolio API endpoints."""

from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Coin, PortfolioEntry


@pytest.mark.asyncio
async def test_get_empty_portfolio(test_client: AsyncClient):
    """Test getting an empty portfolio."""
    response = await test_client.get("/api/portfolio/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_portfolio_summary_empty(test_client: AsyncClient):
    """Test getting portfolio summary for empty portfolio."""
    response = await test_client.get("/api/portfolio/summary")
    assert response.status_code == 200
    data = response.json()

    assert data["total_value_usd"] == "0"
    assert data["entries"] == []
    assert data["total_coins"] == 0
    assert data["total_24h_change_percentage"] is None


@pytest.mark.asyncio
async def test_add_coin_to_portfolio(
    test_client: AsyncClient, test_session: AsyncSession, sample_coin_data, sample_portfolio_entry_data
):
    """Test adding a coin to the portfolio."""
    # First add a coin to the database
    coin = Coin(**sample_coin_data)
    test_session.add(coin)
    await test_session.commit()

    # Convert Decimal to float for JSON serialization
    json_data = {
        "coin_id": sample_portfolio_entry_data["coin_id"],
        "amount": float(sample_portfolio_entry_data["amount"]),
    }

    # Add coin to portfolio
    response = await test_client.post("/api/portfolio/", json=json_data)

    assert response.status_code == 200
    data = response.json()
    assert data["coin_id"] == sample_portfolio_entry_data["coin_id"]
    assert data["amount"] == "0.5"
    assert "id" in data
    assert "updated_at" in data
    assert "created_at" in data
    assert "coin" in data


@pytest.mark.asyncio
async def test_get_portfolio_with_entries(test_client: AsyncClient, test_session: AsyncSession, sample_coin_data):
    """Test getting a portfolio with entries."""
    # First add a coin to the database
    coin = Coin(**sample_coin_data)
    test_session.add(coin)

    # Add a portfolio entry
    entry = PortfolioEntry(coin_id=coin.id, amount=Decimal("0.75000000"))
    test_session.add(entry)
    await test_session.commit()

    # Get the portfolio
    response = await test_client.get("/api/portfolio/")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["coin_id"] == coin.id
    assert data[0]["amount"] == "0.75000000"
    assert "coin" in data[0]
    assert data[0]["coin"]["name"] == coin.name


@pytest.mark.asyncio
async def test_update_portfolio_entry(test_client: AsyncClient, test_session: AsyncSession, sample_coin_data):
    """Test updating a portfolio entry."""
    # First add a coin to the database
    coin = Coin(**sample_coin_data)
    test_session.add(coin)

    # Add a portfolio entry
    entry = PortfolioEntry(coin_id=coin.id, amount=Decimal("0.50000000"))
    test_session.add(entry)
    await test_session.commit()

    # Update the entry
    response = await test_client.put(f"/api/portfolio/{entry.id}", json={"amount": 1.0})
    assert response.status_code == 200

    # Need to commit and expire all to ensure DB is in sync
    await test_session.commit()
    test_session.expire_all()

    # Verify the update
    response = await test_client.get(f"/api/portfolio/{entry.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == "1.00000000"


@pytest.mark.asyncio
async def test_delete_portfolio_entry(test_client: AsyncClient, test_session: AsyncSession, sample_coin_data):
    """Test deleting a portfolio entry."""
    # First add a coin to the database
    coin = Coin(**sample_coin_data)
    test_session.add(coin)

    # Add a portfolio entry
    entry = PortfolioEntry(coin_id=coin.id, amount=Decimal("0.50000000"))
    test_session.add(entry)
    await test_session.commit()

    # Delete the entry
    response = await test_client.delete(f"/api/portfolio/{entry.id}")
    assert response.status_code == 200

    # Need to commit and expire all to ensure DB is in sync
    await test_session.commit()
    test_session.expire_all()

    # Verify the entry was deleted
    response = await test_client.get("/api/portfolio/")
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_refresh_prices(test_client: AsyncClient, test_session: AsyncSession, sample_coin_data, monkeypatch):
    """Test refreshing coin prices."""
    from app.schemas.models import CoinDetail
    from app.services.coingecko import coingecko_service

    # Mock the coingecko service with complete coin data
    coin_data = dict(sample_coin_data)
    coin_data["current_price"] = Decimal("50000.00000000")
    coin_data["price_change_percentage_24h"] = 3.5

    async def mock_get_coin_details(coin_id):
        return CoinDetail.model_validate(coin_data)

    monkeypatch.setattr(coingecko_service, "get_coin_details", mock_get_coin_details)

    # Add a coin to the database
    coin = Coin(**sample_coin_data)
    test_session.add(coin)

    # Add a portfolio entry
    entry = PortfolioEntry(coin_id=coin.id, amount=Decimal("0.50000000"))
    test_session.add(entry)
    await test_session.commit()

    # Refresh prices
    response = await test_client.post("/api/portfolio/refresh-prices")
    assert response.status_code == 200
    assert response.json()["detail"] == "Updated prices for 1 coins"

    # After refresh, we need to commit and expire all to get fresh data
    await test_session.commit()
    test_session.expire_all()  # Expire all cached objects

    response = await test_client.get("/api/portfolio/")
    assert response.status_code == 200
    data = response.json()

    # Verify the price updates
    data = response.json()
    assert len(data) == 1
    assert data[0]["coin"]["current_price"] == "50000.00000000"  # New price after refresh
    assert data[0]["coin"]["price_change_percentage_24h"] == 3.5  # Price change should be copied from mock data
