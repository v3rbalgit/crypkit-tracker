"""API endpoints for portfolio operations."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.models import (
    PortfolioEntryCreate,
    PortfolioEntryResponse,
    PortfolioEntryUpdate,
    PortfolioSummary,
)
from app.services.portfolio import portfolio_service
from app.repositories.portfolio_repository import PortfolioRepository

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/refresh-prices")
async def refresh_coin_prices(db: AsyncSession = Depends(get_db)):
    """Refresh all coin prices in the portfolio.

    Args:
        db: Database session

    Returns:
        Success message
    """
    updated_count = await portfolio_service.refresh_coin_prices(db)
    return {"detail": f"Updated prices for {updated_count} coins"}


@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(db: AsyncSession = Depends(get_db)):
    """Get portfolio summary with total value and statistics.

    Args:
        db: Database session

    Returns:
        Portfolio summary
    """
    # Get the portfolio summary directly from the service
    summary = await portfolio_service.get_portfolio_summary(db)

    # The service now returns a fully formed PortfolioSummary object
    return summary


@router.get("/{entry_id}", response_model=PortfolioEntryResponse)
async def get_portfolio_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific portfolio entry.

    Args:
        entry_id: Portfolio entry ID
        db: Database session

    Returns:
        Portfolio entry
    """
    entry = await PortfolioRepository.get_entry_by_id(db, entry_id)

    if not entry:
        raise HTTPException(status_code=404, detail="Portfolio entry not found")

    return PortfolioEntryResponse.model_validate(entry, from_attributes=True)


@router.put("/{entry_id}", response_model=PortfolioEntryResponse)
async def update_portfolio_entry(entry_id: int, entry_data: PortfolioEntryUpdate, db: AsyncSession = Depends(get_db)):
    """Update a portfolio entry.

    Args:
        entry_id: Portfolio entry ID
        entry_data: Updated portfolio entry data
        db: Database session

    Returns:
        Updated portfolio entry
    """
    db_entry = await portfolio_service.update_portfolio_entry(db, entry_id, entry_data)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Portfolio entry not found")

    # Convert to Pydantic model for response
    return PortfolioEntryResponse.model_validate(db_entry, from_attributes=True)


@router.delete("/{entry_id}")
async def remove_portfolio_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    """Remove a coin from the portfolio.

    Args:
        entry_id: Portfolio entry ID
        db: Database session

    Returns:
        Success message
    """
    success = await portfolio_service.remove_portfolio_entry(db, entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Portfolio entry not found")

    return {"detail": "Portfolio entry deleted successfully"}


@router.post("/", response_model=PortfolioEntryResponse)
async def add_coin_to_portfolio(entry_data: PortfolioEntryCreate, db: AsyncSession = Depends(get_db)):
    """Add a coin to the portfolio.

    Args:
        entry_data: Portfolio entry data
        db: Database session

    Returns:
        Created portfolio entry
    """
    try:
        db_entry = await portfolio_service.add_coin_to_portfolio(db, entry_data)
        # Convert to Pydantic model for response
        return PortfolioEntryResponse.model_validate(db_entry, from_attributes=True)
    except ValidationError as e:
        # Handle Pydantic validation errors specifically
        raise HTTPException(status_code=422, detail=f"Validation error: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add coin: {str(e)}")


@router.get("/", response_model=List[PortfolioEntryResponse])
async def get_portfolio(db: AsyncSession = Depends(get_db)):
    """Get all portfolio entries.

    Args:
        db: Database session

    Returns:
        List of portfolio entries
    """
    entries = await portfolio_service.get_portfolio_entries(db)
    return [PortfolioEntryResponse.model_validate(entry, from_attributes=True) for entry in entries]
