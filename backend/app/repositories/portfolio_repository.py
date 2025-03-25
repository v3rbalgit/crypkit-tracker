"""Portfolio repository for database operations."""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Coin, PortfolioEntry
from app.utils.decimal_utils import DecimalValue, standardize_decimal


class PortfolioRepository:
    """Repository for portfolio operations with stateless data access methods."""

    @staticmethod
    async def get_entry_by_id(db: AsyncSession, entry_id: int) -> Optional[PortfolioEntry]:
        """Get a portfolio entry by ID."""
        query = select(PortfolioEntry).options(selectinload(PortfolioEntry.coin)).where(PortfolioEntry.id == entry_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_entries(db: AsyncSession) -> List[PortfolioEntry]:
        """Get all portfolio entries."""
        query = select(PortfolioEntry).options(selectinload(PortfolioEntry.coin)).order_by(PortfolioEntry.created_at)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_coin(db: AsyncSession, coin_id: str) -> Optional[Coin]:
        """Get a coin by ID."""
        query = select(Coin).where(Coin.id == coin_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_portfolio_coins(db: AsyncSession) -> List[Coin]:
        """Get all coins in the portfolio."""
        query = select(Coin).join(Coin.portfolio_entries)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_entry_by_coin_id(db: AsyncSession, coin_id: str) -> Optional[PortfolioEntry]:
        """Find a portfolio entry by coin ID."""
        query = select(PortfolioEntry).where(PortfolioEntry.coin_id == coin_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_coin(db: AsyncSession, coin_data: dict) -> Coin:
        """Create a new coin."""
        # Standardize any decimal values in the coin data
        if "current_price" in coin_data and coin_data["current_price"] is not None:
            coin_data["current_price"] = standardize_decimal(coin_data["current_price"])

        coin = Coin(**coin_data)
        db.add(coin)
        return coin

    @staticmethod
    async def create_portfolio_entry(db: AsyncSession, coin_id: str, amount: DecimalValue) -> PortfolioEntry:
        """Create a new portfolio entry."""
        standardized_amount = standardize_decimal(amount)
        entry = PortfolioEntry(coin_id=coin_id, amount=standardized_amount)
        db.add(entry)
        return entry

    @staticmethod
    async def update_entry_amount(db: AsyncSession, entry: PortfolioEntry, new_amount: DecimalValue) -> None:
        """Update a portfolio entry's amount."""
        entry.amount = standardize_decimal(new_amount)
        entry.updated_at = datetime.now(timezone.utc)

    @staticmethod
    async def delete_entry(db: AsyncSession, entry: PortfolioEntry) -> None:
        """Delete a portfolio entry."""
        await db.delete(entry)

    @staticmethod
    async def get_refreshed_entry(db: AsyncSession, coin_id: str) -> Optional[PortfolioEntry]:
        """Get a fresh copy of a portfolio entry with coin relationship loaded."""
        query = (
            select(PortfolioEntry).options(selectinload(PortfolioEntry.coin)).where(PortfolioEntry.coin_id == coin_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_refreshed_entry_by_id(db: AsyncSession, entry_id: int) -> Optional[PortfolioEntry]:
        """Get a fresh copy of a portfolio entry by ID with coin relationship loaded."""
        query = select(PortfolioEntry).options(selectinload(PortfolioEntry.coin)).where(PortfolioEntry.id == entry_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_coin_price(
        db: AsyncSession, coin: Coin, price: DecimalValue, price_change: Optional[float] = None
    ) -> None:
        """Update a coin's price information."""
        coin.current_price = standardize_decimal(price)
        if price_change is not None:
            coin.price_change_percentage_24h = price_change
        coin.last_updated = datetime.now(timezone.utc)
