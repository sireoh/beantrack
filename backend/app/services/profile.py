"""Export and import a user's watchlists (list data only, no catalog metadata)."""

import time
from collections.abc import Callable
from typing import Any, Literal

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.clients.omdb import OmdbClient
from app.clients.tvmaze import TvMazeClient
from app.core.errors import AppError, UpstreamError
from app.db.types import utcnow
from app.models import Episode, Movie, TvShow, User, UserMovie, UserTvShow
from app.repositories import media as media_repo
from app.repositories import movielists as movielists_repo
from app.repositories import tvlists as tvlists_repo
from app.schemas.movielist import MovieData
from app.schemas.profile import (
    ImportFailure,
    MovieExportEntry,
    ProfileExport,
    ProfileImportRequest,
    ProfileImportResult,
    TvExportEntry,
)
from app.schemas.tvlist import TvShowData
from app.services.lists import episode_metadata

# TVmaze allows ~20 calls / 10 s; an import that fills an empty cache can hit that.
UPSTREAM_RETRIES = 2
UPSTREAM_RETRY_DELAY_SECONDS = 5.0


def export_profile(db: Session, user: User) -> ProfileExport:
    tvlist = tvlists_repo.get_for_user(db, user.discord_id)
    movielist = movielists_repo.get_for_user(db, user.discord_id)
    return ProfileExport(
        exported_at=utcnow(),
        tvlist=[_export_tv(e) for e in (tvlist.entries if tvlist else [])],
        movielist=[_export_movie(e) for e in (movielist.entries if movielist else [])],
    )


def _export_tv(entry: UserTvShow) -> TvExportEntry:
    metadata = entry.current_episode_metadata or {}
    episode_id = metadata.get("id")
    return TvExportEntry(
        imdb=entry.imdb,
        tvmaze_id=entry.show.tvmaze_id,
        status=entry.status,
        current_episode=entry.current_episode,
        current_episode_id=episode_id if isinstance(episode_id, int) else None,
        added_at=entry.added_at,
        updated_at=entry.updated_at,
    )


def _export_movie(entry: UserMovie) -> MovieExportEntry:
    return MovieExportEntry(
        imdb=entry.imdb, status=entry.status, added_at=entry.added_at, updated_at=entry.updated_at
    )


def import_profile(
    db: Session,
    *,
    user: User,
    tvmaze: TvMazeClient,
    omdb: OmdbClient,
    request: ProfileImportRequest,
) -> ProfileImportResult:
    """Add every entry that isn't already in the user's lists. Each entry commits on its own,
    so one bad row (unknown title, upstream error) never undoes the others."""
    imported = skipped = 0
    failures: list[ImportFailure] = []

    jobs: list[tuple[Literal["tv", "movie"], dict[str, Any], Callable[[dict[str, Any]], bool]]] = [
        *(("tv", raw, lambda r: _import_tv(db, user, tvmaze, r)) for raw in request.tvlist),
        *(("movie", raw, lambda r: _import_movie(db, user, omdb, r)) for raw in request.movielist),
    ]
    for kind, raw, run in jobs:
        try:
            added = _with_retries(db, lambda: run(raw))
            db.commit()
        except (AppError, ValidationError, IntegrityError) as exc:
            db.rollback()
            failures.append(ImportFailure(kind=kind, imdb=_imdb_of(raw), reason=_reason(exc)))
            continue
        if added:
            imported += 1
        else:
            skipped += 1

    return ProfileImportResult(
        imported=imported, skipped=skipped, failed=len(failures), failures=failures
    )


def _import_tv(db: Session, user: User, tvmaze: TvMazeClient, raw: dict[str, Any]) -> bool:
    item = TvExportEntry.model_validate(raw)
    if tvlists_repo.get_entry(db, user.tvlist.tvlist_id, item.imdb) is not None:
        return False

    show = _ensure_show(db, tvmaze, item)
    episodes = list(show.episodes)
    index, current = _resolve_progress(episodes, item)
    now = utcnow()
    entry = tvlists_repo.add_entry(
        db,
        tvlist=user.tvlist,
        show=show,
        status=item.status,
        current_episode=index,
        now=item.added_at or now,
    )
    entry.current_episode_metadata = episode_metadata(current) if current else None
    entry.updated_at = item.updated_at or now
    db.flush()
    return True


def _ensure_show(db: Session, tvmaze: TvMazeClient, item: TvExportEntry) -> TvShow:
    """Use the shared cache; fill it from TVmaze when the show or its episodes are missing."""
    show = media_repo.get_tvshow(db, item.imdb)
    if show is None:
        details = (
            tvmaze.get_show(item.tvmaze_id, item.imdb)
            if item.tvmaze_id is not None
            else tvmaze.get_show_by_imdb(item.imdb)
        )
        show = media_repo.insert_tvshow(
            db,
            TvShowData(
                imdb=item.imdb,
                tvmaze_id=details.tvmaze_id,
                title=details.title,
                image=details.image,
                score=details.score,
            ),
        )
        media_repo.insert_episodes(db, show, details.episodes)
    elif not show.episodes and show.tvmaze_id is not None:
        media_repo.insert_episodes(db, show, tvmaze.get_episodes(show.tvmaze_id))
    return show


def _resolve_progress(episodes: list[Episode], item: TvExportEntry) -> tuple[int, Episode | None]:
    """Prefer the saved episode id (stable even if TVmaze inserts episodes); fall back to
    the saved index. Returns (index, current episode or None if never started)."""
    max_index = max(len(episodes) - 1, 0)
    if item.current_episode_id is not None:
        for index, episode in enumerate(episodes):
            if episode.id == item.current_episode_id:
                return index, episode
        index = min(item.current_episode, max_index)
        return index, episodes[index] if episodes else None
    return min(item.current_episode, max_index), None


def _import_movie(db: Session, user: User, omdb: OmdbClient, raw: dict[str, Any]) -> bool:
    item = MovieExportEntry.model_validate(raw)
    if movielists_repo.get_entry(db, user.movielist.movielist_id, item.imdb) is not None:
        return False

    movie: Movie | None = media_repo.get_movie(db, item.imdb)
    if movie is None:
        details = omdb.get_movie(item.imdb)
        movie = media_repo.insert_movie(
            db,
            MovieData(imdb=item.imdb, title=details.title, image=details.image),
            score=details.score,
        )
    now = utcnow()
    entry = movielists_repo.add_entry(
        db, movielist=user.movielist, movie=movie, status=item.status, now=item.added_at or now
    )
    entry.updated_at = item.updated_at or now
    db.flush()
    return True


def _with_retries(db: Session, action: Callable[[], bool]) -> bool:
    for attempt in range(UPSTREAM_RETRIES + 1):
        try:
            return action()
        except UpstreamError:
            if attempt == UPSTREAM_RETRIES:
                raise
            db.rollback()  # drop anything half-inserted before trying again
            time.sleep(UPSTREAM_RETRY_DELAY_SECONDS)
    raise AssertionError("unreachable")


def _imdb_of(raw: object) -> str | None:
    imdb = raw.get("imdb") if isinstance(raw, dict) else None
    return imdb if isinstance(imdb, str) else None


def _reason(exc: Exception) -> str:
    if isinstance(exc, AppError):
        return exc.detail
    if isinstance(exc, ValidationError):
        first = exc.errors()[0]
        field = ".".join(str(part) for part in first["loc"])
        return f"Invalid {field}: {first['msg']}" if field else first["msg"]
    return "Already in your list"
