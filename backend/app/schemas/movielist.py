from datetime import datetime

from app.models.enums import WatchStatus
from app.schemas.common import ImdbId, MediaOut, ORMModel, RequestModel


class MovieOut(MediaOut):
    pass


class MovieListEntryOut(ORMModel):
    movie: MovieOut
    status: WatchStatus
    added_at: datetime
    updated_at: datetime


class MovieListOut(ORMModel):
    movielist_id: str
    entries: list[MovieListEntryOut]


class MovieListAddRequest(RequestModel):
    imdb: ImdbId
    status: WatchStatus = WatchStatus.PLANNED
