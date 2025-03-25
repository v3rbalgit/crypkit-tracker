"""Pydantic models for request/response validation."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class CoinBase(BaseModel):
    """Base Coin schema."""

    id: str
    symbol: str
    name: str


class CoinCreate(CoinBase):
    """Schema for creating a new coin."""

    pass


class CoinResponse(CoinBase):
    """Schema for coin response."""

    model_config = ConfigDict(from_attributes=True)

    current_price: Optional[Decimal] = None
    price_change_percentage_24h: Optional[float] = None
    last_updated: Optional[datetime] = None
    created_at: datetime


class CoinDetail(CoinResponse):
    """Schema for detailed coin information."""

    model_config = ConfigDict(from_attributes=True)

    market_cap: Optional[Decimal] = None
    market_cap_rank: Optional[int] = None

    # Supply data
    circulating_supply: Optional[Decimal] = None
    max_supply: Optional[Decimal] = None

    # Descriptive data
    description: Optional[str] = None
    image_url: Optional[str] = None


class PortfolioEntryBase(BaseModel):
    """Base schema for portfolio entries."""

    coin_id: str
    amount: Decimal = Field(gt=0)

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        """Validate that amount is positive."""
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class PortfolioEntryCreate(PortfolioEntryBase):
    """Schema for creating a portfolio entry."""

    pass


class PortfolioEntryUpdate(BaseModel):
    """Schema for updating a portfolio entry."""

    amount: Decimal = Field(gt=0)

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        """Validate that amount is positive."""
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class PortfolioEntryResponse(PortfolioEntryBase):
    """Schema for portfolio entry response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: datetime
    created_at: datetime
    coin: CoinResponse

    @computed_field
    def current_value_usd(self) -> Optional[Decimal]:
        """Calculate current value based on amount and coin price."""
        try:
            if not hasattr(self, "amount") or not self.amount:
                return None

            if not hasattr(self, "coin") or not self.coin:
                return None

            if not hasattr(self.coin, "current_price") or not self.coin.current_price:
                return None

            amount = Decimal(self.amount) if not isinstance(self.amount, Decimal) else self.amount
            price = (
                Decimal(self.coin.current_price)
                if not isinstance(self.coin.current_price, Decimal)
                else self.coin.current_price
            )

            return amount * price
        except (TypeError, ValueError, AttributeError):
            return None


class PortfolioSummary(BaseModel):
    """Schema for portfolio summary with portfolio statistics."""

    # Basic portfolio data
    total_value_usd: Decimal = Field(default=Decimal(0), description="Total portfolio value in USD")
    entries: List[PortfolioEntryResponse] = Field(default_factory=list, description="List of portfolio entries")

    @computed_field
    def total_coins(self) -> int:
        """Calculate total number of different coins in portfolio."""
        return len(self.entries)

    @computed_field
    def total_24h_change_percentage(self) -> Optional[float]:
        """Calculate weighted 24h change percentage for the entire portfolio."""
        # Return None if we don't have enough data
        if not self.entries or self.total_value_usd <= 0:
            return None

        weighted_changes = Decimal(0)
        total_with_changes = Decimal(0)

        for entry in self.entries:
            if not hasattr(entry, "coin") or not entry.coin:
                continue

            # Call the computed_field method to get the current value
            value = (
                entry.current_value_usd()
                if callable(getattr(entry, "current_value_usd", None))
                else getattr(entry, "current_value_usd", Decimal(0))
            )
            value = value or Decimal(0)

            change = entry.coin.price_change_percentage_24h

            if value > 0 and change is not None:
                weighted_changes += Decimal(change) * (value / self.total_value_usd)
                total_with_changes += value

        # Return None if we don't have enough data for calculation
        if total_with_changes <= 0:
            return None

        # Adjust for the percentage of portfolio with known 24h changes
        adjustment_factor = self.total_value_usd / total_with_changes if total_with_changes > 0 else Decimal(1)
        return float(weighted_changes * adjustment_factor)


class CoinSearchResponse(BaseModel):
    """Schema for coin search response."""

    id: str
    symbol: str
    name: str
    in_portfolio: bool = False


class CoinSearchResults(BaseModel):
    """Schema for coin search results."""

    results: List[CoinSearchResponse]
    total: int
