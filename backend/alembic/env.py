"""Alembic environment configuration."""

import asyncio
import psycopg2
from logging.config import fileConfig
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.db.database import Base
from app.db.models import Coin, PortfolioEntry  # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Set sqlalchemy.url from environment variables
section = config.config_ini_section
config.set_section_option(section, "POSTGRES_USER", settings.POSTGRES_USER)
config.set_section_option(section, "POSTGRES_PASSWORD", settings.POSTGRES_PASSWORD)
config.set_section_option(section, "POSTGRES_HOST", settings.POSTGRES_HOST)
config.set_section_option(section, "POSTGRES_PORT", str(settings.POSTGRES_PORT))
config.set_section_option(section, "POSTGRES_DB", settings.POSTGRES_DB)


# Function to create the database if it doesn't exist
def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    # Get database settings from settings
    db_user = settings.POSTGRES_USER
    db_pass = settings.POSTGRES_PASSWORD
    db_host = settings.POSTGRES_HOST
    db_port = settings.POSTGRES_PORT
    db_name = settings.POSTGRES_DB

    try:
        # Connection string for PostgreSQL server (without specific database)
        dsn = f"host={db_host} user={db_user} password={db_pass} port={db_port}"

        # Connect to PostgreSQL server (default database)
        conn = psycopg2.connect(dsn)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if our target database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()

        if not exists:
            print(f"Creating database '{db_name}'")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' created successfully")
        else:
            print(f"Database '{db_name}' already exists")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {str(e)}")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations within the provided connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    # Try to create the database before running migrations
    create_database_if_not_exists()

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
