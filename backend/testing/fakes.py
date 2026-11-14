"""In-process fakes for TVmaze, OMDb, Discord and Backblaze B2, served through httpx.MockTransport."""

import base64
import hashlib
import json
import re
from urllib.parse import unquote
from dataclasses import dataclass, field
from typing import Any

import httpx

OMDB_TEST_KEY = "omdb-test-key"
B2_TEST_KEY_ID = "b2-test-key-id"
B2_TEST_APP_KEY = "b2-test-app-key"
B2_TEST_BUCKET = "beantrack-test"


def b2_file_id(name: str) -> str:
    """Fake B2 fileId for a file name (real ones are opaque and contain no slashes)."""
    return "4_z" + hashlib.sha1(name.encode()).hexdigest()[:24]

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
    # B2 bucket contents: file name -> (bytes, upload timestamp in ms)
    b2_files: dict[str, tuple[bytes, int]] = field(default_factory=dict)

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
        if host.endswith("backblazeb2.com"):
            return self._b2(request)
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

    def _b2(self, request: httpx.Request) -> httpx.Response:
        host, path = request.url.host, request.url.path
        token = "b2-account-token"
        if host == "api.backblazeb2.com" and path == "/b2api/v2/b2_authorize_account":
            credentials = base64.b64encode(f"{B2_TEST_KEY_ID}:{B2_TEST_APP_KEY}".encode()).decode()
            if request.headers.get("authorization") != f"Basic {credentials}":
                return httpx.Response(401, json={"code": "unauthorized", "message": "bad key"})
            return httpx.Response(
                200,
                json={
                    "accountId": "acct",
                    "authorizationToken": token,
                    "apiUrl": "https://api000.backblazeb2.com",
                    "downloadUrl": "https://f000.backblazeb2.com",
                    "allowed": {"bucketId": "bucket-1", "bucketName": B2_TEST_BUCKET},
                },
            )
        if host == "api000.backblazeb2.com":
            if request.headers.get("authorization") != token:
                return httpx.Response(401, json={"message": "bad token"})
            body = json.loads(request.content or b"{}")
            if path == "/b2api/v2/b2_get_upload_url":
                return httpx.Response(
                    200,
                    json={
                        "uploadUrl": "https://pod-000.backblazeb2.com/upload",
                        "authorizationToken": "upload-token",
                    },
                )
            if path == "/b2api/v2/b2_list_file_names":
                files = [
                    {
                        "fileId": b2_file_id(name),
                        "fileName": name,
                        "contentLength": len(data),
                        "uploadTimestamp": ts,
                    }
                    for name, (data, ts) in sorted(self.b2_files.items())
                    if name.startswith(body.get("prefix", ""))
                ]
                return httpx.Response(200, json={"files": files, "nextFileName": None})
            if path == "/b2api/v2/b2_delete_file_version":
                name = body.get("fileName", "")
                if name not in self.b2_files or body.get("fileId") != b2_file_id(name):
                    return httpx.Response(400, json={"message": "file not present"})
                del self.b2_files[name]
                return httpx.Response(200, json={"fileId": body["fileId"], "fileName": name})
        if host == "pod-000.backblazeb2.com" and request.method == "POST":
            if request.headers.get("authorization") != "upload-token":
                return httpx.Response(401, json={"message": "bad upload token"})
            data = request.content
            if request.headers.get("x-bz-content-sha1") != hashlib.sha1(data).hexdigest():
                return httpx.Response(400, json={"message": "sha1 mismatch"})
            name = unquote(request.headers["x-bz-file-name"])
            ts = 1_700_000_000_000 + len(self.b2_files) * 1000  # strictly increasing
            self.b2_files[name] = (data, ts)
            return httpx.Response(
                200,
                json={
                    "fileId": b2_file_id(name),
                    "fileName": name,
                    "contentLength": len(data),
                    "uploadTimestamp": ts,
                },
            )
        if host == "f000.backblazeb2.com" and request.method == "GET":
            prefix = f"/file/{B2_TEST_BUCKET}/"
            name = unquote(path[len(prefix):]) if path.startswith(prefix) else ""
            if name not in self.b2_files:
                return httpx.Response(404, json={"message": "not found"})
            return httpx.Response(200, content=self.b2_files[name][0])
        return httpx.Response(404)
