"""Shared catalog (tvshows, episodes, movies).

Inserts use `INSERT ... ON CONFLICT DO NOTHING`, so two users adding the same new title
at the same time both succeed and end up pointing at the same row.
"""

from typing import Any

from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from app.clients.omdb import OmdbMovie
from app.clients.tvmaze import TvMazeEpisode
from app.models import Episode, Movie, TvShow
from app.schemas.tvlist import TvShowData


def get_tvshow(db: Session, imdb: str) -> TvShow | None:
    return db.get(TvShow, imdb)


def get_episodes_for_tvshow(db: Session, imdb: str) -> list[Episode]:
    show = db.get(TvShow, imdb)
    if show is None:
        return []
    return list(show.episodes)


def get_episode(db: Session, episode_id: int) -> Episode | None:
    return db.get(Episode, episode_id)


def get_movie(db: Session, imdb: str) -> Movie | None:
    return db.get(Movie, imdb)


def insert_tvshow(db: Session, data: TvShowData) -> TvShow:
    db.execute(
        insert(TvShow)
        .values(
            imdb=data.imdb,
            title=data.title,
            image=data.image,
            score=data.score,
            tvmaze_id=data.tvmaze_id,
        )
        .on_conflict_do_nothing()
    )
    show = db.get(TvShow, data.imdb)
    assert show is not None
    return show


def insert_episodes(db: Session, show: TvShow, episodes: list[TvMazeEpisode]) -> None:
    episode_rows: list[dict[str, Any]] = [
        {
            "id": ep.id,
            "imdb": show.imdb,
            "title": ep.title,
            "image": ep.image,
            "season": ep.season,
            "number": ep.number,
        }
        for ep in episodes
    ]
    if episode_rows:
        db.execute(insert(Episode).on_conflict_do_nothing(), episode_rows)
        db.expire(show, ["episodes"])


def insert_movie(db: Session, data: OmdbMovie) -> Movie:
    db.execute(
        insert(Movie)
        .values(imdb=data.imdb, title=data.title, image=data.image, score=data.score)
        .on_conflict_do_nothing()
    )
    movie = db.get(Movie, data.imdb)
    assert movie is not None
    return movie
