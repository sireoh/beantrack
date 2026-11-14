from fastapi.testclient import TestClient


def test_users_have_separate_lists(alice: TestClient, bob: TestClient) -> None:
    alice_tv = alice.get("/api/tvlist").json()["tvlist_id"]
    bob_tv = bob.get("/api/tvlist").json()["tvlist_id"]
    alice_movies = alice.get("/api/movielist").json()["movielist_id"]
    bob_movies = bob.get("/api/movielist").json()["movielist_id"]

    assert alice_tv != bob_tv
    assert alice_movies != bob_movies


def test_tv_entries_are_isolated(alice: TestClient, bob: TestClient) -> None:
    alice.post("/api/tvlist/add", json={"imdb": "tt0903747", "status": "watching"})
    bob.post("/api/tvlist/add", json={"imdb": "tt0306414"})

    alice_titles = [e["show"]["imdb"] for e in alice.get("/api/tvlist").json()["entries"]]
    bob_titles = [e["show"]["imdb"] for e in bob.get("/api/tvlist").json()["entries"]]

    assert alice_titles == ["tt0903747"]
    assert bob_titles == ["tt0306414"]


def test_same_show_tracked_independently(alice: TestClient, bob: TestClient) -> None:
    alice.post("/api/tvlist/add", json={"imdb": "tt0903747", "status": "completed"})

    # Bob can add the show Alice already has (no 409 leaking across users)...
    response = bob.post(
        "/api/tvlist/add", json={"imdb": "tt0903747", "status": "watching", "current_episode": 12192}
    )
    assert response.status_code == 201

    # ...and each keeps their own progress.
    alice_entry = alice.get("/api/tvlist").json()["entries"][0]
    bob_entry = bob.get("/api/tvlist").json()["entries"][0]
    assert (alice_entry["status"], alice_entry["current_episode"]) == ("completed", None)
    assert (bob_entry["status"], bob_entry["current_episode"]["id"]) == ("watching", 12192)


def test_movie_entries_are_isolated(alice: TestClient, bob: TestClient) -> None:
    alice.post("/api/movielist/add", json={"imdb": "tt0133093"})

    assert bob.get("/api/movielist").json()["entries"] == []
    assert bob.post("/api/movielist/add", json={"imdb": "tt0133093"}).status_code == 201
    assert len(alice.get("/api/movielist").json()["entries"]) == 1
