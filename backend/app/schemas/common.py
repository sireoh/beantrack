from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.models.enums import WatchStatus

ImdbId = Annotated[str, StringConstraints(pattern=r"^tt\d{5,10}$")]


class ORMModel(BaseModel):
    """Base for response models built from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class RequestModel(BaseModel):
    """Base for request bodies: unknown fields are rejected."""

    model_config = ConfigDict(extra="forbid")


class StatusUpdateRequest(RequestModel):
    status: WatchStatus


class MediaOut(ORMModel):
    imdb: str
    title: str
    image: str | None
    score: float | None
