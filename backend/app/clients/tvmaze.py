"""TVmaze API client (https://www.tvmaze.com/api). No API key required."""

import httpx
from pydantic import BaseModel, Field, ValidationError

from app.clients._http import get_json
from app.core.errors import NotFoundError, UpstreamError
from app.schemas.search import SearchResult

BASE_URL = "https://api.tvmaze.com"


# --- Raw TVmaze payloads (only the fields we use) ---------------------------------


class _Image(BaseModel):
    medium: str | None = None
    original: str | None = None


class _Rating(BaseModel):
    average: float | None = None


class _Externals(BaseModel):
    imdb: str | None = None


class _Show(BaseModel):
    id: int
    name: str
    premiered: str | None = None
    image: _Image | None = None
    rating: _Rating = Field(default_factory=_Rating)
    externals: _Externals = Field(default_factory=_Externals)


class _SearchHit(BaseModel):
    show: _Show


class _Episode(BaseModel):
    id: int
    name: str | None = None
    season: int
    number: int | None = None
    image: _Image | None = None


# --- What the rest of the app consumes ---------------------------------------------


class TvMazeEpisode(BaseModel):
    id: int
    title: str
    image: str | None
    season: int
    number: int | None


class TvMazeShowDetails(BaseModel):
    imdb: str
    tvmaze_id: int
    title: str
    image: str | None
    score: float | None
    episodes: list[TvMazeEpisode]


def _best_image(image: _Image | None) -> str | None:
    if image is None:
        return None
    return image.original or image.medium


class TvMazeClient:
    def __init__(self, http: httpx.Client, base_url: str = BASE_URL) -> None:
        self._http = http
        self._base_url = base_url

    def search(self, query: str) -> list[SearchResult]:
        payload = get_json(self._http, "TVmaze", f"{self._base_url}/search/shows", params={"q": query})
        try:
            hits = [_SearchHit.model_validate(item) for item in payload or []]
        except ValidationError as exc:
            raise UpstreamError("TVmaze returned an unexpected response") from exc
        return [
            SearchResult(
                imdb=hit.show.externals.imdb,
                tvmaze_id=hit.show.id,
                title=hit.show.name,
                year=hit.show.premiered[:4] if hit.show.premiered else None,
                image=_best_image(hit.show.image),
                score=hit.show.rating.average,
            )
            for hit in hits
        ]

    def get_episodes(self, tvmaze_id: int) -> list[TvMazeEpisode]:
        """Fetch and parse the complete episode list for a TVmaze show."""
        payload = get_json(
            self._http,
            "TVmaze",
            f"{self._base_url}/shows/{tvmaze_id}",
            params={"embed": "episodes"},
        )
        try:
            episodes_payload = (payload.get("_embedded") or {}).get("episodes", [])
            episodes = [_Episode.model_validate(item) for item in episodes_payload]
        except (AttributeError, TypeError, ValidationError) as exc:
            raise UpstreamError("TVmaze returned an unexpected response") from exc
        return [
            TvMazeEpisode(
                id=ep.id,
                title=ep.name or f"Episode {ep.number or ep.id}",
                image=ep.image.original if ep.image else None,
                season=ep.season,
                number=ep.number,
            )
            for ep in episodes
        ]

    def get_show(self, tvmaze_id: int, imdb: str) -> TvMazeShowDetails:
        """Fetch a show and all of its episodes in one call (`?embed=episodes`)."""
        payload = get_json(
            self._http,
            "TVmaze",
            f"{self._base_url}/shows/{tvmaze_id}",
            params={"embed": "episodes"},
            allow_404=True,
        )
        if payload is None:
            raise NotFoundError(f"No TV show found for TVmaze id {tvmaze_id}")
        try:
            show = _Show.model_validate(payload)
            episodes_payload = (payload.get("_embedded") or {}).get("episodes", [])
            episodes = [_Episode.model_validate(item) for item in episodes_payload]
        except (AttributeError, TypeError, ValidationError) as exc:
            raise UpstreamError("TVmaze returned an unexpected response") from exc

        return TvMazeShowDetails(
            imdb=imdb,
            tvmaze_id=show.id,
            title=show.name,
            image=_best_image(show.image),
            score=show.rating.average,
            episodes=[
                TvMazeEpisode(
                    id=ep.id,
                    title=ep.name or f"Episode {ep.number or ep.id}",
                    image=ep.image.original if ep.image else None,
                    season=ep.season,
                    number=ep.number,
                )
                for ep in episodes
            ],
        )

    def get_show_by_imdb(self, imdb: str) -> TvMazeShowDetails:
        """Look a show up by IMDb id, then fetch it with all episodes. Raises NotFoundError."""
        show_payload = get_json(
            self._http,
            "TVmaze",
            f"{self._base_url}/lookup/shows",
            params={"imdb": imdb},
            allow_404=True,
        )
        if show_payload is None:
            raise NotFoundError(f"No TV show found for IMDb id {imdb}")
        try:
            show = _Show.model_validate(show_payload)
        except ValidationError as exc:
            raise UpstreamError("TVmaze returned an unexpected response") from exc
        return self.get_show(show.id, imdb)
