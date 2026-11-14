"""ORM models. Importing this package registers every table on `Base.metadata`."""

from app.models.enums import WatchStatus
from app.models.lists import MovieList, TvList, UserMovie, UserTvShow
from app.models.media import Episode, Movie, TvShow
from app.models.user import User, UserSession

__all__ = [
    "Episode",
    "Movie",
    "MovieList",
    "TvList",
    "TvShow",
    "User",
    "UserMovie",
    "UserSession",
    "UserTvShow",
    "WatchStatus",
]
