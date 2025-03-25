"""Test coins API endpoints."""

import pytest
from httpx import AsyncClient

from app.schemas.models import CoinBase, CoinDetail, CoinResponse


@pytest.mark.asyncio
async def test_get_coins_list(test_client: AsyncClient, monkeypatch):
    """Test getting a list of coins."""
    from app.services.coingecko import coingecko_service

    from datetime import datetime, timezone

    current_time = datetime.now(timezone.utc)

    # Sample coin list data
    sample_coins = [
        CoinResponse(id="bitcoin", symbol="btc", name="Bitcoin", created_at=current_time),
        CoinResponse(id="ethereum", symbol="eth", name="Ethereum", created_at=current_time),
        CoinResponse(id="cardano", symbol="ada", name="Cardano", created_at=current_time),
    ]

    # Mock the coingecko service
    async def mock_get_coins_list():
        return sample_coins

    # Apply the mock
    monkeypatch.setattr(coingecko_service, "get_coins_list", mock_get_coins_list)

    # Test the endpoint
    response = await test_client.get("/api/coins/")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3
    assert data[0]["id"] == "bitcoin"
    assert data[1]["id"] == "ethereum"
    assert data[2]["id"] == "cardano"


@pytest.mark.asyncio
async def test_get_coins_with_pagination(test_client: AsyncClient, monkeypatch):
    """Test getting a paginated list of coins."""
    from app.services.coingecko import coingecko_service

    # Generate sample coins
    from datetime import datetime, timezone

    current_time = datetime.now(timezone.utc)

    sample_coins = [
        CoinResponse(id=f"coin{i}", symbol=f"c{i}", name=f"Coin {i}", created_at=current_time) for i in range(1, 20)
    ]

    # Mock the coingecko service
    async def mock_get_coins_list():
        return sample_coins

    # Apply the mock
    monkeypatch.setattr(coingecko_service, "get_coins_list", mock_get_coins_list)

    # Test with pagination
    response = await test_client.get("/api/coins/?skip=5&limit=5")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 5
    assert data[0]["id"] == "coin6"  # 0-indexed + skip 5
    assert data[4]["id"] == "coin10"


@pytest.mark.asyncio
async def test_get_coin_detail(test_client: AsyncClient, monkeypatch):
    """Test getting details for a specific coin."""
    from datetime import datetime, timezone

    from app.services.coingecko import coingecko_service

    # Create sample data with proper datetime objects
    coin_data = {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": 50000.0,
        "market_cap": 1000000000000.0,
        "price_change_percentage_24h": 2.5,
        "last_updated": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
    }

    # Mock the coingecko service
    async def mock_get_coin_details(coin_id):
        return CoinDetail.model_validate(coin_data)

    # Apply the mock
    monkeypatch.setattr(coingecko_service, "get_coin_details", mock_get_coin_details)

    # Test the endpoint
    response = await test_client.get("/api/coins/bitcoin")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == "bitcoin"
    assert data["symbol"] == "btc"
    assert data["name"] == "Bitcoin"
    assert float(data["current_price"]) == 50000.0
    assert float(data["market_cap"]) == 1000000000000.0
    assert data["price_change_percentage_24h"] == 2.5


@pytest.mark.asyncio
async def test_get_coin_not_found(test_client: AsyncClient, monkeypatch):
    """Test getting a non-existent coin."""
    from app.services.coingecko import coingecko_service

    # Mock the coingecko service to raise an exception
    async def mock_get_coin_details(coin_id):
        raise Exception("Coin not found")

    # Apply the mock
    monkeypatch.setattr(coingecko_service, "get_coin_details", mock_get_coin_details)

    # Test the endpoint
    response = await test_client.get("/api/coins/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_search_coins(test_client: AsyncClient, monkeypatch, test_session):
    """Test searching for coins."""
    from app.services.coingecko import coingecko_service

    # Sample search results
    sample_coins = [
        CoinBase(id="bitcoin", symbol="btc", name="Bitcoin"),
        CoinBase(id="bitcoin-cash", symbol="bch", name="Bitcoin Cash"),
        CoinBase(id="bitcoin-gold", symbol="btg", name="Bitcoin Gold"),
    ]

    # Mock the coingecko service
    async def mock_search_coins(query):
        # Just return coins that match the query
        return sample_coins, len(sample_coins)

    # Apply the mock
    monkeypatch.setattr(coingecko_service, "search_coins", mock_search_coins)

    # Test the endpoint
    response = await test_client.get("/api/coins/search/?query=bitcoin")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 3
    assert len(data["results"]) == 3
    for coin in data["results"]:
        assert "bitcoin" in coin["id"]
        assert coin["in_portfolio"] is False  # No coins in portfolio yet


@pytest.mark.asyncio
async def test_search_with_portfolio_check(test_client: AsyncClient, monkeypatch, test_session, sample_coin_data):
    """Test searching for coins with portfolio check."""
    from app.db.models import Coin, PortfolioEntry
    from app.services.coingecko import coingecko_service

    # Add Bitcoin to the database and portfolio
    coin = Coin(**sample_coin_data)
    test_session.add(coin)

    # Add a portfolio entry
    entry = PortfolioEntry(coin_id=coin.id, amount=0.5)
    test_session.add(entry)
    await test_session.commit()

    # Sample search results
    sample_coins = [
        CoinBase(id="bitcoin", symbol="btc", name="Bitcoin"),
        CoinBase(id="ethereum", symbol="eth", name="Ethereum"),
    ]

    # Mock the coingecko service
    async def mock_search_coins(query):
        return sample_coins, len(sample_coins)

    # Apply the mock
    monkeypatch.setattr(coingecko_service, "search_coins", mock_search_coins)

    # Test the endpoint
    response = await test_client.get("/api/coins/search/?query=coin")
    assert response.status_code == 200
    data = response.json()

    assert len(data["results"]) == 2
    # Bitcoin should be marked as in_portfolio
    for coin in data["results"]:
        if coin["id"] == "bitcoin":
            assert coin["in_portfolio"] is True, "Bitcoin should be marked as in portfolio"
        else:
            assert coin["in_portfolio"] is False
