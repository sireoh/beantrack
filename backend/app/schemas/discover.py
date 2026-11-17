from pydantic import BaseModel, Field

from app.models.enums import WatchStatus
from app.schemas.common import RequestModel
from app.schemas.search import MediaType


class DiscoverItem(BaseModel):
    """One TMDB discover result, the same shape for TV and movies."""

    tmdb_id: int
    title: str  # TMDB `name` for TV, `title` for movies
    date: str | None  # `first_air_date` / `release_date` (YYYY-MM-DD)
    score: float | None  # `vote_average`; None when nobody has voted
    poster_path: str | None  # append to https://image.tmdb.org/t/p/w500
    genre_ids: list[int]
    # Known once someone has added this title from Discover; used to mark cards as added.
    imdb: str | None = None


class DiscoverPage(BaseModel):
    type: MediaType
    page: int
    total_pages: int
    results: list[DiscoverItem]


class DiscoverAddRequest(RequestModel):
    tmdb_id: int = Field(gt=0)
    status: WatchStatus = WatchStatus.PLANNED
