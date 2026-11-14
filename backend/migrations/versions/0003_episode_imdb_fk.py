"""Rename the episode show foreign key to imdb."""

from alembic import op


revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_episodes_tvshow_imdb", table_name="episodes")
    with op.batch_alter_table("episodes") as batch:
        batch.alter_column("tvshow_imdb", new_column_name="imdb")
    op.create_index("ix_episodes_imdb", "episodes", ["imdb"])


def downgrade() -> None:
    op.drop_index("ix_episodes_imdb", table_name="episodes")
    with op.batch_alter_table("episodes") as batch:
        batch.alter_column("imdb", new_column_name="tvshow_imdb")
    op.create_index("ix_episodes_tvshow_imdb", "episodes", ["tvshow_imdb"])
