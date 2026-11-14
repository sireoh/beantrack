from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Movie, MovieList, UserMovie, WatchStatus


def get_for_user(db: Session, discord_id: str) -> MovieList | None:
    stmt = (
        select(MovieList)
        .where(MovieList.discord_id == discord_id)
        .options(selectinload(MovieList.entries).selectinload(UserMovie.movie))
    )
    return db.scalars(stmt).one_or_none()


def get_entry(db: Session, movielist_id: str, imdb: str) -> UserMovie | None:
    return db.get(UserMovie, (movielist_id, imdb))


def add_entry(
    db: Session, *, movielist: MovieList, movie: Movie, status: WatchStatus, now: datetime
) -> UserMovie:
    entry = UserMovie(
        movielist_id=movielist.movielist_id,
        imdb=movie.imdb,
        status=status,
        added_at=now,
        updated_at=now,
    )
    entry.movie = movie
    db.add(entry)
    db.flush()
    return entry
