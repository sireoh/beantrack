"""ORM models. Importing this package registers every table on `Base.metadata`."""

from app.models.discover import DiscoverCacheMovie, DiscoverCacheTv
from app.models.enums import Theme, UserRole, WatchStatus
from app.models.lists import MovieList, TvList, UserMovie, UserTvShow
from app.models.media import Episode, Movie, TvShow
from app.models.user import User, UserSession

__all__ = [
    "DiscoverCacheMovie",
    "DiscoverCacheTv",
    "Episode",
    "Movie",
    "MovieList",
    "Theme",
    "TvList",
    "TvShow",
    "User",
    "UserMovie",
    "UserRole",
    "UserSession",
    "UserTvShow",
    "WatchStatus",
]
