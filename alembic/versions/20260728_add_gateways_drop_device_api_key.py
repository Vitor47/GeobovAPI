"""Add gateways table and drop devices.api_key.

Revision ID: 20260728_gateways
Revises: 94240bf389b8
Create Date: 2026-07-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "20260728_gateways"
down_revision: Union[str, Sequence[str], None] = "94240bf389b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if "gateways" not in tables:
        op.create_table(
            "gateways",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=True,
            ),
            sa.Column("serial_number", sa.String(), nullable=False),
            sa.Column("name", sa.String(), nullable=True),
            sa.Column("api_key", sa.String(), nullable=False),
            sa.Column("company_id", sa.Integer(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("api_key"),
            sa.UniqueConstraint("serial_number"),
        )
        op.create_index(op.f("ix_gateways_id"), "gateways", ["id"], unique=False)
        op.create_index(
            op.f("ix_gateways_serial_number"),
            "gateways",
            ["serial_number"],
            unique=True,
        )
        op.create_index(
            op.f("ix_gateways_api_key"),
            "gateways",
            ["api_key"],
            unique=True,
        )

    if "devices" in tables:
        device_columns = {col["name"] for col in inspector.get_columns("devices")}
        if "api_key" in device_columns:
            device_indexes = {idx["name"] for idx in inspector.get_indexes("devices")}
            if "ix_devices_api_key" in device_indexes:
                op.drop_index(op.f("ix_devices_api_key"), table_name="devices")
            # UniqueConstraint may also create devices_api_key_key
            for idx_name in list(device_indexes):
                if (
                    idx_name
                    and "api_key" in idx_name
                    and idx_name != "ix_devices_api_key"
                ):
                    op.drop_index(idx_name, table_name="devices")
            op.drop_column("devices", "api_key")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if "devices" in tables:
        device_columns = {col["name"] for col in inspector.get_columns("devices")}
        if "api_key" not in device_columns:
            op.add_column(
                "devices",
                sa.Column("api_key", sa.String(), nullable=False, server_default=""),
            )
            op.create_index(
                op.f("ix_devices_api_key"),
                "devices",
                ["api_key"],
                unique=True,
            )
            op.alter_column("devices", "api_key", server_default=None)

    if "gateways" in tables:
        op.drop_index(op.f("ix_gateways_api_key"), table_name="gateways")
        op.drop_index(op.f("ix_gateways_serial_number"), table_name="gateways")
        op.drop_index(op.f("ix_gateways_id"), table_name="gateways")
        op.drop_table("gateways")
