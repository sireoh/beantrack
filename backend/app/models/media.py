"""Shared catalog data: stored once, referenced by every user who tracks it."""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TvShow(Base):
    __tablename__ = "tvshows"

    imdb: Mapped[str] = mapped_column(String(16), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    image: Mapped[str | None] = mapped_column(String(512))
    score: Mapped[float | None] = mapped_column(Float)
    # TVmaze's own show id, kept so episodes can be (re)fetched without another lookup.
    tvmaze_id: Mapped[int | None] = mapped_column(Integer, unique=True)

    episodes: Mapped[list[Episode]] = relationship(
        back_populates="show",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="[Episode.season, Episode.number]",
    )

    @property
    def episodes_count(self) -> int:
        return len(self.episodes)


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)  # TVmaze id
    imdb: Mapped[str] = mapped_column(
        ForeignKey("tvshows.imdb", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255))
    image: Mapped[str | None] = mapped_column(String(512))  # TVmaze "original" image
    season: Mapped[int] = mapped_column(Integer)
    number: Mapped[int | None] = mapped_column(Integer)  # None for TVmaze specials

    show: Mapped[TvShow] = relationship(back_populates="episodes")


class Movie(Base):
    __tablename__ = "movies"

    imdb: Mapped[str] = mapped_column(String(16), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    image: Mapped[str | None] = mapped_column(String(512))
    score: Mapped[float | None] = mapped_column(Float)
