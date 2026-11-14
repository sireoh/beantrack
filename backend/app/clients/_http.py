from typing import Any

import httpx

from app.core.errors import UpstreamError


def get_json(
    http: httpx.Client,
    service: str,
    url: str,
    *,
    params: dict[str, str] | None = None,
    allow_404: bool = False,
) -> Any | None:
    """GET a JSON document. Returns None on 404 when `allow_404`; raises UpstreamError otherwise."""
    try:
        response = http.get(url, params=params)
    except httpx.HTTPError as exc:
        raise UpstreamError(f"{service} is unreachable") from exc
    if allow_404 and response.status_code == 404:
        return None
    if response.is_error:
        raise UpstreamError(f"{service} returned HTTP {response.status_code}")
    try:
        return response.json()
    except ValueError as exc:
        raise UpstreamError(f"{service} returned invalid JSON") from exc
