"""TMDB API client (https://developer.themoviedb.org). Requires TMDB_BEARER_TOKEN.

Used for the Discover pages (popular titles, cached per page) and to turn a TMDB id into
an IMDb id when one of those titles is added to a list.
"""

from typing import Any, Literal

import httpx

from app.clients._http import get_json
from app.core.errors import NotFoundError, UpstreamError

BASE_URL = "https://api.themoviedb.org/3"
# TMDB refuses `page` above 500 on /discover, whatever `total_pages` says.
MAX_PAGE = 500

DiscoverKind = Literal["tv", "movie"]


class TmdbClient:
    def __init__(self, http: httpx.Client, bearer_token: str, base_url: str = BASE_URL) -> None:
        self._http = http
        self._headers = {"Authorization": f"Bearer {bearer_token}", "Accept": "application/json"}
        self._base_url = base_url

    def _get(self, path: str, params: dict[str, str] | None = None, *, allow_404: bool = False) -> Any:
        return get_json(
            self._http,
            "TMDB",
            f"{self._base_url}{path}",
            params=params,
            headers=self._headers,
            allow_404=allow_404,
        )

    def discover(self, kind: DiscoverKind, page: int) -> tuple[list[dict[str, Any]], int]:
        """One page of /discover/{tv|movie}: (raw result objects, total_pages capped at 500)."""
        payload = self._get(f"/discover/{kind}", {"page": str(page)})
        if not isinstance(payload, dict) or not isinstance(payload.get("results"), list):
            raise UpstreamError("TMDB returned an unexpected response")
        results = [
            item
            for item in payload["results"]
            if isinstance(item, dict) and isinstance(item.get("id"), int)
        ]
        total = payload.get("total_pages")
        total_pages = min(total, MAX_PAGE) if isinstance(total, int) and total > 0 else page
        return results, total_pages

    def tv_imdb_id(self, tmdb_id: int) -> str | None:
        """IMDb id of a TV show (from /tv/{id}/external_ids), or None if TMDB has none."""
        payload = self._get(f"/tv/{tmdb_id}/external_ids", allow_404=True)
        if payload is None:
            raise NotFoundError("Couldn't find this show on TMDB")
        return _imdb_or_none(payload)

    def movie_imdb_id(self, tmdb_id: int) -> str | None:
        """IMDb id of a movie (from the /movie/{id} details), or None if TMDB has none."""
        payload = self._get(f"/movie/{tmdb_id}", allow_404=True)
        if payload is None:
            raise NotFoundError("Couldn't find this movie on TMDB")
        return _imdb_or_none(payload)


def _imdb_or_none(payload: object) -> str | None:
    if not isinstance(payload, dict):
        raise UpstreamError("TMDB returned an unexpected response")
    imdb = payload.get("imdb_id")
    return imdb if isinstance(imdb, str) and imdb.startswith("tt") else None
