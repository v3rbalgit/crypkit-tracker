"""Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import coins, portfolio
from app.core.config import settings
from app.services.coingecko import coingecko_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup: Initialize services and fetch initial data
    try:
        # Prefetch coins list to cache
        await coingecko_service.get_coins_list(force_refresh=True)
    except Exception as e:
        print(f"Warning: Failed to prefetch coins list: {str(e)}")

    yield

    # Shutdown: Close service connections
    if coingecko_service.session:
        await coingecko_service.close()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Cryptocurrency Portfolio Tracker API",
        version=settings.VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For production, this should be restricted
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add API routers
    app.include_router(coins.router, prefix=settings.API_PREFIX)
    app.include_router(portfolio.router, prefix=settings.API_PREFIX)

    @app.get("/")
    async def root():
        """Root endpoint for redirection."""
        return {"status": "ok", "message": "CrypKit Tracker API is running"}

    @app.get("/api/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        return {"status": "ok", "service": "crypkit-tracker-api"}

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
