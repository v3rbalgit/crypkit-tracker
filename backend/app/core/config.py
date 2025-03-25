"""Application configuration settings with validation.

This module defines the application settings using Pydantic for validation,
environment variable loading, and type safety. It centralizes all configuration
in one place and provides proper defaults and validation.
"""

from typing import Any

from pydantic import (
    Field,
    PostgresDsn,
    RedisDsn,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    # Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # FastAPI settings
    API_PREFIX: str = Field(default="/api", description="API prefix for all routes")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    PROJECT_NAME: str = Field(default="CrypKit Tracker", description="Project name used in documentation")
    VERSION: str = Field(default="0.1.0", description="API version number")

    # PostgreSQL settings
    POSTGRES_USER: str = Field(default="crypkit", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(default="crypkit_password", description="PostgreSQL password")
    POSTGRES_DB: str = Field(default="tracker", description="PostgreSQL database name")
    POSTGRES_HOST: str = Field(default="postgres", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")
    DATABASE_URL: PostgresDsn | None = Field(
        default=None, description="Database connection string (built automatically if not provided)"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str | None, info: Any) -> Any:
        """Assemble database URL if not provided."""
        if isinstance(v, str) and v != "":
            return v

        values = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            port=values.get("POSTGRES_PORT"),
            path=values.get("POSTGRES_DB"),
        )

    # Redis settings
    REDIS_HOST: str = Field(default="redis")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)
    REDIS_URL: RedisDsn | None = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v: str | None, info: Any) -> Any:
        """Assemble Redis URL if not provided."""
        if isinstance(v, str) and v != "":
            return v

        values = info.data
        return RedisDsn.build(
            scheme="redis",
            host=values.get("REDIS_HOST"),
            port=values.get("REDIS_PORT"),
            path=values.get("REDIS_DB") or str(0),
        )

    # CoinGecko API settings
    COINGECKO_API_URL: str = Field(default="https://api.coingecko.com/api/v3", description="CoinGecko API base URL")
    COINGECKO_API_KEY: str | None = Field(default=None, description="CoinGecko API key for authenticated requests")
    COINGECKO_CACHE_TTL: int = Field(default=86400, description="Cache TTL in seconds (default: 24 hours)")

    @field_validator("COINGECKO_API_KEY")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate that the API key is provided."""
        if not v or v.strip() == "":
            raise ValueError("CoinGecko API key is required")
        return v


# Create a global settings object
settings = Settings()
