"""Shared catalog (tvshows, episodes, movies).

Inserts use `INSERT ... ON CONFLICT DO NOTHING`, so two users adding the same new title
at the same time both succeed and end up pointing at the same row.
"""

from typing import Any

from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from app.clients.omdb import OmdbMovie
from app.clients.tvmaze import TvMazeShowDetails
from app.models import Episode, Movie, TvShow


def get_tvshow(db: Session, imdb: str) -> TvShow | None:
    return db.get(TvShow, imdb)


def get_episode(db: Session, episode_id: int) -> Episode | None:
    return db.get(Episode, episode_id)


def get_movie(db: Session, imdb: str) -> Movie | None:
    return db.get(Movie, imdb)


def insert_tvshow(db: Session, data: TvMazeShowDetails) -> TvShow:
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
    episode_rows: list[dict[str, Any]] = [
        {
            "id": ep.id,
            "tvshow_imdb": data.imdb,
            "title": ep.title,
            "image": ep.image,
            "season": ep.season,
            "number": ep.number,
        }
        for ep in data.episodes
    ]
    if episode_rows:
        db.execute(insert(Episode).on_conflict_do_nothing(), episode_rows)
    show = db.get(TvShow, data.imdb)
    assert show is not None
    return show


def insert_movie(db: Session, data: OmdbMovie) -> Movie:
    db.execute(
        insert(Movie)
        .values(imdb=data.imdb, title=data.title, image=data.image, score=data.score)
        .on_conflict_do_nothing()
    )
    movie = db.get(Movie, data.imdb)
    assert movie is not None
    return movie
