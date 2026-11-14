from datetime import datetime

from app.models.enums import WatchStatus
from app.schemas.common import ImdbId, MediaOut, ORMModel, RequestModel


class MovieOut(MediaOut):
    pass


class MovieData(RequestModel):
    imdb: ImdbId
    title: str
    image: str | None = None


class MovieListEntryOut(ORMModel):
    movie: MovieOut
    status: WatchStatus
    added_at: datetime
    updated_at: datetime


class MovieListOut(ORMModel):
    movielist_id: str
    entries: list[MovieListEntryOut]


class MovieListAddRequest(RequestModel):
    movie: MovieData
    status: WatchStatus = WatchStatus.PLANNED
