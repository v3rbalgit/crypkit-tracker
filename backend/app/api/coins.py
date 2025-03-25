"""API endpoints for coin operations."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import PortfolioEntry
from app.schemas.models import CoinDetail, CoinBase, CoinSearchResponse, CoinSearchResults
from app.services.coingecko import coingecko_service

router = APIRouter(prefix="/coins", tags=["coins"])


@router.get("/", response_model=List[CoinBase])
async def get_coins(search: Optional[str] = None):
    """Get a list of coins, optionally filtered by search query.

    Args:
        search: Optional search query

    Returns:
        List of coins
    """
    if search:
        results, _ = await coingecko_service.search_coins(search)
        return results

    # If no search, return a paginated list from CoinGecko
    coins_list = await coingecko_service.get_coins_list()
    return coins_list


@router.get("/{coin_id}", response_model=CoinDetail)
async def get_coin(coin_id: str):
    """Get detailed information for a specific coin.

    Args:
        coin_id: CoinGecko coin ID

    Returns:
        Coin details
    """
    try:
        coin_detail = await coingecko_service.get_coin_details(coin_id)
        return coin_detail

    except ValidationError as e:
        # Handle validation errors when parsing API response
        raise HTTPException(status_code=422, detail=f"Invalid data from API: {str(e)}")
    except Exception as e:
        # Handle other errors, like coin not found
        raise HTTPException(status_code=404, detail=f"Coin not found: {str(e)}")


@router.get("/search/", response_model=CoinSearchResults)
async def search_coins(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    db: AsyncSession = Depends(get_db),
):
    """Search for coins by name or symbol.

    Args:
        query: Search query (coin name or symbol)
        limit: Maximum number of results to return
        db: Database session

    Returns:
        Search results containing matching coins
    """
    try:
        # Get search results as pydantic models
        results, total = await coingecko_service.search_coins(query)

        # Limit the results
        limited_results = results[:limit]

        # Convert CoinBase to CoinSearchResponse with in_portfolio=False
        search_results = [
            CoinSearchResponse(id=coin.id, symbol=coin.symbol, name=coin.name, in_portfolio=False)
            for coin in limited_results
        ]

        # Check which coins are already in the portfolio
        if search_results:
            # Get IDs of coins in the portfolio
            portfolio_query = select(PortfolioEntry.coin_id)
            result = await db.execute(portfolio_query)
            portfolio_coin_ids = set(result.scalars().all())

            # Mark coins that are already in the portfolio
            for coin in search_results:
                coin.in_portfolio = coin.id in portfolio_coin_ids

        # Create the response model
        return CoinSearchResults(results=search_results, total=total)

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching coins: {str(e)}")
