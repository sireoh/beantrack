from datetime import datetime

from app.models.enums import WatchStatus
from app.schemas.common import ImdbId, MediaOut, ORMModel, RequestModel


class TvShowOut(MediaOut):
    pass


class EpisodeOut(ORMModel):
    id: int
    season: int
    number: int | None
    title: str
    image: str | None


class TvListEntryOut(ORMModel):
    show: TvShowOut
    status: WatchStatus
    current_episode: EpisodeOut | None
    added_at: datetime
    updated_at: datetime


class TvListOut(ORMModel):
    tvlist_id: str
    entries: list[TvListEntryOut]


class TvListAddRequest(RequestModel):
    imdb: ImdbId
    status: WatchStatus = WatchStatus.PLANNED
    # TVmaze episode id; must belong to the show being added.
    current_episode: int | None = None
