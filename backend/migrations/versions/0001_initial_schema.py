"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-11-13
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

WATCH_STATUS = sa.Enum(
    "watching",
    "completed",
    "planned",
    "dropped",
    name="watch_status",
    native_enum=False,
    create_constraint=True,
    length=16,
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("discord_id", sa.String(length=32), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("avatar", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_login", sa.DateTime(), nullable=False),
        sa.Column("discord_access_token", sa.Text(), nullable=True),
        sa.Column("discord_refresh_token", sa.Text(), nullable=True),
        sa.Column("discord_token_expires_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("discord_id", name=op.f("pk_users")),
    )
    op.create_table(
        "tvshows",
        sa.Column("imdb", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("image", sa.String(length=512), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("tvmaze_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("imdb", name=op.f("pk_tvshows")),
        sa.UniqueConstraint("tvmaze_id", name=op.f("uq_tvshows_tvmaze_id")),
    )
    op.create_table(
        "movies",
        sa.Column("imdb", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("image", sa.String(length=512), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("imdb", name=op.f("pk_movies")),
    )
    op.create_table(
        "sessions",
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("discord_id", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("device_info", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(
            ["discord_id"],
            ["users.discord_id"],
            name=op.f("fk_sessions_discord_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("session_id", name=op.f("pk_sessions")),
    )
    op.create_index(op.f("ix_sessions_discord_id"), "sessions", ["discord_id"])
    op.create_table(
        "tvlists",
        sa.Column("tvlist_id", sa.String(length=36), nullable=False),
        sa.Column("discord_id", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(
            ["discord_id"],
            ["users.discord_id"],
            name=op.f("fk_tvlists_discord_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("tvlist_id", name=op.f("pk_tvlists")),
        sa.UniqueConstraint("discord_id", name=op.f("uq_tvlists_discord_id")),
    )
    op.create_table(
        "movielists",
        sa.Column("movielist_id", sa.String(length=36), nullable=False),
        sa.Column("discord_id", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(
            ["discord_id"],
            ["users.discord_id"],
            name=op.f("fk_movielists_discord_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("movielist_id", name=op.f("pk_movielists")),
        sa.UniqueConstraint("discord_id", name=op.f("uq_movielists_discord_id")),
    )
    op.create_table(
        "episodes",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("tvshow_imdb", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("image", sa.String(length=512), nullable=True),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tvshow_imdb"],
            ["tvshows.imdb"],
            name=op.f("fk_episodes_tvshow_imdb_tvshows"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_episodes")),
    )
    op.create_index(op.f("ix_episodes_tvshow_imdb"), "episodes", ["tvshow_imdb"])
    op.create_table(
        "user_tvshows",
        sa.Column("tvlist_id", sa.String(length=36), nullable=False),
        sa.Column("imdb", sa.String(length=16), nullable=False),
        sa.Column("status", WATCH_STATUS, nullable=False),
        sa.Column("current_episode", sa.Integer(), nullable=True),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["current_episode"],
            ["episodes.id"],
            name=op.f("fk_user_tvshows_current_episode_episodes"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["imdb"], ["tvshows.imdb"], name=op.f("fk_user_tvshows_imdb_tvshows")
        ),
        sa.ForeignKeyConstraint(
            ["tvlist_id"],
            ["tvlists.tvlist_id"],
            name=op.f("fk_user_tvshows_tvlist_id_tvlists"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("tvlist_id", "imdb", name=op.f("pk_user_tvshows")),
    )
    op.create_table(
        "user_movies",
        sa.Column("movielist_id", sa.String(length=36), nullable=False),
        sa.Column("imdb", sa.String(length=16), nullable=False),
        sa.Column("status", WATCH_STATUS, nullable=False),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["imdb"], ["movies.imdb"], name=op.f("fk_user_movies_imdb_movies")
        ),
        sa.ForeignKeyConstraint(
            ["movielist_id"],
            ["movielists.movielist_id"],
            name=op.f("fk_user_movies_movielist_id_movielists"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("movielist_id", "imdb", name=op.f("pk_user_movies")),
    )


def downgrade() -> None:
    op.drop_table("user_movies")
    op.drop_table("user_tvshows")
    op.drop_index(op.f("ix_episodes_tvshow_imdb"), table_name="episodes")
    op.drop_table("episodes")
    op.drop_table("movielists")
    op.drop_table("tvlists")
    op.drop_index(op.f("ix_sessions_discord_id"), table_name="sessions")
    op.drop_table("sessions")
    op.drop_table("movies")
    op.drop_table("tvshows")
    op.drop_table("users")
