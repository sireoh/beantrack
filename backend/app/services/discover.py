"""Discover: popular TV shows and movies from TMDB, cached per page in SQLite.

Pages are served from the cache while they are younger than DISCOVER_CACHE_HOURS and
fetched from TMDB otherwise. Adding a title resolves its IMDb id on TMDB, then goes through
the same add flow as search (TVmaze for shows, OMDb for movies).
"""

import logging
from datetime import datetime, timedelta
from typing import cast

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.clients.omdb import OmdbClient
from app.clients.tmdb import DiscoverKind, TmdbClient
from app.clients.tvmaze import TvMazeClient
from app.core.errors import ConflictError, NotFoundError, UpstreamError
from app.db.types import utcnow
from app.models import (
    DiscoverCacheMovie,
    DiscoverCacheTv,
    Movie,
    TvShow,
    User,
    UserMovie,
    UserTvShow,
    WatchStatus,
)
from app.repositories import movielists as movielists_repo
from app.repositories import tvlists as tvlists_repo
from app.schemas.discover import DiscoverItem, DiscoverPage
from app.schemas.movielist import MovieData, MovieListAddRequest
from app.schemas.search import MediaType
from app.schemas.tvlist import TvListAddRequest, TvShowData
from app.services import lists as list_service

log = logging.getLogger("uvicorn.error.discover")

_CACHE = {"tv": DiscoverCacheTv, "movie": DiscoverCacheMovie}
_CATALOG = {"tv": TvShow, "movie": Movie}


def get_page(
    db: Session, tmdb: TmdbClient, kind: DiscoverKind, page: int, max_age: timedelta
) -> DiscoverPage:
    """Cache-first: a fresh cached page, else TMDB (saved for next time)."""
    model = _CACHE[kind]
    row = db.get(model, page)
    now = utcnow()
    if row is None or now - row.fetched_at >= max_age:
        try:
            results, total_pages = tmdb.discover(kind, page)
        except UpstreamError:
            if row is None:
                raise
            # TMDB is down: an expired page is better than an error.
            log.warning("TMDB unavailable; serving expired discover %s page %d", kind, page)
        else:
            row = _save_page(db, model, page, results, total_pages, now)

    return DiscoverPage(
        type=MediaType(kind),
        page=page,
        total_pages=row.total_pages,
        results=_with_imdb(db, kind, [_item(kind, raw) for raw in row.results]),
    )


def clear_cache(db: Session) -> None:
    db.execute(delete(DiscoverCacheTv))
    db.execute(delete(DiscoverCacheMovie))
    db.commit()


def add_tv(
    db: Session,
    *,
    tmdb: TmdbClient,
    tvmaze: TvMazeClient,
    user: User,
    tmdb_id: int,
    status: WatchStatus,
) -> UserTvShow:
    imdb = tmdb.tv_imdb_id(tmdb_id)
    if imdb is None:
        raise NotFoundError("Couldn't find this title on TVmaze (TMDB has no IMDb id for it)")
    _link_tmdb_id(db, "tv", imdb, tmdb_id)
    if tvlists_repo.get_entry(db, user.tvlist.tvlist_id, imdb) is not None:
        raise ConflictError(list_service.TV_DUPLICATE)

    found = tvmaze.lookup_by_imdb(imdb)
    if found is None or found.tvmaze_id is None:
        raise NotFoundError("Couldn't find this title on TVmaze")
    # Exactly what the search page sends for a TVmaze result.
    request = TvListAddRequest(
        show=TvShowData(
            imdb=imdb,
            tvmaze_id=found.tvmaze_id,
            title=found.title,
            image=found.image,
            score=found.score,
        ),
        status=status,
    )
    entry = list_service.add_tvshow(db, tvmaze=tvmaze, user=user, request=request)
    _link_tmdb_id(db, "tv", imdb, tmdb_id)
    return entry


def add_movie(
    db: Session,
    *,
    tmdb: TmdbClient,
    omdb: OmdbClient,
    user: User,
    tmdb_id: int,
    status: WatchStatus,
) -> UserMovie:
    imdb = tmdb.movie_imdb_id(tmdb_id)
    if imdb is None:
        raise NotFoundError("Couldn't find this title on OMDb (TMDB has no IMDb id for it)")
    _link_tmdb_id(db, "movie", imdb, tmdb_id)
    if movielists_repo.get_entry(db, user.movielist.movielist_id, imdb) is not None:
        raise ConflictError(list_service.MOVIE_DUPLICATE)

    try:
        details = omdb.get_movie(imdb)
    except NotFoundError as exc:
        raise NotFoundError("Couldn't find this title on OMDb") from exc
    # Exactly what the search page sends for an OMDb result.
    request = MovieListAddRequest(
        movie=MovieData(imdb=imdb, title=details.title, image=details.image), status=status
    )
    entry = list_service.add_movie(db, omdb=omdb, user=user, request=request, details=details)
    _link_tmdb_id(db, "movie", imdb, tmdb_id)
    return entry


# --- helpers -----------------------------------------------------------------------


def _save_page(
    db: Session,
    model: type[DiscoverCacheTv] | type[DiscoverCacheMovie],
    page: int,
    results: list[dict[str, object]],
    total_pages: int,
    now: datetime,
) -> DiscoverCacheTv | DiscoverCacheMovie:
    row = db.merge(model(page=page, results=results, total_pages=total_pages, fetched_at=now))
    try:
        db.commit()
    except IntegrityError:  # another request cached the same page first
        db.rollback()
        existing = db.get(model, page)
        assert existing is not None
        return existing
    return row


def _item(kind: DiscoverKind, raw: dict[str, object]) -> DiscoverItem:
    title = raw.get("name" if kind == "tv" else "title")
    date = raw.get("first_air_date" if kind == "tv" else "release_date")
    score = raw.get("vote_average")
    votes = raw.get("vote_count")
    poster = raw.get("poster_path")
    genres = raw.get("genre_ids")
    return DiscoverItem(
        tmdb_id=cast(int, raw["id"]),  # TmdbClient only keeps results with an int id
        title=title if isinstance(title, str) and title else "Untitled",
        date=date if isinstance(date, str) and date else None,
        score=float(score) if isinstance(score, int | float) and votes != 0 else None,
        poster_path=poster if isinstance(poster, str) and poster else None,
        genre_ids=[g for g in genres if isinstance(g, int)] if isinstance(genres, list) else [],
    )


def _with_imdb(db: Session, kind: DiscoverKind, items: list[DiscoverItem]) -> list[DiscoverItem]:
    """Fill in IMDb ids the catalog already knows for these TMDB ids."""
    model = _CATALOG[kind]
    ids = [item.tmdb_id for item in items]
    if not ids:
        return items
    rows = db.execute(select(model.tmdb_id, model.imdb).where(model.tmdb_id.in_(ids))).tuples()
    known = {tmdb_id: imdb for tmdb_id, imdb in rows}
    for item in items:
        item.imdb = known.get(item.tmdb_id)
    return items


def _link_tmdb_id(db: Session, kind: DiscoverKind, imdb: str, tmdb_id: int) -> None:
    """Remember the TMDB id on the catalog row (if the title is in the catalog yet)."""
    row = db.get(_CATALOG[kind], imdb)
    if row is not None and row.tmdb_id != tmdb_id:
        row.tmdb_id = tmdb_id
        db.commit()
