"""Database models."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import REAL, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Coin(Base):
    """Coin model representing cryptocurrency metadata."""

    __tablename__ = "coins"

    # CoinGecko ID (primary key)
    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)

    # Basic coin info
    symbol: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String, index=True)

    # Price info
    current_price: Mapped[Optional[Decimal]] = mapped_column(
        REAL(precision=10, asdecimal=True, decimal_return_scale=8), nullable=True
    )
    price_change_percentage_24h: Mapped[Optional[float]] = mapped_column(
        REAL(precision=10, asdecimal=True, decimal_return_scale=8), nullable=True
    )

    # Market data
    market_cap: Mapped[Optional[Decimal]] = mapped_column(
        REAL(precision=16, asdecimal=True, decimal_return_scale=2), nullable=True
    )
    market_cap_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Supply data
    circulating_supply: Mapped[Optional[Decimal]] = mapped_column(
        REAL(precision=16, asdecimal=True, decimal_return_scale=2), nullable=True
    )
    max_supply: Mapped[Optional[Decimal]] = mapped_column(
        REAL(precision=16, asdecimal=True, decimal_return_scale=2), nullable=True
    )

    # Descriptive data
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Timestamps
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    portfolio_entries = relationship("PortfolioEntry", back_populates="coin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of the Coin."""
        return f"<Coin {self.symbol}: {self.name}>"


class PortfolioEntry(Base):
    """Portfolio entry model representing a user's coin holdings."""

    __tablename__ = "portfolio_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign key to Coin
    coin_id: Mapped[str] = mapped_column(ForeignKey("coins.id"), index=True)

    # Amount of coins held
    amount: Mapped[Decimal] = mapped_column(REAL(precision=18, asdecimal=True), default=0)

    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    coin = relationship("Coin", back_populates="portfolio_entries")

    def __repr__(self) -> str:
        """String representation of the PortfolioEntry."""
        return f"<PortfolioEntry {self.coin_id}: {self.amount}>"
