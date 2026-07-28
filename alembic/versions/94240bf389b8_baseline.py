"""Baseline revision recorded in existing databases.

This revision was applied historically (schema via create_all / earlier work)
but the migration file was not kept in the repository. Restored as an empty
stub so Alembic can locate the DB head and apply later upgrades.

Revision ID: 94240bf389b8
Revises:
Create Date: 2026-07-28
"""

from typing import Sequence, Union

revision: str = "94240bf389b8"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op: schema already exists on databases that stamped this revision."""


def downgrade() -> None:
    """No-op baseline."""
