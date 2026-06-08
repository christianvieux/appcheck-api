"""rename saved tests to smoke tests

Revision ID: 9b2c4d6e8f10
Revises: 380edd90fc80
Create Date: 2026-06-07 19:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b2c4d6e8f10"
down_revision: Union[str, Sequence[str], None] = "380edd90fc80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Upgrade schema."""
    if _table_exists("saved_tests") and not _table_exists("smoke_tests"):
        op.rename_table("saved_tests", "smoke_tests")


def downgrade() -> None:
    """Downgrade schema."""
    if _table_exists("smoke_tests") and not _table_exists("saved_tests"):
        op.rename_table("smoke_tests", "saved_tests")
