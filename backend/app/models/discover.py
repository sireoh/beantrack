"""Cached TMDB /discover pages (one row per page), shared by every visitor."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.types import UTCDateTime


class _DiscoverPage:
    page: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    # TMDB's `results` array for this page, as returned.
    results: Mapped[list[dict[str, Any]]] = mapped_column(JSON)
    total_pages: Mapped[int] = mapped_column(Integer)
    fetched_at: Mapped[datetime] = mapped_column(UTCDateTime())


class DiscoverCacheTv(_DiscoverPage, Base):
    __tablename__ = "discovercache_tv"


class DiscoverCacheMovie(_DiscoverPage, Base):
    __tablename__ = "discovercache_movies"
