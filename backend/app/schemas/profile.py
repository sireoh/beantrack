"""Watchlist export/import format.

Only the user's own list data is exported (IDs, status, progress, dates). Show, movie and
episode metadata stays in the shared server cache and is re-fetched on import if missing.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.models.enums import WatchStatus
from app.schemas.common import ImdbId

EXPORT_FORMAT = "beantrack-export"
EXPORT_VERSION = 1
MAX_IMPORT_ENTRIES = 5000


class TvExportEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    imdb: ImdbId
    tvmaze_id: int | None = None
    status: WatchStatus = WatchStatus.PLANNED
    # Zero-based index into the show's episode list.
    current_episode: int = Field(default=0, ge=0)
    # TVmaze id of the current episode; null if progress was never set.
    current_episode_id: int | None = None
    added_at: AwareDatetime | None = None
    updated_at: AwareDatetime | None = None


class MovieExportEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    imdb: ImdbId
    status: WatchStatus = WatchStatus.PLANNED
    added_at: AwareDatetime | None = None
    updated_at: AwareDatetime | None = None


class ProfileExport(BaseModel):
    format: Literal["beantrack-export"] = EXPORT_FORMAT
    version: int = EXPORT_VERSION
    exported_at: datetime
    tvlist: list[TvExportEntry]
    movielist: list[MovieExportEntry]


class ProfileImportRequest(BaseModel):
    """The export file as-is. Entries are validated one by one so a bad row only fails itself."""

    model_config = ConfigDict(extra="ignore")

    format: str | None = None
    version: int | None = None
    tvlist: list[dict[str, Any]] = Field(default_factory=list, max_length=MAX_IMPORT_ENTRIES)
    movielist: list[dict[str, Any]] = Field(default_factory=list, max_length=MAX_IMPORT_ENTRIES)


class ImportFailure(BaseModel):
    kind: Literal["tv", "movie"]
    imdb: str | None
    reason: str


class ProfileImportResult(BaseModel):
    imported: int
    skipped: int  # already in the list
    failed: int
    failures: list[ImportFailure]
