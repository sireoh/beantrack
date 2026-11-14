"""OMDb API client (https://www.omdbapi.com). Requires OMDB_API_KEY."""

import httpx
from pydantic import BaseModel

from app.clients._http import get_json
from app.core.errors import NotFoundError, UpstreamError
from app.schemas.search import SearchResult

BASE_URL = "https://www.omdbapi.com/"


class OmdbMovie(BaseModel):
    imdb: str
    title: str
    image: str | None
    score: float | None


def _na(value: object) -> str | None:
    """OMDb uses the string "N/A" for missing values."""
    if not isinstance(value, str) or value in ("", "N/A"):
        return None
    return value


def _float_or_none(value: object) -> float | None:
    text = _na(value)
    if text is None:
        return None
    try:
        return float(text)
    except ValueError:
        return None


class OmdbClient:
    def __init__(self, http: httpx.Client, api_key: str, base_url: str = BASE_URL) -> None:
        self._http = http
        self._api_key = api_key
        self._base_url = base_url

    def _get(self, params: dict[str, str]) -> dict[str, object]:
        payload = get_json(self._http, "OMDb", self._base_url, params={**params, "apikey": self._api_key})
        if not isinstance(payload, dict):
            raise UpstreamError("OMDb returned an unexpected response")
        return payload

    def search(self, query: str) -> list[SearchResult]:
        payload = self._get({"s": query, "type": "movie"})
        if payload.get("Response") == "False":
            error = str(payload.get("Error", ""))
            # "Movie not found!" / "Too many results." are normal "no results" outcomes.
            if "not found" in error.lower() or "too many" in error.lower():
                return []
            raise UpstreamError(f"OMDb error: {error or 'unknown'}")

        results: list[SearchResult] = []
        items = payload.get("Search")
        for item in items if isinstance(items, list) else []:
            if not isinstance(item, dict):
                continue
            imdb = _na(item.get("imdbID"))
            title = _na(item.get("Title"))
            if imdb is None or title is None:
                continue
            results.append(
                SearchResult(
                    imdb=imdb,
                    title=title,
                    year=_na(item.get("Year")),
                    image=_na(item.get("Poster")),
                    score=None,  # OMDb search results don't include ratings
                )
            )
        return results

    def get_movie(self, imdb: str) -> OmdbMovie:
        """Fetch one movie by IMDb id. Raises NotFoundError if OMDb doesn't know it."""
        payload = self._get({"i": imdb, "type": "movie"})
        if payload.get("Response") == "False":
            error = str(payload.get("Error", ""))
            if "not found" in error.lower() or "incorrect imdb id" in error.lower():
                raise NotFoundError(f"No movie found for IMDb id {imdb}")
            raise UpstreamError(f"OMDb error: {error or 'unknown'}")

        title = _na(payload.get("Title"))
        if title is None:
            raise UpstreamError("OMDb returned a movie without a title")
        return OmdbMovie(
            imdb=imdb,
            title=title,
            image=_na(payload.get("Poster")),
            score=_float_or_none(payload.get("imdbRating")),
        )
