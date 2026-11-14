"""In-process fakes for TVmaze, OMDb and Discord, served through httpx.MockTransport."""

import json
import re
from dataclasses import dataclass, field
from typing import Any

import httpx

OMDB_TEST_KEY = "omdb-test-key"

BREAKING_BAD = {
    "id": 169,
    "name": "Breaking Bad",
    "premiered": "2008-01-20",
    "rating": {"average": 9.2},
    "image": {
        "medium": "https://static.tvmaze.com/bb-medium.jpg",
        "original": "https://static.tvmaze.com/bb-original.jpg",
    },
    "externals": {"imdb": "tt0903747"},
}
BREAKING_BAD_EPISODES = [
    {
        "id": 12192,
        "name": "Pilot",
        "season": 1,
        "number": 1,
        "image": {"medium": "https://static.tvmaze.com/e1-m.jpg", "original": "https://static.tvmaze.com/e1-o.jpg"},
    },
    {"id": 12193, "name": "Cat's in the Bag...", "season": 1, "number": 2, "image": None},
]
THE_WIRE = {
    "id": 179,
    "name": "The Wire",
    "premiered": "2002-06-02",
    "rating": {"average": 9.3},
    "image": None,
    "externals": {"imdb": "tt0306414"},
}
THE_WIRE_EPISODES = [{"id": 15000, "name": "The Target", "season": 1, "number": 1, "image": None}]
NO_IMDB_SHOW = {"id": 999, "name": "Breaking Bad: Obscure Web Series", "externals": {"imdb": None}}

TV_SHOWS_BY_IMDB = {"tt0903747": BREAKING_BAD, "tt0306414": THE_WIRE}
EPISODES_BY_TVMAZE_ID = {169: BREAKING_BAD_EPISODES, 179: THE_WIRE_EPISODES}

THE_MATRIX = {
    "Title": "The Matrix",
    "Year": "1999",
    "imdbID": "tt0133093",
    "Type": "movie",
    "Poster": "https://m.media-amazon.com/matrix.jpg",
    "imdbRating": "8.7",
    "Response": "True",
}
INTERSTELLAR = {
    "Title": "Interstellar",
    "Year": "2014",
    "imdbID": "tt0816692",
    "Type": "movie",
    "Poster": "N/A",
    "imdbRating": "N/A",
    "Response": "True",
}
MOVIES_BY_IMDB = {"tt0133093": THE_MATRIX, "tt0816692": INTERSTELLAR}


def tv_add_payload(
    imdb: str = "tt0903747",
    *,
    status: str | None = None,
    current_episode: int | None = None,
) -> dict[str, Any]:
    show = TV_SHOWS_BY_IMDB[imdb]
    payload: dict[str, Any] = {
        "show": {
            "imdb": imdb,
            "tvmaze_id": show["id"],
            "title": show["name"],
            "image": (show.get("image") or {}).get("original"),
            "score": show["rating"]["average"],
        }
    }
    if status is not None:
        payload["status"] = status
    if current_episode is not None:
        payload["current_episode"] = current_episode
    return payload


def movie_add_payload(imdb: str = "tt0133093", *, status: str | None = None) -> dict[str, Any]:
    movie = MOVIES_BY_IMDB[imdb]
    payload: dict[str, Any] = {
        "movie": {
            "imdb": imdb,
            "title": movie["Title"],
            "image": None if movie["Poster"] == "N/A" else movie["Poster"],
        }
    }
    if status is not None:
        payload["status"] = status
    return payload


@dataclass
class FakeDiscordUser:
    id: str = "100000000000000001"
    username: str = "beanfan"
    avatar: str | None = "abc123"


@dataclass
class FakeUpstream:
    """Routes outbound requests by host. Records every request it sees."""

    requests: list[httpx.Request] = field(default_factory=list)
    discord_user: FakeDiscordUser = field(default_factory=FakeDiscordUser)
    valid_discord_code: str = "good-code"
    fail_hosts: set[str] = field(default_factory=set)

    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self.handle)

    def count(self, host: str, path_prefix: str = "") -> int:
        return sum(
            1 for r in self.requests if r.url.host == host and r.url.path.startswith(path_prefix)
        )

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        host = request.url.host
        if host in self.fail_hosts:
            return httpx.Response(503, text="unavailable")
        if host == "api.tvmaze.com":
            return self._tvmaze(request)
        if host == "www.omdbapi.com":
            return self._omdb(request)
        if host == "discord.com":
            return self._discord(request)
        return httpx.Response(404)

    def _tvmaze(self, request: httpx.Request) -> httpx.Response:
        path, params = request.url.path, request.url.params
        if path == "/search/shows":
            q = params.get("q", "").lower()
            hits = [
                {"score": 0.9, "show": show}
                for show in (BREAKING_BAD, THE_WIRE, NO_IMDB_SHOW)
                if q in str(show["name"]).lower()
            ]
            return httpx.Response(200, json=hits)
        if path == "/lookup/shows":
            show = TV_SHOWS_BY_IMDB.get(params.get("imdb", ""))
            return httpx.Response(200, json=show) if show else httpx.Response(404, json=None)
        if match := re.fullmatch(r"/shows/(\d+)", path):
            show = next(
                (show for show in TV_SHOWS_BY_IMDB.values() if show["id"] == int(match.group(1))),
                None,
            )
            if show is None:
                return httpx.Response(404, json=None)
            return httpx.Response(
                200,
                json={
                    **show,
                    "_embedded": {"episodes": EPISODES_BY_TVMAZE_ID[int(match.group(1))]},
                },
            )
        return httpx.Response(404)

    def _omdb(self, request: httpx.Request) -> httpx.Response:
        params = request.url.params
        if params.get("apikey") != OMDB_TEST_KEY:
            return httpx.Response(401, json={"Response": "False", "Error": "Invalid API key!"})
        if "s" in params:
            q = params["s"].lower()
            found = [
                {k: m[k] for k in ("Title", "Year", "imdbID", "Type", "Poster")}
                for m in MOVIES_BY_IMDB.values()
                if q in m["Title"].lower()
            ]
            if not found:
                return httpx.Response(200, json={"Response": "False", "Error": "Movie not found!"})
            return httpx.Response(
                200, json={"Search": found, "totalResults": str(len(found)), "Response": "True"}
            )
        if "i" in params:
            movie = MOVIES_BY_IMDB.get(params["i"])
            if movie is None:
                return httpx.Response(200, json={"Response": "False", "Error": "Incorrect IMDb ID."})
            return httpx.Response(200, json=movie)
        return httpx.Response(200, json={"Response": "False", "Error": "No parameters."})

    def _discord(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/oauth2/token" and request.method == "POST":
            form = dict(httpx.QueryParams(request.content.decode()))
            if form.get("code") != self.valid_discord_code:
                return httpx.Response(400, json={"error": "invalid_grant"})
            return httpx.Response(
                200,
                json={
                    "access_token": "discord-access-plaintext",
                    "refresh_token": "discord-refresh-plaintext",
                    "expires_in": 604800,
                    "token_type": "Bearer",
                    "scope": "identify",
                },
            )
        if request.url.path == "/api/users/@me":
            if request.headers.get("authorization") != "Bearer discord-access-plaintext":
                return httpx.Response(401, json={"message": "401: Unauthorized"})
            user: dict[str, Any] = {
                "id": self.discord_user.id,
                "username": self.discord_user.username,
                "avatar": self.discord_user.avatar,
                "global_name": None,
            }
            return httpx.Response(200, content=json.dumps(user))
        return httpx.Response(404)
