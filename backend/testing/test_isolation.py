from fastapi.testclient import TestClient

from testing.fakes import movie_add_payload, tv_add_payload


def test_users_have_separate_lists(alice: TestClient, bob: TestClient) -> None:
    alice_tv = alice.get("/api/tvlist").json()["tvlist_id"]
    bob_tv = bob.get("/api/tvlist").json()["tvlist_id"]
    alice_movies = alice.get("/api/movielist").json()["movielist_id"]
    bob_movies = bob.get("/api/movielist").json()["movielist_id"]

    assert alice_tv != bob_tv
    assert alice_movies != bob_movies


def test_tv_entries_are_isolated(alice: TestClient, bob: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload(status="watching"))
    bob.post("/api/tvlist/add", json=tv_add_payload("tt0306414"))

    alice_titles = [e["show"]["imdb"] for e in alice.get("/api/tvlist").json()["entries"]]
    bob_titles = [e["show"]["imdb"] for e in bob.get("/api/tvlist").json()["entries"]]

    assert alice_titles == ["tt0903747"]
    assert bob_titles == ["tt0306414"]


def test_same_show_tracked_independently(alice: TestClient, bob: TestClient) -> None:
    alice.post("/api/tvlist/add", json=tv_add_payload(status="completed"))

    # Bob can add the show Alice already has (no 409 leaking across users)...
    response = bob.post(
        "/api/tvlist/add", json=tv_add_payload(status="watching", current_episode=1)
    )
    assert response.status_code == 201

    # ...and each keeps their own progress.
    alice_entry = alice.get("/api/tvlist").json()["entries"][0]
    bob_entry = bob.get("/api/tvlist").json()["entries"][0]
    assert (alice_entry["status"], alice_entry["current_episode"]) == ("completed", 0)
    assert (bob_entry["status"], bob_entry["current_episode"]) == ("watching", 1)


def test_movie_entries_are_isolated(alice: TestClient, bob: TestClient) -> None:
    alice.post("/api/movielist/add", json=movie_add_payload())

    assert bob.get("/api/movielist").json()["entries"] == []
    assert bob.post("/api/movielist/add", json=movie_add_payload()).status_code == 201
    assert len(alice.get("/api/movielist").json()["entries"]) == 1
