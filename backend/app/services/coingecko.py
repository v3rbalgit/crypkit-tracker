"""CoinGecko API service."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from aiohttp.client_exceptions import ClientError
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.models import CoinBase, CoinDetail
from app.services.redis_cache import redis_cache
from app.utils.logger import get_logger
from app.utils.rate_limiter import coingecko_rate_limiter

logger = get_logger(__name__)


class CoinGeckoService:
    """Service for interacting with the CoinGecko API."""

    # Redis cache keys
    COINS_LIST_CACHE_KEY = "coingecko:coins:list"
    COIN_DETAIL_CACHE_PREFIX = "coingecko:coin:"

    def __init__(self):
        """Initialize the CoinGecko service."""
        self.base_url = settings.COINGECKO_API_URL
        self.api_key = settings.COINGECKO_API_KEY
        self.cache_ttl = settings.COINGECKO_CACHE_TTL
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info("CoinGecko service initialized")

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create an aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _api_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make a rate-limited request to the CoinGecko API.

        Args:
            endpoint: API endpoint path
            params: Optional query parameters

        Returns:
            JSON response (can be dict or list depending on endpoint)
        """
        try:
            # Wait for rate limiter before making the request
            await coingecko_rate_limiter.acquire()

            session = await self._get_session()
            url = f"{self.base_url}/{endpoint}"

            # Set up headers with API key if available
            headers = {}
            if self.api_key:
                headers["x-cg-demo-api-key"] = self.api_key

            logger.debug(f"Making request to: {url}")

            async with session.get(url, params=params, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                return data

        except ClientError as e:
            logger.error(f"CoinGecko API error: {str(e)}")
            raise

    async def get_coins_list(self, force_refresh: bool = False) -> List[CoinBase]:
        """Get a list of all available coins.

        Args:
            force_refresh: If True, bypasses cache and fetches fresh data

        Returns:
            List of CoinBase objects with id, symbol, and name
        """
        # Try to get from cache first
        if not force_refresh:
            cached_data = await redis_cache.get(self.COINS_LIST_CACHE_KEY)
            if cached_data:
                # Convert cached dictionary data to Pydantic models
                return [CoinBase.model_validate(coin) for coin in cached_data]

        # Fetch from API if not in cache or force refresh
        coins_list_data: List[Dict[str, Any]] = await self._api_request("coins/list")

        # Cache the data (still as dictionary for compatibility)
        await redis_cache.set(self.COINS_LIST_CACHE_KEY, coins_list_data, ttl=self.cache_ttl)

        # Convert to Pydantic models with better error handling
        coins_list: List[CoinBase] = []
        for coin_data in coins_list_data:
            try:
                coin_model = CoinBase.model_validate(coin_data)
                coins_list.append(coin_model)
            except ValidationError as e:
                logger.warning(f"Failed to parse coin data: {str(e)}")

        return coins_list

    async def get_coin_details(self, coin_id: str) -> CoinDetail:
        """Get detailed information for a specific coin.

        Args:
            coin_id: CoinGecko coin ID

        Returns:
            CoinDetail object with coin details
        """
        cache_key = f"{self.COIN_DETAIL_CACHE_PREFIX}{coin_id}"

        # Try to get from cache first
        cached_data = await redis_cache.get(cache_key)
        if cached_data:
            # Convert cached dictionary to Pydantic model
            try:
                return CoinDetail(**cached_data)
            except ValidationError as e:
                logger.warning(f"Failed to parse cached coin data: {str(e)}")
                # Continue to fetch fresh data if parsing fails

        # Fetch from API if not in cache or parsing failed
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
        }

        coin_api_data = await self._api_request(f"coins/{coin_id}", params)

        # Prepare data for Pydantic model
        processed_data = {
            "id": coin_api_data.get("id", ""),
            "symbol": coin_api_data.get("symbol", ""),
            "name": coin_api_data.get("name", ""),
            "current_price": coin_api_data.get("market_data", {}).get("current_price", {}).get("usd"),
            "market_cap": coin_api_data.get("market_data", {}).get("market_cap", {}).get("usd"),
            "market_cap_rank": coin_api_data.get("market_data", {}).get("market_cap_rank"),
            "price_change_percentage_24h": coin_api_data.get("market_data", {}).get("price_change_percentage_24h"),
            "circulating_supply": coin_api_data.get("market_data", {}).get("circulating_supply"),
            "max_supply": coin_api_data.get("market_data", {}).get("max_supply"),
            "image_url": coin_api_data.get("image", {}).get("large"),
            "description": coin_api_data.get("description", {}).get("en"),
            "last_updated": coin_api_data.get("last_updated"),
            "created_at": datetime.now(timezone.utc),
        }

        # Create Pydantic model using model_validate
        try:
            coin_detail = CoinDetail.model_validate(processed_data)
        except ValidationError as e:
            logger.error(f"Failed to create CoinDetail model: {str(e)}")
            raise

        # Cache the model (as dict for compatibility)
        model_dict = coin_detail.model_dump()
        await redis_cache.set(cache_key, model_dict, ttl=5)  # 5 seconds

        return coin_detail

    async def search_coins(self, query: str) -> Tuple[List[CoinBase], int]:
        """Search coins by name or symbol.

        Args:
            query: Search query string

        Returns:
            Tuple of (matching coins list, total count)
        """
        # Get all coins list from cache or API (now as CoinBase objects)
        coins_list = await self.get_coins_list()

        # Perform case-insensitive search on name and symbol
        query = query.lower()
        results = [coin for coin in coins_list if query in coin.name.lower() or query in coin.symbol.lower()]

        return results, len(results)

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()


# Create a global CoinGecko service instance
coingecko_service = CoinGeckoService()
