"""Add cached current episode metadata to user TV entries."""

from alembic import op
import sqlalchemy as sa


revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "user_tvshows",
        sa.Column("current_episode_metadata", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_tvshows", "current_episode_metadata")
