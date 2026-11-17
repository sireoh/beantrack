"""Discover (TMDB) page cache, TMDB ids on the catalog, and the login IP on sessions."""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def _cache_table(name: str) -> None:
    op.create_table(
        name,
        sa.Column("page", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("results", sa.JSON(), nullable=False),
        sa.Column("total_pages", sa.Integer(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("page", name=op.f(f"pk_{name}")),
    )


def upgrade() -> None:
    _cache_table("discovercache_tv")
    _cache_table("discovercache_movies")

    op.add_column("tvshows", sa.Column("tmdb_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_tvshows_tmdb_id"), "tvshows", ["tmdb_id"])
    op.add_column("movies", sa.Column("tmdb_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_movies_tmdb_id"), "movies", ["tmdb_id"])

    op.add_column("sessions", sa.Column("ip_address", sa.String(length=45), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("sessions") as batch:
        batch.drop_column("ip_address")
    op.drop_index(op.f("ix_movies_tmdb_id"), table_name="movies")
    with op.batch_alter_table("movies") as batch:
        batch.drop_column("tmdb_id")
    op.drop_index(op.f("ix_tvshows_tmdb_id"), table_name="tvshows")
    with op.batch_alter_table("tvshows") as batch:
        batch.drop_column("tmdb_id")
    op.drop_table("discovercache_movies")
    op.drop_table("discovercache_tv")
