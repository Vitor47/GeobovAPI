"""Add user_companies membership table for multi-farm farmers.

Revision ID: 20260728_user_companies
Revises: 20260728_gateways
Create Date: 2026-07-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "20260728_user_companies"
down_revision: Union[str, Sequence[str], None] = "20260728_gateways"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if "user_companies" not in tables:
        op.create_table(
            "user_companies",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(
                ["company_id"], ["companies.id"], ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("user_id", "company_id"),
        )
        op.create_index(
            "ix_user_companies_company_id",
            "user_companies",
            ["company_id"],
            unique=False,
        )

        # Backfill memberships from existing default company_id values.
        op.execute("""
        INSERT INTO user_companies (user_id, company_id)
        SELECT id, company_id
        FROM users
        WHERE company_id IS NOT NULL
        ON CONFLICT DO NOTHING
        """)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()
    if "user_companies" in tables:
        op.drop_index("ix_user_companies_company_id", table_name="user_companies")
        op.drop_table("user_companies")
