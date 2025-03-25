"""Test Pydantic models validation."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.models import (
    CoinBase,
    CoinDetail,
    PortfolioEntryBase,
    PortfolioEntryCreate,
    PortfolioEntryResponse,
    PortfolioEntryUpdate,
    PortfolioSummary,
)


def test_coin_base_validation():
    """Test CoinBase model validation."""
    # Valid data
    data = {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin"}
    coin = CoinBase(**data)
    assert coin.id == "bitcoin"
    assert coin.symbol == "btc"
    assert coin.name == "Bitcoin"

    # Missing required fields
    with pytest.raises(ValidationError):
        CoinBase(symbol="btc", name="Bitcoin")  # Missing id


def test_coin_detail_validation():
    """Test CoinDetail model validation."""
    # Valid minimal data - need all required fields
    now = datetime.now(timezone.utc)
    data = {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "created_at": now}
    coin = CoinDetail(**data)
    assert coin.id == "bitcoin"
    assert coin.current_price is None  # Optional fields

    # Valid complete data
    full_data = {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "current_price": Decimal("50000.0"),
        "market_cap": Decimal("1000000000000.0"),
        "market_cap_rank": 1,
        "price_change_percentage_24h": 2.5,
        "circulating_supply": Decimal("19000000.0"),
        "max_supply": Decimal("21000000.0"),
        "image_url": "https://example.com/bitcoin.png",
        "description": "Bitcoin is a decentralized digital currency.",
        "last_updated": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
    }
    coin = CoinDetail(**full_data)
    assert coin.current_price == Decimal("50000.0")
    assert coin.price_change_percentage_24h == 2.5


def test_portfolio_entry_base_validation():
    """Test PortfolioEntryBase model validation."""
    # Valid data
    data = {"coin_id": "bitcoin", "amount": Decimal("0.5")}
    entry = PortfolioEntryBase(**data)
    assert entry.coin_id == "bitcoin"
    assert entry.amount == Decimal("0.5")

    # Invalid amount (zero)
    with pytest.raises(ValidationError):
        PortfolioEntryBase(coin_id="bitcoin", amount=Decimal("0"))

    # Invalid amount (negative)
    with pytest.raises(ValidationError):
        PortfolioEntryBase(coin_id="bitcoin", amount=Decimal("-1"))


def test_portfolio_entry_create():
    """Test PortfolioEntryCreate model."""
    # Since it inherits from PortfolioEntryBase without adding fields,
    # just test that it works with valid data
    data = {"coin_id": "bitcoin", "amount": Decimal("0.5")}
    entry = PortfolioEntryCreate(**data)
    assert entry.coin_id == "bitcoin"
    assert entry.amount == Decimal("0.5")


def test_portfolio_entry_update():
    """Test PortfolioEntryUpdate model."""
    # Valid data
    data = {"amount": Decimal("0.5")}
    entry = PortfolioEntryUpdate(**data)
    assert entry.amount == Decimal("0.5")

    # Invalid amount (zero)
    with pytest.raises(ValidationError):
        PortfolioEntryUpdate(amount=Decimal("0"))

    # Invalid amount (negative)
    with pytest.raises(ValidationError):
        PortfolioEntryUpdate(amount=Decimal("-1"))


def test_portfolio_entry_response():
    """Test PortfolioEntryResponse model."""
    # Valid minimal data
    now = datetime.now(timezone.utc)
    data = {
        "id": 1,
        "coin_id": "bitcoin",
        "amount": Decimal("0.5"),
        "updated_at": now,
        "created_at": now,
        "coin": {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "created_at": now},
    }
    entry = PortfolioEntryResponse(**data)
    assert entry.id == 1
    assert entry.coin_id == "bitcoin"
    assert entry.amount == Decimal("0.5")
    assert entry.coin.id == "bitcoin"
    assert entry.current_value_usd is None  # Not calculated yet

    # With current price to test calculated field
    data["coin"]["current_price"] = Decimal("50000.0")
    entry = PortfolioEntryResponse(**data)

    # Check current_value_usd calculation
    assert entry.current_value_usd == Decimal("25000.0")  # 0.5 BTC * $50,000


def test_portfolio_summary():
    """Test PortfolioSummary model."""
    # Create some sample portfolio entries
    now = datetime.now(timezone.utc)
    entries = [
        PortfolioEntryResponse(
            id=1,
            coin_id="bitcoin",
            amount=Decimal("0.5"),
            updated_at=now,
            created_at=now,
            coin=CoinDetail(
                id="bitcoin",
                symbol="btc",
                name="Bitcoin",
                current_price=Decimal("50000.0"),
                price_change_percentage_24h=2.0,
                created_at=now,
            ),
        ),
        PortfolioEntryResponse(
            id=2,
            coin_id="ethereum",
            amount=Decimal("5.0"),
            updated_at=now,
            created_at=now,
            coin=CoinDetail(
                id="ethereum",
                symbol="eth",
                name="Ethereum",
                current_price=Decimal("3000.0"),
                price_change_percentage_24h=3.0,
                created_at=now,
            ),
        ),
    ]

    # Test summary creation with explicit values for all fields
    summary = PortfolioSummary(
        total_value_usd=Decimal("40000.0"),  # 0.5 BTC + 5 ETH
        entries=entries,
        total_coins=2,  # Explicitly set
        total_24h_change_percentage=2.375,  # Explicitly set
    )

    # Check the values match what we expect
    assert summary.total_coins == 2
    assert summary.total_24h_change_percentage == 2.375

    # Test creation with automatic calculation
    summary_auto = PortfolioSummary(
        total_value_usd=Decimal("40000.0"),
        entries=entries,
    )

    # Check the validator calculated the values correctly
    assert summary_auto.total_coins == 2

    # Check that the calculation works as expected (with small delta for floating point)
    # BTC: 0.5 * 50000 = 25000 (62.5% of portfolio)
    # ETH: 5 * 3000 = 15000 (37.5% of portfolio)
    # Weighted change: (2.0 * 0.625) + (3.0 * 0.375) = 1.25 + 1.125 = 2.375%
    assert summary_auto.total_24h_change_percentage is not None
    assert abs(summary_auto.total_24h_change_percentage - 2.375) < 0.01
