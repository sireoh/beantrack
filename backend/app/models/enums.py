from enum import StrEnum

from sqlalchemy import Enum


class WatchStatus(StrEnum):
    WATCHING = "watching"
    COMPLETED = "completed"
    PLANNED = "planned"
    DROPPED = "dropped"


def watch_status_column_type() -> Enum:
    """Stored as VARCHAR + CHECK constraint (SQLite has no native enums), using the values."""
    return Enum(
        WatchStatus,
        name="watch_status",
        native_enum=False,
        create_constraint=True,
        length=16,
        values_callable=lambda enum_cls: [member.value for member in enum_cls],
        validate_strings=True,
    )
