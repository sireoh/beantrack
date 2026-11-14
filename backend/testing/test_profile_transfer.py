"""Watchlist export / import (/api/auth/profile/export and /import)."""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Movie, TvShow
from app.services import profile as profile_service
from testing.fakes import FakeUpstream, movie_add_payload, tv_add_payload


@pytest.fixture(autouse=True)
def _no_retry_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(profile_service, "UPSTREAM_RETRY_DELAY_SECONDS", 0.0)


def _set_progress(client: TestClient, imdb: str, index: int, episode_id: int) -> None:
    response = client.patch(
        f"/api/tvlist/{imdb}/progress",
        json={
            "set_to": index,
            "current_episode_metadata": {
                "id": episode_id,
                "season": 1,
                "number": index + 1,
                "title": "x",
                "image": None,
            },
        },
    )
    assert response.status_code == 200, response.text


def _import(client: TestClient, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/api/auth/profile/import", json=payload)
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()
    return body


def test_export_contains_only_list_data(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload(status="watching"))
    _set_progress(alice, "tt0903747", 1, 12193)
    alice.post("/api/movielist/add", json=movie_add_payload(status="completed"))

    body = alice.get("/api/auth/profile/export").json()

    assert body["format"] == "beantrack-export" and body["version"] == 1
    (tv,) = body["tvlist"]
    assert tv["imdb"] == "tt0903747" and tv["tvmaze_id"] == 169
    assert (tv["status"], tv["current_episode"], tv["current_episode_id"]) == (
        "completed",  # episode index 1 is the fixture's last, so progress completed the show
        1,
        12193,
    )
    assert tv["added_at"] and tv["updated_at"]
    (movie,) = body["movielist"]
    assert (movie["imdb"], movie["status"]) == ("tt0133093", "completed")
    # No catalog metadata.
    for entry in (tv, movie):
        assert not {"title", "image", "score", "current_episode_metadata"} & entry.keys()


def test_export_then_import_into_another_account(alice: TestClient, bob: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload(status="watching"))
    _set_progress(alice, "tt0903747", 1, 12193)
    alice.post("/api/movielist/add", json=movie_add_payload(status="dropped"))
    exported = alice.get("/api/auth/profile/export").json()

    result = _import(bob, exported)

    assert result == {"imported": 2, "skipped": 0, "failed": 0, "failures": []}
    (tv,) = bob.get("/api/tvlist").json()["entries"]
    assert tv["status"] == "completed" and tv["current_episode"] == 1  # last episode
    assert tv["current_episode_metadata"]["id"] == 12193
    assert tv["added_at"] == alice.get("/api/tvlist").json()["entries"][0]["added_at"]
    (movie,) = bob.get("/api/movielist").json()["entries"]
    assert movie["status"] == "dropped"


def test_import_fetches_missing_catalog_data(
    alice: TestClient, upstream: FakeUpstream, db: Session
) -> None:
    payload: dict[str, Any] = {
        "tvlist": [
            {"imdb": "tt0306414", "tvmaze_id": 179, "status": "planned"},  # by TVmaze id
            {"imdb": "tt0903747", "status": "completed", "current_episode": 1},  # IMDb lookup
        ],
        "movielist": [{"imdb": "tt0816692", "status": "planned"}],
    }

    result = _import(alice, payload)

    assert result["imported"] == 3, result
    assert upstream.count("api.tvmaze.com", "/lookup/shows") == 1
    assert upstream.count("www.omdbapi.com") == 1
    assert db.scalar(select(func.count()).select_from(TvShow)) == 2
    assert db.get(Movie, "tt0816692") is not None
    shows = {e["show"]["imdb"]: e for e in alice.get("/api/tvlist").json()["entries"]}
    assert shows["tt0306414"]["show"]["episodes_count"] == 1
    assert shows["tt0903747"]["current_episode"] == 1


def test_import_skips_existing_and_reports_failures(alice: TestClient) -> None:
    alice.post("/api/movielist/add", json=movie_add_payload())
    payload = {
        "tvlist": [{"imdb": "not-an-id"}, {"imdb": "tt9999999", "status": "planned"}],
        "movielist": [
            {"imdb": "tt0133093", "status": "planned"},  # already there
            {"imdb": "tt0816692", "status": "binging"},  # bad status
            {"imdb": "tt0816692", "status": "planned"},
        ],
    }

    result = _import(alice, payload)

    assert (result["imported"], result["skipped"], result["failed"]) == (1, 1, 3)
    failed = {(f["kind"], f["imdb"]) for f in result["failures"]}
    assert failed == {("tv", "not-an-id"), ("tv", "tt9999999"), ("movie", "tt0816692")}
    assert len(alice.get("/api/movielist").json()["entries"]) == 2


def test_import_upstream_outage_fails_only_affected_entries(
    alice: TestClient, upstream: FakeUpstream
) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload())  # Breaking Bad is now cached
    exported = alice.get("/api/auth/profile/export").json()
    alice.delete("/api/tvlist/tt0903747")
    upstream.fail_hosts.update({"www.omdbapi.com", "api.tvmaze.com"})
    payload = {**exported, "movielist": [{"imdb": "tt0816692", "status": "planned"}]}

    result = _import(alice, payload)

    assert (result["imported"], result["failed"]) == (1, 1)
    assert result["failures"][0]["kind"] == "movie"
    assert "OMDb" in result["failures"][0]["reason"]


def test_profile_routes_require_login(client: TestClient) -> None:
    assert client.get("/api/auth/profile/export").status_code == 401
    assert client.post("/api/auth/profile/import", json={}).status_code == 401
