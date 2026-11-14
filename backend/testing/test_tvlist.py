from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Episode, TvShow
from testing.fakes import FakeUpstream, tv_add_payload


def test_get_tvlist_starts_empty(alice: TestClient) -> None:
    response = alice.get("/api/tvlist")

    assert response.status_code == 200
    body = response.json()
    assert body["entries"] == []
    assert isinstance(body["tvlist_id"], str) and len(body["tvlist_id"]) == 36  # uuid4


def test_add_show_fetches_and_caches_episodes(
    alice: TestClient, db: Session
) -> None:
    response = alice.post("/api/tvlist/add", json=tv_add_payload(status="watching"))

    assert response.status_code == 201, response.text
    entry = response.json()
    assert entry["status"] == "watching"
    assert entry["current_episode"] == 0
    assert entry["show"] == {
        "imdb": "tt0903747",
        "title": "Breaking Bad",
        "image": "https://static.tvmaze.com/bb-original.jpg",
        "score": 9.2,
        "episodes_count": 2,
    }

    show = db.get(TvShow, "tt0903747")
    assert show is not None and show.tvmaze_id == 169
    episodes = db.scalars(select(Episode).order_by(Episode.id)).all()
    assert [(e.id, e.imdb, e.season, e.number, e.title) for e in episodes] == [
        (12192, "tt0903747", 1, 1, "Pilot"),
        (12193, "tt0903747", 1, 2, "Cat's in the Bag..."),
    ]


def test_get_tvlist_returns_added_shows(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload(current_episode=1))
    alice.post("/api/tvlist/add", json=tv_add_payload("tt0306414", status="completed"))

    body = alice.get("/api/tvlist").json()

    assert [e["show"]["title"] for e in body["entries"]] == ["Breaking Bad", "The Wire"]
    first, second = body["entries"]
    assert first["status"] == "planned"  # default
    assert first["current_episode"] == 1
    assert second["status"] == "completed"


def test_add_show_rejects_negative_episode_index(alice: TestClient) -> None:
    response = alice.post("/api/tvlist/add", json=tv_add_payload(current_episode=-1))

    assert response.status_code == 422


def test_add_same_show_twice_is_conflict(alice: TestClient) -> None:
    assert alice.post("/api/tvlist/add", json=tv_add_payload()).status_code == 201

    response = alice.post("/api/tvlist/add", json=tv_add_payload())

    assert response.status_code == 409


def test_delete_show_removes_only_the_user_entry(alice: TestClient, bob: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload())
    bob.post("/api/tvlist/add", json=tv_add_payload())

    response = alice.delete("/api/tvlist/tt0903747")

    assert response.status_code == 204
    assert alice.get("/api/tvlist").json()["entries"] == []
    assert len(bob.get("/api/tvlist").json()["entries"]) == 1


def test_delete_missing_show_is_404(alice: TestClient) -> None:
    response = alice.delete("/api/tvlist/tt0903747")

    assert response.status_code == 404


def test_add_show_uses_payload_without_upstream_lookup(alice: TestClient) -> None:
    payload = tv_add_payload()
    payload["show"]["imdb"] = "tt9999999"

    response = alice.post("/api/tvlist/add", json=payload)

    assert response.status_code == 201
    assert response.json()["show"]["imdb"] == "tt9999999"


def test_add_show_validates_body(alice: TestClient) -> None:
    invalid = tv_add_payload()
    invalid["show"]["imdb"] = "breaking-bad"
    assert alice.post("/api/tvlist/add", json=invalid).status_code == 422
    assert (
        alice.post("/api/tvlist/add", json=tv_add_payload(status="binging")).status_code
        == 422
    )
    assert (
        alice.post("/api/tvlist/add", json={**tv_add_payload(), "extra": 1}).status_code == 422
    )


def test_show_data_is_fetched_once_and_shared(
    alice: TestClient, bob: TestClient, upstream: FakeUpstream, db: Session
) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload())
    bob.post("/api/tvlist/add", json=tv_add_payload())

    assert upstream.count("api.tvmaze.com", "/lookup/shows") == 0
    assert db.scalar(select(func.count()).select_from(TvShow)) == 1


def test_add_show_fails_when_episode_fetch_fails(alice: TestClient, upstream: FakeUpstream) -> None:
    upstream.fail_hosts.add("api.tvmaze.com")

    response = alice.post("/api/tvlist/add", json=tv_add_payload())

    assert response.status_code == 502
    assert alice.get("/api/tvlist").json()["entries"] == []
