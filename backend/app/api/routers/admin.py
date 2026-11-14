"""Admin-only routes. The router-level dependency protects every /api/admin/* path."""

from typing import cast

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import Engine

from app.api.deps import B2, DbSession, SettingsDep, require_admin
from app.clients.b2 import B2File
from app.schemas.admin import BackupOut, RestoreOut, RestoreRequest
from app.services import backups as backup_service

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def _out(file: B2File) -> BackupOut:
    return BackupOut(name=file.name, size=file.size, created_at=file.uploaded_at)


@router.post("/backup", response_model=BackupOut, status_code=status.HTTP_201_CREATED)
def create_backup(b2: B2, settings: SettingsDep) -> BackupOut:
    """Snapshot the SQLite database (VACUUM INTO) and upload it to the B2 bucket."""
    return _out(backup_service.create_backup(b2, settings.database_path))


@router.get("/backups", response_model=list[BackupOut])
def list_backups(b2: B2) -> list[BackupOut]:
    """Manual backups in the bucket, newest first."""
    return [_out(f) for f in backup_service.list_backups(b2)]


@router.post("/restore", response_model=RestoreOut)
def restore_backup(
    body: RestoreRequest, request: Request, b2: B2, settings: SettingsDep, db: DbSession
) -> RestoreOut:
    """Replace the live database with a manual backup (a safety snapshot is taken first)."""
    db.close()  # release this request's connection before the database is overwritten
    restored, safety = backup_service.restore_backup(b2, settings.database_path, body.name)
    # Pooled connections would otherwise keep page caches from before the restore.
    cast(Engine, request.app.state.engine).dispose()
    return RestoreOut(restored=_out(restored), safety_backup=_out(safety))
