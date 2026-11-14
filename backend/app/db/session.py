"""Engine and session factories. SQLite is configured for WAL on every new connection."""

from pathlib import Path
from sqlite3 import Connection as SQLite3Connection
from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

BUSY_TIMEOUT_MS = 5000


def _set_sqlite_pragmas(dbapi_connection: Any, _connection_record: Any) -> None:
    if not isinstance(dbapi_connection, SQLite3Connection):
        return
    cursor = dbapi_connection.cursor()
    try:
        # WAL lets readers and a writer work concurrently, and is required by Litestream.
        cursor.execute("PRAGMA journal_mode=WAL")
        # Wait for a competing writer instead of failing immediately with "database is locked".
        cursor.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS}")
        # Safe with WAL and much faster than FULL.
        cursor.execute("PRAGMA synchronous=NORMAL")
        # SQLite ignores foreign keys unless asked.
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()


def build_engine(url: str) -> Engine:
    parsed = make_url(url)
    if parsed.get_backend_name() == "sqlite" and parsed.database not in (None, "", ":memory:"):
        Path(parsed.database).parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        url,
        # FastAPI runs sync endpoints in a thread pool, so connections cross threads.
        connect_args={"check_same_thread": False, "timeout": BUSY_TIMEOUT_MS / 1000},
    )
    event.listen(engine, "connect", _set_sqlite_pragmas)
    return engine


def build_sessionmaker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
