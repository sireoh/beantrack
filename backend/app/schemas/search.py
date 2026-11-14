from enum import StrEnum

from pydantic import BaseModel


class MediaType(StrEnum):
    TV = "tv"
    MOVIE = "movie"


class SearchResult(BaseModel):
    # None when TVmaze has no IMDb id for a show; such results can't be added to a list.
    imdb: str | None
    tvmaze_id: int | None = None
    title: str
    year: str | None
    image: str | None
    score: float | None


class SearchResponse(BaseModel):
    type: MediaType
    query: str
    results: list[SearchResult]
