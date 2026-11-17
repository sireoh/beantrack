"""Discover: TMDB pages cached in SQLite, adding titles via TMDB -> TVmaze / OMDb."""

from datetime import timedelta

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from pydantic import SecretStr
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.base import Base
from app.db.types import utcnow
from app.main import create_app
from app.models import DiscoverCacheMovie, DiscoverCacheTv
from testing.fakes import TMDB_TOTAL_PAGES, FakeUpstream, tv_add_payload

TMDB = "api.themoviedb.org"


def _tmdb_discover_calls(upstream: FakeUpstream) -> int:
    return upstream.count(TMDB, "/3/discover")


# --- browsing ------------------------------------------------------------------------


def test_discover_tv_is_public_and_maps_tmdb_fields(client: TestClient) -> None:
    response = client.get("/api/discover/tv?page=1")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["type"] == "tv" and body["page"] == 1
    assert body["total_pages"] == TMDB_TOTAL_PAGES
    first, no_votes = body["results"][0], body["results"][1]
    assert first == {
        "tmdb_id": 1396,
        "title": "Breaking Bad",
        "date": "2008-01-20",
        "score": 8.912,
        "poster_path": "/bb.jpg",
        "genre_ids": [18, 80],
        "imdb": None,
    }
    # No votes -> no score; empty date / poster -> None.
    assert no_votes["score"] is None and no_votes["date"] is None and no_votes["poster_path"] is None


def test_discover_movies_uses_title_and_release_date(client: TestClient) -> None:
    body = client.get("/api/discover/movies").json()  # page defaults to 1

    assert body["type"] == "movie" and body["page"] == 1
    assert body["results"][0]["title"] == "The Matrix"
    assert body["results"][0]["date"] == "1999-03-31"


def test_pages_are_served_from_the_cache_while_fresh(
    client: TestClient, upstream: FakeUpstream
) -> None:
    client.get("/api/discover/tv?page=1")
    client.get("/api/discover/tv?page=1")
    assert _tmdb_discover_calls(upstream) == 1

    client.get("/api/discover/tv?page=2")
    assert _tmdb_discover_calls(upstream) == 2


def test_expired_pages_are_fetched_again(
    client: TestClient, upstream: FakeUpstream, db: Session
) -> None:
    client.get("/api/discover/movies?page=1")
    row = db.get(DiscoverCacheMovie, 1)
    assert row is not None
    row.fetched_at = utcnow() - timedelta(hours=25)
    db.commit()

    client.get("/api/discover/movies?page=1")

    assert _tmdb_discover_calls(upstream) == 2
    db.expire_all()
    refreshed = db.get(DiscoverCacheMovie, 1)
    assert refreshed is not None and utcnow() - refreshed.fetched_at < timedelta(minutes=1)


def test_expired_page_is_served_when_tmdb_is_down(
    client: TestClient, upstream: FakeUpstream, db: Session
) -> None:
    client.get("/api/discover/tv?page=1")
    row = db.get(DiscoverCacheTv, 1)
    assert row is not None
    row.fetched_at = utcnow() - timedelta(days=3)
    db.commit()
    upstream.fail_hosts.add(TMDB)

    response = client.get("/api/discover/tv?page=1")

    assert response.status_code == 200
    assert response.json()["results"][0]["title"] == "Breaking Bad"


def test_uncached_page_with_tmdb_down_is_502(client: TestClient, upstream: FakeUpstream) -> None:
    upstream.fail_hosts.add(TMDB)
    assert client.get("/api/discover/tv?page=1").status_code == 502


@pytest.mark.parametrize("page", ["0", "501", "x"])
def test_page_must_be_between_1_and_500(client: TestClient, page: str) -> None:
    assert client.get(f"/api/discover/tv?page={page}").status_code == 422


def test_discover_without_tmdb_token_is_a_clear_error(
    settings: Settings, upstream: FakeUpstream
) -> None:
    unconfigured = settings.model_copy(update={"tmdb_bearer_token": SecretStr("")})
    app = create_app(unconfigured, http_client=httpx.Client(transport=upstream.transport()))
    Base.metadata.create_all(app.state.engine)
    with TestClient(app) as client:
        response = client.get("/api/discover/tv")
    assert response.status_code == 400
    assert "TMDB_BEARER_TOKEN" in response.json()["detail"]


# --- adding ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", ["/api/discover/tv/add", "/api/discover/movies/add"])
def test_add_requires_login(client: TestClient, path: str) -> None:
    assert client.post(path, json={"tmdb_id": 1396}).status_code == 401


def test_add_tv_matches_a_search_add(alice: TestClient, bob: TestClient) -> None:
    via_discover = alice.post(
        "/api/discover/tv/add", json={"tmdb_id": 1396, "status": "watching"}
    )
    via_search = bob.post("/api/tvlist/add", json=tv_add_payload(status="watching"))

    assert via_discover.status_code == 201, via_discover.text
    a, b = via_discover.json(), via_search.json()
    for entry in (a, b):
        entry.pop("added_at"), entry.pop("updated_at")
    assert a == b
    assert a["show"]["title"] == "Breaking Bad" and a["show"]["episodes_count"] == 2
    assert alice.get("/api/tvlist/tt0903747/episodes").status_code == 200


def test_added_titles_are_marked_with_their_imdb_id(alice: TestClient) -> None:
    alice.get("/api/discover/tv?page=1")  # cached before the add
    alice.post("/api/discover/tv/add", json={"tmdb_id": 1396})

    results = alice.get("/api/discover/tv?page=1").json()["results"]

    assert results[0]["imdb"] == "tt0903747"
    assert results[1]["imdb"] is None


def test_title_added_from_search_is_marked_after_a_duplicate_discover_add(
    alice: TestClient,
) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload())

    duplicate = alice.post("/api/discover/tv/add", json={"tmdb_id": 1396})

    assert duplicate.status_code == 409
    assert alice.get("/api/discover/tv").json()["results"][0]["imdb"] == "tt0903747"


def test_add_tv_without_imdb_id_adds_nothing(alice: TestClient) -> None:
    response = alice.post("/api/discover/tv/add", json={"tmdb_id": 5000})

    assert response.status_code == 404
    assert "Couldn't find this title on TVmaze" in response.json()["detail"]
    assert alice.get("/api/tvlist").json()["entries"] == []


def test_add_tv_unknown_to_tvmaze_adds_nothing(alice: TestClient) -> None:
    response = alice.post("/api/discover/tv/add", json={"tmdb_id": 6000})

    assert response.status_code == 404
    assert response.json()["detail"] == "Couldn't find this title on TVmaze"
    assert alice.get("/api/tvlist").json()["entries"] == []


def test_add_movie_uses_one_omdb_call(alice: TestClient, upstream: FakeUpstream) -> None:
    response = alice.post("/api/discover/movies/add", json={"tmdb_id": 603, "status": "completed"})

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "completed"
    assert body["movie"] == {
        "imdb": "tt0133093",
        "title": "The Matrix",
        "image": "https://m.media-amazon.com/matrix.jpg",
        "score": 8.7,
    }
    assert upstream.count("www.omdbapi.com") == 1


def test_add_movie_unknown_to_omdb_adds_nothing(alice: TestClient) -> None:
    response = alice.post("/api/discover/movies/add", json={"tmdb_id": 8000})

    assert response.status_code == 404
    assert response.json()["detail"] == "Couldn't find this title on OMDb"
    assert alice.get("/api/movielist").json()["entries"] == []


def test_add_movie_without_imdb_id_or_unknown_tmdb_id(alice: TestClient) -> None:
    assert alice.post("/api/discover/movies/add", json={"tmdb_id": 7000}).status_code == 404
    assert alice.post("/api/discover/movies/add", json={"tmdb_id": 424242}).status_code == 404


def test_duplicate_movie_add_is_409(alice: TestClient) -> None:
    alice.post("/api/discover/movies/add", json={"tmdb_id": 603})
    assert alice.post("/api/discover/movies/add", json={"tmdb_id": 603}).status_code == 409


# --- admin: clear the cache ------------------------------------------------------------


def test_clear_discover_cache_is_admin_only(alice: TestClient, client: TestClient) -> None:
    assert alice.delete("/api/admin/discover-cache").status_code == 403
    assert client.delete("/api/admin/discover-cache").status_code == 401


def test_admin_clears_both_cache_tables(
    admin: TestClient, upstream: FakeUpstream, db: Session, app: FastAPI
) -> None:
    admin.get("/api/discover/tv?page=1")
    admin.get("/api/discover/movies?page=1")

    response = admin.delete("/api/admin/discover-cache")

    assert response.status_code == 204
    assert db.scalar(select(func.count()).select_from(DiscoverCacheTv)) == 0
    assert db.scalar(select(func.count()).select_from(DiscoverCacheMovie)) == 0
    admin.get("/api/discover/tv?page=1")
    assert _tmdb_discover_calls(upstream) == 3
