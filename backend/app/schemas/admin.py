from datetime import datetime

from app.schemas.common import ORMModel, RequestModel


class BackupOut(ORMModel):
    """A manual database snapshot stored in the B2 bucket."""

    name: str
    size: int  # bytes (gzip-compressed)
    created_at: datetime


class RestoreRequest(RequestModel):
    name: str


class RestoreOut(ORMModel):
    restored: BackupOut
    # Snapshot of the database taken just before it was overwritten.
    safety_backup: BackupOut
