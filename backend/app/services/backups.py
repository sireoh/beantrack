"""Manual database snapshots to Backblaze B2, and restoring from them.

Independent of Litestream (which keeps streaming WAL changes); this works anywhere,
including Windows. Snapshots are gzip-compressed SQLite files under `BACKUP_PREFIX`.

- Backup uses `VACUUM INTO`, which writes a consistent copy while the app keeps running.
- Restore uses SQLite's online backup API to copy the snapshot *into* the live database,
  so open connections (and Litestream, if running) see the change through normal locking.
  A safety snapshot of the current database is uploaded first.
"""

import gzip
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

from app.clients.b2 import B2Client, B2File
from app.core.errors import ConflictError, InvalidRequestError, NotFoundError
from app.core.ids import new_id
from app.db.types import utcnow

BACKUP_PREFIX = "manual-backups/"
BACKUP_SUFFIX = ".db.gz"
CONTENT_TYPE = "application/gzip"
LOCK_TIMEOUT_SECONDS = 30


def create_backup(b2: B2Client, db_path: Path, *, label: str | None = None) -> B2File:
    """Snapshot the live database and upload it. Returns the stored file."""
    stamp = utcnow().strftime("%Y%m%dT%H%M%SZ")
    unique = new_id()[:8]  # two backups in the same second must not overwrite each other
    suffix = f"-{label}" if label else ""
    name = f"{BACKUP_PREFIX}beantrack-{stamp}-{unique}{suffix}{BACKUP_SUFFIX}"
    return b2.upload(name, gzip.compress(_snapshot(db_path)), CONTENT_TYPE)


def list_backups(b2: B2Client) -> list[B2File]:
    """Manual backups, newest first."""
    files = [f for f in b2.list_files(BACKUP_PREFIX) if f.name.endswith(BACKUP_SUFFIX)]
    return sorted(files, key=lambda f: f.uploaded_at, reverse=True)


def delete_backup(b2: B2Client, file_id: str) -> B2File:
    """Delete one manual backup. Only files under BACKUP_PREFIX are looked up here, so
    Litestream's replica (stored under its own path) can never be deleted this way."""
    backup = next((f for f in list_backups(b2) if f.id == file_id), None)
    if backup is None:
        raise NotFoundError("Backup not found")
    b2.delete(backup)
    return backup


def restore_backup(b2: B2Client, db_path: Path, name: str) -> tuple[B2File, B2File]:
    """Overwrite the live database with backup `name`. Returns (restored, safety backup)."""
    if not name.startswith(BACKUP_PREFIX) or not name.endswith(BACKUP_SUFFIX) or ".." in name:
        raise InvalidRequestError("Not a manual backup name")
    restored = next((f for f in b2.list_files(BACKUP_PREFIX) if f.name == name), None)
    if restored is None:
        raise InvalidRequestError(f"Backup {name} does not exist")

    try:
        data = gzip.decompress(b2.download(name))
    except (OSError, EOFError) as exc:
        raise InvalidRequestError("Backup file is not a valid gzip archive") from exc

    with tempfile.TemporaryDirectory() as tmp:
        snapshot_path = Path(tmp) / "restore.db"
        snapshot_path.write_bytes(data)
        with closing(sqlite3.connect(snapshot_path)) as snapshot:
            _check_restorable(snapshot, db_path)
            safety = create_backup(b2, db_path, label="pre-restore")
            with closing(sqlite3.connect(db_path, timeout=LOCK_TIMEOUT_SECONDS)) as live:
                snapshot.backup(live)
    return restored, safety


def _snapshot(db_path: Path) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "snapshot.db"
        with closing(sqlite3.connect(db_path, timeout=LOCK_TIMEOUT_SECONDS)) as conn:
            conn.execute("VACUUM INTO ?", (str(out),))
        return out.read_bytes()


def _check_restorable(snapshot: sqlite3.Connection, db_path: Path) -> None:
    try:
        result = snapshot.execute("PRAGMA quick_check").fetchone()
    except sqlite3.DatabaseError as exc:
        raise InvalidRequestError("Backup is not a SQLite database") from exc
    if not result or result[0] != "ok":
        raise InvalidRequestError("Backup failed SQLite's integrity check")

    with closing(sqlite3.connect(db_path, timeout=LOCK_TIMEOUT_SECONDS)) as live:
        live_version = _schema_version(live)
    snapshot_version = _schema_version(snapshot)
    if snapshot_version != live_version:
        raise ConflictError(
            f"Backup uses database schema {snapshot_version or 'unknown'}, but the app is on "
            f"{live_version or 'unknown'}. Restore it with a matching app version."
        )


def _schema_version(conn: sqlite3.Connection) -> str | None:
    """The Alembic revision recorded in a database, if any."""
    try:
        row = conn.execute("SELECT version_num FROM alembic_version").fetchone()
    except sqlite3.OperationalError:
        return None
    return str(row[0]) if row else None
