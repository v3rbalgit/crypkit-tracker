"""Redis cache service."""

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
from redis.asyncio.client import Redis

from app.core.config import settings


def json_serializer(obj):
    """Custom JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, Decimal):
        return float(obj)  # Convert Decimal to float
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO format string
    raise TypeError(f"Type {type(obj)} not serializable")


class RedisCache:
    """Redis cache service for storing and retrieving data."""

    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client: Redis = redis.from_url(str(settings.REDIS_URL))

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a value in Redis cache.

        Args:
            key: Redis key
            value: Value to store (will be JSON serialized)
            ttl: Time to live in seconds (defaults to None - no expiration)
        """
        serialized_value = json.dumps(value, default=json_serializer)
        await self.redis_client.set(key, serialized_value, ex=ttl)

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis cache.

        Args:
            key: Redis key

        Returns:
            Deserialized value if found, None otherwise
        """
        value = await self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None

    async def delete(self, key: str) -> None:
        """Delete a key from Redis cache.

        Args:
            key: Redis key
        """
        await self.redis_client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis cache.

        Args:
            key: Redis key

        Returns:
            True if key exists, False otherwise
        """
        return await self.redis_client.exists(key) > 0

    async def search(self, pattern: str) -> List[Dict[str, Any]]:
        """Search for keys matching pattern and return their values.

        Args:
            pattern: Redis key pattern (e.g., "coins:*")

        Returns:
            List of deserialized values
        """
        keys = await self.redis_client.keys(pattern)

        if not keys:
            return []

        values = await self.redis_client.mget(keys)
        return [json.loads(value) for value in values if value]


# Create a global Redis cache instance
redis_cache = RedisCache()
