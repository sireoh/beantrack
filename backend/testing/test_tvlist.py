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


def test_get_show_episodes_by_imdb(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload())

    response = alice.get("/api/tvlist/tt0903747/episodes")

    assert response.status_code == 200
    assert response.json()[0] == {
        "id": 12192,
        "season": 1,
        "number": 1,
        "title": "Pilot",
        "image": "https://static.tvmaze.com/e1-o.jpg",
    }


def test_update_progress_sets_and_clamps_metadata(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload())

    response = alice.patch(
        "/api/tvlist/tt0903747/progress",
        json={
            "set_to": 100,
            "current_episode_metadata": {
                "id": 1874762,
                "season": 1,
                "number": 1,
                "title": "Pilot",
                "image": "https://static.tvmaze.com/uploads/images/original_untouched/342/856397.jpg",
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["current_episode"] == 1
    assert response.json()["current_episode_metadata"]["id"] == 1874762


def test_update_progress_applies_delta_and_clamps_to_zero(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload(current_episode=1))

    response = alice.patch(
        "/api/tvlist/tt0903747/progress",
        json={
            "delta": -1000,
            "current_episode_metadata": {
                "id": 1874762,
                "season": 1,
                "number": 1,
                "title": "Pilot",
                "image": None,
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["current_episode"] == 0


def test_update_progress_requires_exactly_one_operation_and_metadata(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload())

    both = alice.patch(
        "/api/tvlist/tt0903747/progress",
        json={"set_to": 1, "delta": 1, "current_episode_metadata": tv_add_payload()["show"]},
    )
    neither = alice.patch(
        "/api/tvlist/tt0903747/progress",
        json={"current_episode_metadata": tv_add_payload()["show"]},
    )
    missing_metadata = alice.patch(
        "/api/tvlist/tt0903747/progress", json={"set_to": 1}
    )

    assert both.status_code == 422
    assert neither.status_code == 422
    assert missing_metadata.status_code == 422


def test_get_missing_show_episodes_is_404(alice: TestClient) -> None:
    response = alice.get("/api/tvlist/tt9999999/episodes")

    assert response.status_code == 404


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


def test_update_status(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload())

    response = alice.patch("/api/tvlist/tt0903747/status", json={"status": "dropped"})

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "dropped"
    assert alice.get("/api/tvlist").json()["entries"][0]["status"] == "dropped"


def test_update_status_validates_and_requires_entry(alice: TestClient) -> None:
    assert (
        alice.patch("/api/tvlist/tt0903747/status", json={"status": "watching"}).status_code
        == 404
    )
    alice.post("/api/tvlist/add", json=tv_add_payload())
    assert (
        alice.patch("/api/tvlist/tt0903747/status", json={"status": "binging"}).status_code
        == 422
    )


def test_cors_allows_frontend_origin_with_credentials(alice: TestClient) -> None:
    response = alice.options(
        "/api/tvlist/tt0903747/status",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "PATCH",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    assert response.headers["access-control-allow-credentials"] == "true"


def test_completing_a_show_moves_progress_to_last_episode(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload(status="watching"))

    entry = alice.patch("/api/tvlist/tt0903747/status", json={"status": "completed"}).json()

    assert entry["current_episode"] == 1  # the Breaking Bad fixture has 2 episodes
    assert entry["current_episode_metadata"]["id"] == 12193


def test_adding_a_completed_show_starts_at_last_episode(alice: TestClient) -> None:
    entry = alice.post("/api/tvlist/add", json=tv_add_payload(status="completed")).json()

    assert entry["current_episode"] == 1
    assert entry["current_episode_metadata"]["id"] == 12193


def _episode(episode_id: int, number: int) -> dict[str, object]:
    return {"id": episode_id, "season": 1, "number": number, "title": "x", "image": None}


def _step(client: TestClient, delta: int, episode_id: int, number: int) -> dict[str, object]:
    response = client.patch(
        "/api/tvlist/tt0903747/progress",
        json={"delta": delta, "current_episode_metadata": _episode(episode_id, number)},
    )
    assert response.status_code == 200, response.text
    body: dict[str, object] = response.json()
    return body


def _jump(client: TestClient, index: int) -> dict[str, object]:
    episode_id, number = (12192, 1) if index == 0 else (12193, 2)
    response = client.patch(
        "/api/tvlist/tt0903747/progress",
        json={"set_to": index, "current_episode_metadata": _episode(episode_id, number)},
    )
    assert response.status_code == 200, response.text
    body: dict[str, object] = response.json()
    return body


# Breaking Bad fixture: 2 episodes, so index 1 is the last one.


def test_increment_to_last_episode_completes_the_show(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload(status="watching"))

    entry = _step(alice, 1, 12193, 2)

    assert (entry["current_episode"], entry["status"]) == (1, "completed")


def test_decrement_from_completed_last_episode_resumes_watching(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload(status="completed"))  # sits on last ep

    entry = _step(alice, -1, 12192, 1)

    assert (entry["current_episode"], entry["status"]) == (0, "watching")


def test_picking_last_episode_completes_even_planned_or_dropped(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload(status="dropped"))

    entry = _jump(alice, 1)

    assert entry["status"] == "completed"


def test_picking_earlier_episode_of_completed_show_resumes_watching(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload(status="completed"))

    entry = _jump(alice, 0)

    assert (entry["current_episode"], entry["status"]) == (0, "watching")


def test_progress_before_last_episode_keeps_planned(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload(status="planned"))

    assert _jump(alice, 0)["status"] == "planned"


def test_progress_before_last_episode_keeps_dropped(alice: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload(status="dropped"))

    assert _jump(alice, 0)["status"] == "dropped"
