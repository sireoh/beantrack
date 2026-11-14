"""Per-user lists and progress rows. Chain: user -> tvlist -> user_tvshows -> tvshow -> episodes."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.ids import new_id
from app.db.base import Base
from app.db.types import UTCDateTime, utcnow
from app.models.enums import WatchStatus, watch_status_column_type

if TYPE_CHECKING:
    from app.models.media import Episode, Movie, TvShow
    from app.models.user import User


class TvList(Base):
    __tablename__ = "tvlists"

    tvlist_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    discord_id: Mapped[str] = mapped_column(
        ForeignKey("users.discord_id", ondelete="CASCADE"), unique=True
    )

    user: Mapped[User] = relationship(back_populates="tvlist")
    entries: Mapped[list[UserTvShow]] = relationship(
        back_populates="tvlist",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="UserTvShow.added_at",
    )


class MovieList(Base):
    __tablename__ = "movielists"

    movielist_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    discord_id: Mapped[str] = mapped_column(
        ForeignKey("users.discord_id", ondelete="CASCADE"), unique=True
    )

    user: Mapped[User] = relationship(back_populates="movielist")
    entries: Mapped[list[UserMovie]] = relationship(
        back_populates="movielist",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="UserMovie.added_at",
    )


class UserTvShow(Base):
    __tablename__ = "user_tvshows"

    tvlist_id: Mapped[str] = mapped_column(
        ForeignKey("tvlists.tvlist_id", ondelete="CASCADE"), primary_key=True
    )
    imdb: Mapped[str] = mapped_column(ForeignKey("tvshows.imdb"), primary_key=True)
    status: Mapped[WatchStatus] = mapped_column(watch_status_column_type())
    current_episode: Mapped[int] = mapped_column("current_episode", Integer, default=0)
    added_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, onupdate=utcnow)

    tvlist: Mapped[TvList] = relationship(back_populates="entries")
    show: Mapped[TvShow] = relationship()


class UserMovie(Base):
    __tablename__ = "user_movies"

    movielist_id: Mapped[str] = mapped_column(
        ForeignKey("movielists.movielist_id", ondelete="CASCADE"), primary_key=True
    )
    imdb: Mapped[str] = mapped_column(ForeignKey("movies.imdb"), primary_key=True)
    status: Mapped[WatchStatus] = mapped_column(watch_status_column_type())
    added_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, onupdate=utcnow)

    movielist: Mapped[MovieList] = relationship(back_populates="entries")
    movie: Mapped[Movie] = relationship()
