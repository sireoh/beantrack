"""TV and movie list use cases."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.clients.omdb import OmdbClient
from app.clients.tvmaze import TvMazeClient, TvMazeEpisode
from app.core.errors import ConflictError, InvalidRequestError, NotFoundError
from app.db.types import utcnow
from app.models import Episode, MovieList, TvList, User, UserMovie, UserTvShow, WatchStatus
from app.repositories import media as media_repo
from app.repositories import movielists as movielists_repo
from app.repositories import tvlists as tvlists_repo
from app.schemas.movielist import MovieListAddRequest
from app.schemas.tvlist import TvListAddRequest, TvProgressRequest

TV_DUPLICATE = "Show is already in your TV list"
MOVIE_DUPLICATE = "Movie is already in your movie list"
TV_NOT_FOUND = "Show is not in your TV list"
MOVIE_NOT_FOUND = "Movie is not in your movie list"


def episode_metadata(episode: Episode) -> dict[str, Any]:
    """The cached `current_episode_metadata` value for an episode."""
    return {
        "id": episode.id,
        "season": episode.season,
        "number": episode.number,
        "title": episode.title,
        "image": episode.image,
    }


def _sync_status_with_progress(entry: UserTvShow) -> None:
    """After a progress change: reaching the last episode completes the show, and moving off
    the last episode of a completed show puts it back to Watching. Planned and Dropped are
    otherwise left alone. Together with `_jump_to_last_episode` (Completed -> last episode)
    this is the only place the progress/status rules live."""
    episode_count = len(entry.show.episodes)
    if episode_count == 0:
        return
    if entry.current_episode == episode_count - 1:
        entry.status = WatchStatus.COMPLETED
    elif entry.status == WatchStatus.COMPLETED:
        entry.status = WatchStatus.WATCHING


def _jump_to_last_episode(entry: UserTvShow) -> None:
    """Completed shows count as fully watched: progress moves to the final episode."""
    episodes = entry.show.episodes
    if episodes:
        entry.current_episode = len(episodes) - 1
        entry.current_episode_metadata = episode_metadata(episodes[-1])


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


def get_episodes(db: Session, imdb: str) -> list[Episode]:
    if media_repo.get_tvshow(db, imdb) is None:
        raise NotFoundError("TV show not found")
    return media_repo.get_episodes_for_tvshow(db, imdb)


def add_tvshow(
    db: Session, *, tvmaze: TvMazeClient, user: User, request: TvListAddRequest
) -> UserTvShow:
    tvlist = user.tvlist
    if tvlists_repo.get_entry(db, tvlist.tvlist_id, request.show.imdb) is not None:
        raise ConflictError(TV_DUPLICATE)

    # Shared catalog: the first add supplies show metadata, then fetches episodes.
    show = media_repo.get_tvshow(db, request.show.imdb)
    if show is None:
        show = media_repo.insert_tvshow(db, request.show)
    if not show.episodes:
        episodes = tvmaze.get_episodes(request.show.tvmaze_id)
        media_repo.insert_episodes(db, show, episodes)

    with _duplicate_is_conflict(db, TV_DUPLICATE):
        entry = tvlists_repo.add_entry(
            db,
            tvlist=tvlist,
            show=show,
            status=request.status,
            current_episode=request.current_episode,
            now=utcnow(),
        )
        if request.status == WatchStatus.COMPLETED:
            _jump_to_last_episode(entry)
        db.commit()
    return entry


def update_tv_progress(
    db: Session, *, user: User, imdb: str, request: TvProgressRequest
) -> UserTvShow:
    entry = tvlists_repo.get_entry(db, user.tvlist.tvlist_id, imdb)
    if entry is None:
        raise NotFoundError(TV_NOT_FOUND)

    episode_count = len(entry.show.episodes)
    max_index = max(episode_count - 1, 0)
    requested = request.set_to if request.set_to is not None else entry.current_episode + request.delta
    current_episode = min(max(requested, 0), max_index)
    metadata: dict[str, Any] = request.current_episode_metadata.model_dump()
    entry.current_episode = current_episode
    _sync_status_with_progress(entry)  # committed together with the progress below
    return tvlists_repo.update_progress(
        db,
        entry,
        current_episode=current_episode,
        current_episode_metadata=metadata,
    )


def update_tv_status(db: Session, *, user: User, imdb: str, status: WatchStatus) -> UserTvShow:
    entry = tvlists_repo.get_entry(db, user.tvlist.tvlist_id, imdb)
    if entry is None:
        raise NotFoundError(TV_NOT_FOUND)
    entry.status = status
    if status == WatchStatus.COMPLETED:
        _jump_to_last_episode(entry)
    db.commit()
    return entry


def update_movie_status(
    db: Session, *, user: User, imdb: str, status: WatchStatus
) -> UserMovie:
    entry = movielists_repo.get_entry(db, user.movielist.movielist_id, imdb)
    if entry is None:
        raise NotFoundError(MOVIE_NOT_FOUND)
    entry.status = status
    db.commit()
    return entry


def delete_tvshow(db: Session, *, user: User, imdb: str) -> None:
    entry = tvlists_repo.get_entry(db, user.tvlist.tvlist_id, imdb)
    if entry is None:
        raise NotFoundError(TV_NOT_FOUND)
    tvlists_repo.delete_entry(db, entry)
    db.commit()


def add_movie(
    db: Session, *, omdb: OmdbClient, user: User, request: MovieListAddRequest
) -> UserMovie:
    movielist = user.movielist
    if movielists_repo.get_entry(db, movielist.movielist_id, request.movie.imdb) is not None:
        raise ConflictError(MOVIE_DUPLICATE)

    movie = media_repo.get_movie(db, request.movie.imdb)
    if movie is None:
        movie = media_repo.insert_movie(
            db, request.movie, score=omdb.get_rating(request.movie.imdb)
        )

    with _duplicate_is_conflict(db, MOVIE_DUPLICATE):
        entry = movielists_repo.add_entry(
            db, movielist=movielist, movie=movie, status=request.status, now=utcnow()
        )
        db.commit()
    return entry


def delete_movie(db: Session, *, user: User, imdb: str) -> None:
    entry = movielists_repo.get_entry(db, user.movielist.movielist_id, imdb)
    if entry is None:
        raise NotFoundError(MOVIE_NOT_FOUND)
    movielists_repo.delete_entry(db, entry)
    db.commit()


@contextmanager
def _duplicate_is_conflict(db: Session, message: str) -> Iterator[None]:
    """A concurrent duplicate add slips past the pre-check and hits the primary key: -> 409."""
    try:
        yield
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError(message) from exc
