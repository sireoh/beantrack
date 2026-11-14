from datetime import datetime
from typing import Any

from pydantic import Field, model_validator

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


class EpisodeMetadata(RequestModel):
    id: int
    season: int
    number: int | None
    title: str
    image: str | None


class TvListEntryOut(ORMModel):
    show: TvShowOut
    status: WatchStatus
    current_episode: int
    current_episode_metadata: EpisodeMetadata | None
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


class TvProgressRequest(RequestModel):
    set_to: int | None = Field(default=None, ge=0)
    delta: int | None = Field(default=None, ge=-1000, le=1000)
    current_episode_metadata: EpisodeMetadata

    @model_validator(mode="after")
    def _exactly_one_operation(self) -> "TvProgressRequest":
        if (self.set_to is None) == (self.delta is None):
            raise ValueError("Exactly one of set_to or delta is required")
        return self
