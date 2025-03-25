"""initial schema

Revision ID: a8c4e573f507
Revises:
Create Date: 2025-03-25 16:50:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.sql import func

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a8c4e573f507"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create coins table with all metadata fields
    op.create_table(
        "coins",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("current_price", sa.REAL(precision=10, asdecimal=True, decimal_return_scale=8), nullable=True),
        sa.Column("price_change_percentage_24h", sa.REAL, nullable=True),
        sa.Column("market_cap", sa.REAL(precision=16, asdecimal=True, decimal_return_scale=2), nullable=True),
        sa.Column("market_cap_rank", sa.Integer(), nullable=True),
        sa.Column("circulating_supply", sa.REAL(precision=16, asdecimal=True, decimal_return_scale=2), nullable=True),
        sa.Column("max_supply", sa.REAL(precision=16, asdecimal=True, decimal_return_scale=2), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("last_updated", sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_coins_id"), "coins", ["id"], unique=False)
    op.create_index(op.f("ix_coins_name"), "coins", ["name"], unique=False)
    op.create_index(op.f("ix_coins_symbol"), "coins", ["symbol"], unique=False)

    # Create portfolio_entries table
    op.create_table(
        "portfolio_entries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("coin_id", sa.String(), nullable=False),
        sa.Column("amount", sa.REAL(precision=16, asdecimal=True, decimal_return_scale=2), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["coin_id"],
            ["coins.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_portfolio_entries_coin_id"), "portfolio_entries", ["coin_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_portfolio_entries_coin_id"), table_name="portfolio_entries")
    op.drop_table("portfolio_entries")
    op.drop_index(op.f("ix_coins_symbol"), table_name="coins")
    op.drop_index(op.f("ix_coins_name"), table_name="coins")
    op.drop_index(op.f("ix_coins_id"), table_name="coins")
    op.drop_table("coins")
