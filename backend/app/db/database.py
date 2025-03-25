"""Database connection setup."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Create an async engine
engine = create_async_engine(str(settings.DATABASE_URL), echo=False)

# Create a session factory
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

# Create a base class for declarative models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting an async DB session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
