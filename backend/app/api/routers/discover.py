"""Discover pages (popular titles from TMDB). Browsing is public; adding needs a login."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DbSession, Omdb, SettingsDep, Tmdb, TvMaze
from app.clients.tmdb import MAX_PAGE
from app.schemas.discover import DiscoverAddRequest, DiscoverPage
from app.schemas.movielist import MovieListEntryOut
from app.schemas.tvlist import TvListEntryOut
from app.services import discover as discover_service

router = APIRouter(prefix="/discover", tags=["discover"])

Page = Annotated[int, Query(ge=1, le=MAX_PAGE)]


@router.get("/tv", response_model=DiscoverPage)
def discover_tv(db: DbSession, tmdb: Tmdb, settings: SettingsDep, page: Page = 1) -> DiscoverPage:
    """One page of popular TV shows (cached for DISCOVER_CACHE_HOURS)."""
    max_age = timedelta(hours=settings.discover_cache_hours)
    return discover_service.get_page(db, tmdb, "tv", page, max_age)


@router.get("/movies", response_model=DiscoverPage)
def discover_movies(
    db: DbSession, tmdb: Tmdb, settings: SettingsDep, page: Page = 1
) -> DiscoverPage:
    """One page of popular movies (cached for DISCOVER_CACHE_HOURS)."""
    max_age = timedelta(hours=settings.discover_cache_hours)
    return discover_service.get_page(db, tmdb, "movie", page, max_age)


@router.post("/tv/add", response_model=TvListEntryOut, status_code=status.HTTP_201_CREATED)
def add_tv(
    body: DiscoverAddRequest, user: CurrentUser, db: DbSession, tmdb: Tmdb, tvmaze: TvMaze
) -> TvListEntryOut:
    """Add a Discover show: TMDB -> IMDb id -> TVmaze, then the normal TV add."""
    entry = discover_service.add_tv(
        db, tmdb=tmdb, tvmaze=tvmaze, user=user, tmdb_id=body.tmdb_id, status=body.status
    )
    return TvListEntryOut.model_validate(entry)


@router.post("/movies/add", response_model=MovieListEntryOut, status_code=status.HTTP_201_CREATED)
def add_movie(
    body: DiscoverAddRequest, user: CurrentUser, db: DbSession, tmdb: Tmdb, omdb: Omdb
) -> MovieListEntryOut:
    """Add a Discover movie: TMDB -> IMDb id -> OMDb, then the normal movie add."""
    entry = discover_service.add_movie(
        db, tmdb=tmdb, omdb=omdb, user=user, tmdb_id=body.tmdb_id, status=body.status
    )
    return MovieListEntryOut.model_validate(entry)
