"""TV and movie list use cases."""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.clients.omdb import OmdbClient
from app.clients.tvmaze import TvMazeClient
from app.core.errors import ConflictError, InvalidRequestError, NotFoundError
from app.db.types import utcnow
from app.models import MovieList, TvList, User, UserMovie, UserTvShow
from app.repositories import media as media_repo
from app.repositories import movielists as movielists_repo
from app.repositories import tvlists as tvlists_repo
from app.schemas.movielist import MovieListAddRequest
from app.schemas.tvlist import TvListAddRequest

TV_DUPLICATE = "Show is already in your TV list"
MOVIE_DUPLICATE = "Movie is already in your movie list"


def get_tvlist(db: Session, user: User) -> TvList:
    tvlist = tvlists_repo.get_for_user(db, user.discord_id)
    if tvlist is None:  # every user gets one on creation, so this means data corruption
        raise NotFoundError("TV list not found")
    return tvlist


def get_movielist(db: Session, user: User) -> MovieList:
    movielist = movielists_repo.get_for_user(db, user.discord_id)
    if movielist is None:
        raise NotFoundError("Movie list not found")
    return movielist


def add_tvshow(
    db: Session, *, tvmaze: TvMazeClient, user: User, request: TvListAddRequest
) -> UserTvShow:
    tvlist = user.tvlist
    if tvlists_repo.get_entry(db, tvlist.tvlist_id, request.imdb) is not None:
        raise ConflictError(TV_DUPLICATE)

    # Shared catalog: TVmaze is only called the first time anyone adds this show.
    show = media_repo.get_tvshow(db, request.imdb)
    if show is None:
        show = media_repo.insert_tvshow(db, tvmaze.get_show_by_imdb(request.imdb))

    current_episode = None
    if request.current_episode is not None:
        current_episode = media_repo.get_episode(db, request.current_episode)
        if current_episode is None or current_episode.tvshow_imdb != show.imdb:
            raise InvalidRequestError("current_episode is not an episode of this show")

    with _duplicate_is_conflict(db, TV_DUPLICATE):
        entry = tvlists_repo.add_entry(
            db,
            tvlist=tvlist,
            show=show,
            status=request.status,
            current_episode=current_episode,
            now=utcnow(),
        )
        db.commit()
    return entry


def add_movie(
    db: Session, *, omdb: OmdbClient, user: User, request: MovieListAddRequest
) -> UserMovie:
    movielist = user.movielist
    if movielists_repo.get_entry(db, movielist.movielist_id, request.imdb) is not None:
        raise ConflictError(MOVIE_DUPLICATE)

    movie = media_repo.get_movie(db, request.imdb)
    if movie is None:
        movie = media_repo.insert_movie(db, omdb.get_movie(request.imdb))

    with _duplicate_is_conflict(db, MOVIE_DUPLICATE):
        entry = movielists_repo.add_entry(
            db, movielist=movielist, movie=movie, status=request.status, now=utcnow()
        )
        db.commit()
    return entry


@contextmanager
def _duplicate_is_conflict(db: Session, message: str) -> Iterator[None]:
    """A concurrent duplicate add slips past the pre-check and hits the primary key: -> 409."""
    try:
        yield
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(message) from exc
