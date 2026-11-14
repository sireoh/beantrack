"""Store current TV episode as a zero-based index."""

from alembic import op
import sqlalchemy as sa


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE user_tvshows
            SET current_episode = COALESCE(
                (
                    SELECT COUNT(*)
                    FROM episodes earlier
                    JOIN episodes selected
                      ON selected.id = user_tvshows.current_episode
                    WHERE earlier.tvshow_imdb = selected.tvshow_imdb
                      AND (
                        earlier.season < selected.season
                        OR (
                            earlier.season = selected.season
                            AND (
                                earlier.number < selected.number
                                OR (
                                    earlier.number = selected.number
                                    AND earlier.id < selected.id
                                )
                            )
                        )
                    )
                ),
                0
            )
            """
        )
    )
    with op.batch_alter_table("user_tvshows") as batch:
        batch.drop_constraint("fk_user_tvshows_current_episode_episodes", type_="foreignkey")
        batch.alter_column("current_episode", existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("user_tvshows") as batch:
        batch.alter_column("current_episode", existing_type=sa.Integer(), nullable=True)
        batch.create_foreign_key(
            "fk_user_tvshows_current_episode_episodes",
            "episodes",
            ["current_episode"],
            ["id"],
            ondelete="SET NULL",
        )
