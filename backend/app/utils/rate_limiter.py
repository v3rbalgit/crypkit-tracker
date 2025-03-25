"""Rate limiter implementation using token bucket algorithm."""

import asyncio
import time

from app.utils.logger import get_logger

logger = get_logger(__name__)


class TokenBucketRateLimiter:
    """Token bucket rate limiter implementation.

    This implementation creates a bucket that fills with tokens at a constant rate.
    Each request consumes a token, and when no tokens are available, requests wait.
    """

    def __init__(self, rate: float = 0.5, max_tokens: int = 30):
        """Initialize the rate limiter.

        Args:
            rate: Tokens per second (default: 0.5, which is 30 per minute)
            max_tokens: Maximum tokens the bucket can hold
        """
        self.rate = rate  # Tokens per second
        self.max_tokens = max_tokens
        self.tokens = max_tokens  # Start with a full bucket
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
        logger.info(f"Rate limiter initialized with rate={rate} tokens/sec, max_tokens={max_tokens}")

    async def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill

        # Calculate new tokens based on rate and elapsed time
        new_tokens = elapsed * self.rate

        # Update token count, capped at max_tokens
        self.tokens = min(self.tokens + new_tokens, self.max_tokens)
        self.last_refill = now

        logger.debug(f"Refilled tokens. Current tokens: {self.tokens:.2f}")

    async def acquire(self, tokens: int = 1) -> None:
        """Acquire tokens from the bucket, waiting if necessary.

        Args:
            tokens: Number of tokens to acquire (default: 1)
        """
        if tokens > self.max_tokens:
            raise ValueError(f"Cannot acquire more than {self.max_tokens} tokens")

        # Use a lock to make this thread-safe
        async with self._lock:
            await self._refill()

            # If not enough tokens, calculate wait time and sleep
            if self.tokens < tokens:
                wait_time = (tokens - self.tokens) / self.rate
                logger.debug(f"Not enough tokens ({self.tokens:.2f}). Waiting: {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                # After sleeping, tokens should be available
                await self._refill()  # Refill again after waiting

            # Consume tokens
            self.tokens -= tokens
            logger.debug(f"Tokens acquired. Remaining: {self.tokens:.2f}")


# Global rate limiter instance for CoinGecko API
coingecko_rate_limiter = TokenBucketRateLimiter(rate=0.5, max_tokens=30)  # 30 requests per minute
