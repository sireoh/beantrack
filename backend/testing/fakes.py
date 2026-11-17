"""In-process fakes for TVmaze, OMDb, TMDB, Discord and Backblaze B2, served through httpx.MockTransport."""

import base64
import hashlib
import json
import re
from urllib.parse import unquote
from dataclasses import dataclass, field
from typing import Any

import httpx

OMDB_TEST_KEY = "omdb-test-key"
TMDB_TEST_TOKEN = "tmdb-test-token"
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

# --- TMDB ---------------------------------------------------------------------------
# Discover results. Each TMDB id maps to an IMDb id (None = TMDB doesn't know one).
TMDB_TV_PAGES = {
    1: [
        {"id": 1396, "name": "Breaking Bad", "first_air_date": "2008-01-20", "vote_average": 8.912,
         "vote_count": 15000, "poster_path": "/bb.jpg", "genre_ids": [18, 80]},
        {"id": 5000, "name": "No IMDb Show", "first_air_date": "", "vote_average": 0,
         "vote_count": 0, "poster_path": None, "genre_ids": [99999]},
        {"id": 6000, "name": "Unknown To TVmaze", "first_air_date": "2020-05-01",
         "vote_average": 6.5, "vote_count": 10, "poster_path": "/u.jpg", "genre_ids": []},
    ],
    2: [
        {"id": 1438, "name": "The Wire", "first_air_date": "2002-06-02", "vote_average": 8.6,
         "vote_count": 2500, "poster_path": "/wire.jpg", "genre_ids": [80, 18]},
    ],
}
TMDB_TV_IMDB = {1396: "tt0903747", 1438: "tt0306414", 5000: None, 6000: "tt9999999"}
TMDB_MOVIE_PAGES = {
    1: [
        {"id": 603, "title": "The Matrix", "release_date": "1999-03-31", "vote_average": 8.2,
         "vote_count": 26000, "poster_path": "/matrix.jpg", "genre_ids": [28, 878]},
        {"id": 7000, "title": "No IMDb Movie", "release_date": "2024-01-01", "vote_average": 5,
         "vote_count": 3, "poster_path": None, "genre_ids": [18]},
        {"id": 8000, "title": "Unknown To OMDb", "release_date": "2023-02-02", "vote_average": 7,
         "vote_count": 3, "poster_path": None, "genre_ids": []},
    ],
    2: [
        {"id": 157336, "title": "Interstellar", "release_date": "2014-11-05", "vote_average": 8.4,
         "vote_count": 35000, "poster_path": "/inter.jpg", "genre_ids": [12, 18, 878]},
    ],
}
TMDB_MOVIE_IMDB = {603: "tt0133093", 157336: "tt0816692", 7000: None, 8000: "tt8888888"}
TMDB_TOTAL_PAGES = 2


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
    b2_uploads: int = 0

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
        if host == "api.themoviedb.org":
            return self._tmdb(request)
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

    def _tmdb(self, request: httpx.Request) -> httpx.Response:
        if request.headers.get("authorization") != f"Bearer {TMDB_TEST_TOKEN}":
            return httpx.Response(401, json={"status_message": "Invalid API key"})
        path = request.url.path
        if match := re.fullmatch(r"/3/discover/(tv|movie)", path):
            pages = TMDB_TV_PAGES if match.group(1) == "tv" else TMDB_MOVIE_PAGES
            page = int(request.url.params.get("page", "1"))
            return httpx.Response(
                200,
                json={
                    "page": page,
                    "results": pages.get(page, []),
                    "total_pages": TMDB_TOTAL_PAGES,
                    "total_results": sum(len(p) for p in pages.values()),
                },
            )
        if match := re.fullmatch(r"/3/tv/(\d+)/external_ids", path):
            tmdb_id = int(match.group(1))
            if tmdb_id not in TMDB_TV_IMDB:
                return httpx.Response(404, json={"status_message": "not found"})
            return httpx.Response(200, json={"id": tmdb_id, "imdb_id": TMDB_TV_IMDB[tmdb_id]})
        if match := re.fullmatch(r"/3/movie/(\d+)", path):
            tmdb_id = int(match.group(1))
            if tmdb_id not in TMDB_MOVIE_IMDB:
                return httpx.Response(404, json={"status_message": "not found"})
            return httpx.Response(200, json={"id": tmdb_id, "imdb_id": TMDB_MOVIE_IMDB[tmdb_id]})
        return httpx.Response(404)

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
            self.b2_uploads += 1
            ts = 1_700_000_000_000 + self.b2_uploads * 1000  # strictly increasing, even after deletes
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
