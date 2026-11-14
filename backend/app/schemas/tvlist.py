from datetime import datetime

from pydantic import Field

from app.models.enums import WatchStatus
from app.schemas.common import ImdbId, MediaOut, ORMModel, RequestModel


class TvShowOut(MediaOut):
    episodes_count: int


class EpisodeOut(ORMModel):
    id: int
    season: int
    number: int | None
    title: str
    image: str | None


class TvListEntryOut(ORMModel):
    show: TvShowOut
    status: WatchStatus
    current_episode: int
    added_at: datetime
    updated_at: datetime


class TvListOut(ORMModel):
    tvlist_id: str
    entries: list[TvListEntryOut]


class TvEpisodeData(RequestModel):
    id: int
    title: str
    image: str | None = None
    season: int
    number: int | None = None


class TvShowData(RequestModel):
    imdb: ImdbId
    tvmaze_id: int
    title: str
    image: str | None = None
    score: float | None = None


class TvListAddRequest(RequestModel):
    show: TvShowData
    status: WatchStatus = WatchStatus.PLANNED
    # Zero-based index into the separately cached episode list.
    current_episode: int = Field(default=0, ge=0)
