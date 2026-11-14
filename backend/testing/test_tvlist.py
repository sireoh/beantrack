from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Episode, TvShow
from testing.fakes import FakeUpstream


def test_get_tvlist_starts_empty(alice: TestClient) -> None:
    response = alice.get("/api/tvlist")

    assert response.status_code == 200
    body = response.json()
    assert body["entries"] == []
    assert isinstance(body["tvlist_id"], str) and len(body["tvlist_id"]) == 36  # uuid4


def test_add_show_returns_entry_and_caches_show_and_episodes(
    alice: TestClient, db: Session
) -> None:
    response = alice.post("/api/tvlist/add", json={"imdb": "tt0903747", "status": "watching"})

    assert response.status_code == 201, response.text
    entry = response.json()
    assert entry["status"] == "watching"
    assert entry["current_episode"] is None
    assert entry["show"] == {
        "imdb": "tt0903747",
        "title": "Breaking Bad",
        "image": "https://static.tvmaze.com/bb-original.jpg",
        "score": 9.2,
    }

    show = db.get(TvShow, "tt0903747")
    assert show is not None and show.tvmaze_id == 169
    episodes = db.scalars(select(Episode).order_by(Episode.id)).all()
    assert [(e.id, e.season, e.number, e.title) for e in episodes] == [
        (12192, 1, 1, "Pilot"),
        (12193, 1, 2, "Cat's in the Bag..."),
    ]
    assert episodes[0].image == "https://static.tvmaze.com/e1-o.jpg"


def test_get_tvlist_returns_added_shows(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json={"imdb": "tt0903747", "current_episode": 12193})
    alice.post("/api/tvlist/add", json={"imdb": "tt0306414", "status": "completed"})

    body = alice.get("/api/tvlist").json()

    assert [e["show"]["title"] for e in body["entries"]] == ["Breaking Bad", "The Wire"]
    first, second = body["entries"]
    assert first["status"] == "planned"  # default
    assert first["current_episode"]["id"] == 12193
    assert first["current_episode"]["season"] == 1 and first["current_episode"]["number"] == 2
    assert second["status"] == "completed"


def test_add_show_rejects_episode_from_another_show(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json={"imdb": "tt0306414"})  # The Wire, episode 15000

    response = alice.post(
        "/api/tvlist/add", json={"imdb": "tt0903747", "current_episode": 15000}
    )

    assert response.status_code == 422
    assert alice.get("/api/tvlist").json()["entries"][0]["show"]["imdb"] == "tt0306414"
    assert len(alice.get("/api/tvlist").json()["entries"]) == 1


def test_add_same_show_twice_is_conflict(alice: TestClient) -> None:
    assert alice.post("/api/tvlist/add", json={"imdb": "tt0903747"}).status_code == 201

    response = alice.post("/api/tvlist/add", json={"imdb": "tt0903747"})

    assert response.status_code == 409


def test_add_unknown_show_is_404(alice: TestClient) -> None:
    response = alice.post("/api/tvlist/add", json={"imdb": "tt9999999"})

    assert response.status_code == 404


def test_add_show_validates_body(alice: TestClient) -> None:
    assert alice.post("/api/tvlist/add", json={"imdb": "breaking-bad"}).status_code == 422
    assert (
        alice.post("/api/tvlist/add", json={"imdb": "tt0903747", "status": "binging"}).status_code
        == 422
    )
    assert (
        alice.post("/api/tvlist/add", json={"imdb": "tt0903747", "extra": 1}).status_code == 422
    )


def test_show_data_is_fetched_once_and_shared(
    alice: TestClient, bob: TestClient, upstream: FakeUpstream, db: Session
) -> None:
    alice.post("/api/tvlist/add", json={"imdb": "tt0903747"})
    bob.post("/api/tvlist/add", json={"imdb": "tt0903747"})

    assert upstream.count("api.tvmaze.com", "/lookup/shows") == 1
    assert db.scalar(select(func.count()).select_from(TvShow)) == 1


def test_tvmaze_outage_is_502(alice: TestClient, upstream: FakeUpstream) -> None:
    upstream.fail_hosts.add("api.tvmaze.com")

    response = alice.post("/api/tvlist/add", json={"imdb": "tt0903747"})

    assert response.status_code == 502
