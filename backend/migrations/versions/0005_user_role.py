"""Add a role (user/admin) to users."""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=16), nullable=False, server_default="user"),
    )


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("role")
