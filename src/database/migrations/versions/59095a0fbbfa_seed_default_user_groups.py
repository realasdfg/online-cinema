"""Seed default user groups

Revision ID: 59095a0fbbfa
Revises: f9eea22f23b1
Create Date: 2026-10-07 17:06:56.806373

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "59095a0fbbfa"
down_revision: Union[str, Sequence[str], None] = "f9eea22f23b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_groups_table = sa.table(
    "user_groups",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
)


def upgrade() -> None:
    op.bulk_insert(
        user_groups_table,
        [
            {"name": "USER"},
            {"name": "MODERATOR"},
            {"name": "ADMIN"},
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM user_groups WHERE name IN ('USER', 'MODERATOR', 'ADMIN')")
