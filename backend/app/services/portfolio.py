"""Portfolio service for managing user's cryptocurrency portfolio."""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import PortfolioEntry
from app.repositories.portfolio_repository import PortfolioRepository
from app.schemas.models import PortfolioEntryCreate, PortfolioEntryResponse, PortfolioEntryUpdate, PortfolioSummary
from app.services.coingecko import coingecko_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PortfolioService:
    """Service for portfolio operations."""

    async def get_portfolio_entries(self, db: AsyncSession) -> List[PortfolioEntry]:
        """Get all portfolio entries with related coin data."""
        entries = await PortfolioRepository.get_all_entries(db)
        logger.debug(f"Retrieved {len(entries)} portfolio entries")
        return entries

    async def get_portfolio_summary(self, db: AsyncSession) -> PortfolioSummary:
        """Get portfolio summary with total value and statistics."""
        # Get all portfolio entries
        entries = await self.get_portfolio_entries(db)

        # Calculate total portfolio value
        total_value = Decimal(0)
        for entry in entries:
            if entry.coin and entry.coin.current_price:
                entry_value = entry.amount * entry.coin.current_price
                total_value += entry_value

        # Convert database entries to Pydantic models
        pydantic_entries = [PortfolioEntryResponse.model_validate(entry, from_attributes=True) for entry in entries]

        # Create a PortfolioSummary instance
        summary = PortfolioSummary(total_value_usd=total_value, entries=pydantic_entries)

        logger.info(f"Portfolio total value: {total_value} USD with {summary.total_coins} coins")
        return summary

    async def add_coin_to_portfolio(self, db: AsyncSession, entry_data: PortfolioEntryCreate) -> PortfolioEntry:
        """Add a coin to the portfolio using nested transactions for isolation."""
        logger.info(f"Adding coin {entry_data.coin_id} to portfolio with amount {entry_data.amount}")

        # First transaction: ensure the coin exists
        async with db.begin_nested():
            coin = await PortfolioRepository.get_coin(db, entry_data.coin_id)

            if not coin:
                logger.debug(f"Coin {entry_data.coin_id} not found in database, fetching from CoinGecko")
                coin_model = await coingecko_service.get_coin_details(entry_data.coin_id)
                coin = await PortfolioRepository.create_coin(db, coin_model.model_dump())
                logger.debug(f"Created new coin record for {coin.name} ({coin.symbol})")

        # Second transaction: handle portfolio entry (create or update)
        async with db.begin_nested():
            # Check if entry exists
            existing_entry = await PortfolioRepository.get_entry_by_coin_id(db, entry_data.coin_id)

            if existing_entry:
                # Update existing entry
                logger.info(f"Coin {entry_data.coin_id} already in portfolio, updating amount")
                old_amount = existing_entry.amount
                # Use existing and new amount directly, avoiding float conversion
                total_amount = existing_entry.amount + entry_data.amount
                await PortfolioRepository.update_entry_amount(db, existing_entry, total_amount)
                logger.info(f"Updated portfolio entry: {old_amount} → {existing_entry.amount}")
            else:
                # Create new entry
                logger.info(f"Creating new portfolio entry for {coin.name}")
                await PortfolioRepository.create_portfolio_entry(db, entry_data.coin_id, entry_data.amount)

        # Final query to get a clean, fully loaded entry to return
        return await PortfolioRepository.get_refreshed_entry(db, entry_data.coin_id)

    async def update_portfolio_entry(
        self, db: AsyncSession, entry_id: int, entry_data: PortfolioEntryUpdate
    ) -> Optional[PortfolioEntry]:
        """Update a portfolio entry using nested transactions."""
        logger.info(f"Updating portfolio entry {entry_id} with amount {entry_data.amount}")

        # Transaction: find and update the entry
        async with db.begin_nested():
            # Find the entry
            entry = await PortfolioRepository.get_entry_by_id(db, entry_id)

            if not entry:
                logger.warning(f"Portfolio entry {entry_id} not found")
                return None

            # Update the entry
            old_amount = entry.amount
            await PortfolioRepository.update_entry_amount(db, entry, entry_data.amount)
            logger.info(f"Updated portfolio entry {entry_id} amount: {old_amount} → {entry.amount}")

        # Get a fresh copy of the entry with all relationships loaded
        return await PortfolioRepository.get_refreshed_entry_by_id(db, entry_id)

    async def remove_portfolio_entry(self, db: AsyncSession, entry_id: int) -> bool:
        """Remove a coin from the portfolio using nested transaction."""
        logger.info(f"Removing portfolio entry {entry_id}")

        # Transaction: find and delete the entry
        async with db.begin_nested():
            # Find the entry
            entry = await PortfolioRepository.get_entry_by_id(db, entry_id)

            if not entry:
                logger.warning(f"Portfolio entry {entry_id} not found for removal")
                return False

            # Delete the entry
            await PortfolioRepository.delete_entry(db, entry)
            logger.info(f"Portfolio entry {entry_id} removed successfully")

        return True

    async def refresh_coin_prices(self, db: AsyncSession) -> int:
        """Refresh all coin prices in the portfolio using nested transactions."""
        logger.info("Refreshing coin prices")

        # First transaction: get all coins in the portfolio
        async with db.begin_nested():
            coins = await PortfolioRepository.get_portfolio_coins(db)
            logger.info(f"Found {len(coins)} coins in portfolio to refresh")

        # Update each coin's price in separate transactions
        updated_count = 0
        for coin in coins:
            try:
                async with db.begin_nested():
                    coin_model = await coingecko_service.get_coin_details(coin.id)

                    if coin_model.current_price is not None:
                        old_price = coin.current_price
                        await PortfolioRepository.update_coin_price(
                            db, coin, coin_model.current_price, coin_model.price_change_percentage_24h
                        )
                        updated_count += 1
                        logger.debug(f"Updated price for {coin.id}: {old_price} → {coin_model.current_price} USD")
                        logger.debug(f"Updated price change for {coin.id}: {coin.price_change_percentage_24h}%")
                    else:
                        logger.warning(f"No price data available for {coin.id}")
            except Exception as e:
                logger.error(f"Error updating price for {coin.id}: {str(e)}")

        logger.info(f"Updated prices for {updated_count} coins")
        return updated_count


# Create a global portfolio service instance
portfolio_service = PortfolioService()
